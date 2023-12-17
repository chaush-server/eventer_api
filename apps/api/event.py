import datetime

from flask import request, jsonify, abort
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser
from sqlalchemy import func
from apps.api.category import category_response_model
from apps.api.city import city_response_model
from apps.models import Event, Organizer, ValidateStatusEnum, StatusEnum, EventDates, Country, Venue, State, \
    City, Genre, Feedback, Booking
from extensions import db

PER_PAGE = 15

namespace = Namespace(name='event', description='Events operations')

event_req_parser = RequestParser(bundle_errors=True)
event_req_parser.add_argument(name="page", type=int)
event_req_parser.add_argument(name="name", type=str, nullable=False, location="args")
event_req_parser.add_argument(name="organizerId", type=int, nullable=False, location="args")

event_dates_expect_model = namespace.model('EventDates event_expect', {
    'id': fields.Integer(readonly=True),
    'startDateTime': fields.DateTime(required=True),
    'endDateTime': fields.DateTime(required=True),
})

venue_dates_expect_model = namespace.model('Venue event_expect', {
    'name': fields.String(required=True),
    'description': fields.String(),
    'photos': fields.List(fields.String()),
    'address': fields.String(),
    'seats': fields.Integer(),
    'country': fields.String(),
    'state': fields.String(),
    'city': fields.String(),
})

event_expect_model = namespace.model('Event', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(),
    'description': fields.String(),
    'expectedAmount': fields.Float(),
    'recommendedDonation': fields.Float(),
    'validateStatus': fields.String(enum=[enum.value for enum in ValidateStatusEnum]),
    'countOfMembers': fields.Integer(),
    'status': fields.String(enum=[enum.value for enum in StatusEnum]),
    'concession': fields.String(),
    'genreId': fields.Integer(),
    'organizerId': fields.Integer(),
    'eventDateTimes': fields.List(fields.Nested(event_dates_expect_model)),
    'venues': fields.List(fields.Nested(venue_dates_expect_model)),
})

event_venues_response_model = namespace.model('Venue event_response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'description': fields.String(),
    'photos': fields.List(fields.String()),
    'seats': fields.Integer(),
    'address': fields.String(),
    'city': fields.Nested(city_response_model),
})

event_organizer_response_model = namespace.model('Organizer event_response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'logo': fields.String(),
})

event_response_model = namespace.model('Event response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'description': fields.String(),
    'expectedAmount': fields.Float(),
    'recommendedDonation': fields.Float(),
    'validateStatus': fields.String(),
    'countOfMembers': fields.Integer(),
    'status': fields.String(),
    'concession': fields.String(),
    'genre': fields.Nested(category_response_model),
    'organizer': fields.Nested(event_organizer_response_model),
    'eventDates': fields.List(fields.Nested(event_dates_expect_model)),
    'venues': fields.List(fields.Nested(event_venues_response_model)),
    'number': fields.Integer(attribute=lambda event: Booking.query.filter_by(eventId=event.id).count())
})


@namespace.route('/')
# @namespace.doc(security='Bearer', )
class EventList(Resource):
    @namespace.marshal_list_with(event_response_model)
    @namespace.expect(event_req_parser)
    # @jwt_required()
    def get(self) -> list[Event]:
        query = Event.query.filter_by(status='ACTIVE')

        name = request.args.get('name')
        organizer_id = request.args.get('organizerId')
        page = request.args.get('page')

        if name:
            query = query.filter(Event.name.ilike(f'%{name}%'))
        if organizer_id:
            query = query.filter_by(organizerId=int(organizer_id))
        if page:
            query = query.paginate(page=int(page), per_page=PER_PAGE)

        events = query.items if page else query.all()

        return events

    @staticmethod
    def is_valid_dates(dates):
        try:
            if dates:
                for i in dates:
                    if len(i) != 2:
                        print('Incorrect amount of datetimes')
                        return False
            else:
                return False
        except Exception as e:
            print(e, 'Data in eventDateTimes is not valid')
            return False
        return True

    @namespace.expect(event_expect_model)
    @namespace.marshal_with(event_response_model, code=201)
    @jwt_required()
    def post(self) -> tuple[Event, int] or jsonify:
        # Получаем данные из запроса
        data = namespace.payload
        # Извлекаем данные о датах и местах проведения мероприятия
        date_times_data = data.pop('eventDateTimes')
        venues_data = data.pop('venues')
        # Проверяем, что категория и организатор существуют
        Genre.query.get_or_404(data['genreId'], 'Genre not found')
        Organizer.query.get_or_404(data['organizerId'], 'Organizer not found')
        # Создаем новое мероприятие
        new_event = Event(**data)
        db.session.add(new_event)
        db.session.flush()

        try:
            # Добавляем даты проведения мероприятия
            for date_time in date_times_data:
                dates = {
                    'startDateTime': datetime.datetime.fromisoformat(date_time['startDateTime']),
                    'endDateTime': datetime.datetime.fromisoformat(date_time['endDateTime']),
                    'eventId': new_event.id
                }
                new_dates = EventDates(**dates)
                db.session.add(new_dates)

            # Добавляем места проведения мероприятия
            for venue in venues_data:
                country_name = venue.pop('country')
                state_name = venue.pop('state')
                city_name = venue.pop('city')

                # Проверяем, существуют ли страна, регион и город
                country = Country.query.filter_by(name=country_name).first()
                if not country:
                    country = Country(name=country_name)
                    db.session.add(country)
                    db.session.flush()

                state = State.query.filter_by(name=state_name, countryId=country.id).first()
                if not state:
                    state = State(name=state_name, countryId=country.id)
                    db.session.add(state)
                    db.session.flush()

                city = City.query.filter_by(name=city_name, stateId=state.id).first()
                if not city:
                    city = City(name=city_name, stateId=state.id)
                    db.session.add(city)
                    db.session.flush()

                # Создаем новое место проведения мероприятия
                new_venue = Venue(
                    **venue,
                    countryId=country.id,
                    stateId=state.id,
                    cityId=city.id,
                    eventId=new_event.id
                )
                db.session.add(new_venue)
                db.session.flush()

        except Exception as e:
            # Если произошла ошибка, откатываем транзакцию
            db.session.rollback()
            abort(400, description=str(e))

        # Сохраняем изменения в базе данных
        db.session.commit()
        return new_event, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of an Event')
@namespace.doc(security='Bearer', )
class EventApi(Resource):
    @namespace.marshal_with(event_response_model)
    @jwt_required()
    def get(self, id):
        event = Event.query.get_or_404(id, 'Event not found')
        return event

    @namespace.expect(event_expect_model)
    @namespace.marshal_with(event_response_model)
    @jwt_required()
    def put(self, id):
        # Получаем событие, которое нужно обновить
        event = Event.query.get_or_404(id, 'Event not found')
        # Получаем данные из запроса
        data = request.get_json()
        if 'eventDateTimes' in data:
            # Удаляем все EventDates, связанные с событием
            event_dates_id = EventDates.query.filter_by(eventId=id).first().id
            event_dates = EventDates.query.get(event_dates_id)
            dates = data.pop('eventDateTimes')[0]
            if 'startDateTime' in dates:
                EventDates.startDateTime = dates['startDateTime']
            if 'endDateTime' in dates:
                EventDates.endDateTime = dates['endDateTime']
            db.session.flush()

        if 'venues' in data:
            venue_id = Venue.query.filter_by(eventId=id).first().id
            venue = Venue.query.get(venue_id)
            venues_data = data.pop('venues')
            for i in venues_data:
                if i.get('country'):
                    if not Country.query.filter_by(name=i['country']).first():
                        db.session.add(Country(name=i['country']))
                        db.session.flush()
                    country = Country.query.filter_by(name=i.pop('country')).first()
                    venue.country = country

                if i.get('state'):
                    if not State.query.filter_by(name=i['state']).first():
                        db.session.add(State(name=i['state'], countryId=venue.country.id))
                        db.session.flush()
                    state = State.query.filter_by(name=i.pop('state')).first()
                    venue.state = state

                if i.get('city'):
                    if not City.query.filter_by(name=i['city']).first():
                        db.session.add(City(name=i['city'], stateId=venue.state.id))
                        db.session.flush()
                    city = City.query.filter_by(name=i.pop('city')).first()
                    venue.city = city

                if i.get('photos'):
                    venue.photos = i.pop('photos')

                for field, value in i.items():
                    if value is not None and value not in ['photos', 'country', 'city', 'state']:
                        setattr(venue, field, value)
                db.session.flush()

        for field, value in data.items():
            if value is not None and value not in ['eventDateTimes', 'venues']:
                setattr(event, field, value)
        db.session.commit()

        return event, 201

    @namespace.response(204, 'Event deleted')
    @jwt_required()
    def delete(self, id):
        event = Event.query.get_or_404(id, 'Event not found')
        db.session.delete(event)
        db.session.commit()
        return '', 204


@namespace.route('/rate/<id>')
@namespace.doc(security='Bearer', )
class EventRate(Resource):
    @jwt_required()
    def get(self, id):
        average_rate = db.session.query(func.avg(Feedback.rate)).filter_by(eventId=id).scalar()
        return {"averageRate": float(average_rate)}
