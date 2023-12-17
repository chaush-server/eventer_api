from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.api.event import event_response_model
from apps.models import EventDates, Event
from extensions import db

namespace = Namespace(name='event_dates', description='Event Dates operations')

event_dates_model = namespace.model('Event Dates', {
    'id': fields.Integer(readonly=True),
    'startDateTime': fields.DateTime(required=True),
    'endDateTime': fields.DateTime(required=True),
    'eventId': fields.Integer(),
})

event_dates_response_model = namespace.model('Event Dates response', {
    'id': fields.Integer(),
    'startDateTime': fields.DateTime(),
    'endDateTime': fields.DateTime(),
    'event': fields.Nested(event_response_model)
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class EventDatesList(Resource):
    @namespace.marshal_list_with(event_dates_response_model)
    @jwt_required()
    def get(self):
        event_dates = EventDates.query.all()
        return event_dates

    @namespace.expect(event_dates_model)
    @namespace.marshal_with(event_dates_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        Event.query.get_or_404(data['eventId'], 'Event not found')
        new_event_dates = EventDates(**data)
        db.session.add(new_event_dates)
        db.session.commit()
        return new_event_dates, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of an Event Dates')
@namespace.doc(security='Bearer', )
class EventDatesApi(Resource):
    @namespace.marshal_with(event_dates_response_model)
    @jwt_required()
    def get(self, id):
        event_dates = EventDates.query.get_or_404(id, 'Event Dates not found')
        return event_dates

    @namespace.expect(event_dates_model)
    @namespace.marshal_with(event_dates_response_model)
    @jwt_required()
    @jwt_required()
    def put(self, id):
        event_dates = EventDates.query.get_or_404(id, 'Event Dates not found')

        data = namespace.payload
        event_id = data.get('eventId')

        if event_id:
            Event.query.get_or_404(event_id, 'Event not found')
            event_dates.eventId = event_id

        for key, value in data.items():
            if key != 'eventId':
                setattr(event_dates, key, value)

        db.session.commit()
        return event_dates

    @namespace.response(204, 'Event Dates deleted')
    @jwt_required()
    def delete(self, id):
        event_dates = EventDates.query.get_or_404(id, 'Event Dates not found')
        db.session.delete(event_dates)
        db.session.commit()
        return '', 204
