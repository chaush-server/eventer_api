from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.api.city import city_response_model
from apps.api.country import country_response_model
from apps.api.event import event_response_model
from apps.api.state import state_response_model
from apps.models import Venue, Country, State, City, Event
from extensions import db

namespace = Namespace(name='venue', description='Venue operations')

venue_model = namespace.model('Venue', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'photos': fields.List(fields.String(), required=True),
    'address': fields.String(required=True),
    'seats': fields.Integer(),
    'countryId': fields.Integer(),
    'stateId': fields.Integer(),
    'cityId': fields.Integer(),
    'eventId': fields.Integer()
})

venue_response_model = namespace.model('Venue response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'description': fields.String(),
    'photos': fields.List(fields.String()),
    'address': fields.String(),
    'country': fields.Nested(country_response_model),
    'state': fields.Nested(state_response_model),
    'city': fields.Nested(city_response_model),
    'event': fields.Nested(event_response_model)
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class VenueList(Resource):
    @namespace.marshal_list_with(venue_response_model)
    @jwt_required()
    def get(self):
        venues = Venue.query.all()
        return venues

    @namespace.expect(venue_model)
    @namespace.marshal_with(venue_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload

        Country.query.get_or_404(data['countryId'], 'Country not found')
        State.query.get_or_404(data['stateId'], 'State not found')
        City.query.get_or_404(data['cityId'], 'City not found')
        Event.query.get_or_404(data['eventId'], 'Event not found')

        new_venue = Venue(**data)
        db.session.add(new_venue)
        db.session.commit()
        return new_venue, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Venue')
@namespace.doc(security='Bearer', )
class VenueApi(Resource):
    @namespace.marshal_with(venue_response_model)
    @jwt_required()
    def get(self, id):
        venue = Venue.query.get_or_404(id, 'Venue not found')
        return venue

    @namespace.expect(venue_model)
    @namespace.marshal_with(venue_response_model)
    @jwt_required()
    def put(self, id):
        venue = Venue.query.get_or_404(id, 'Venue not found')

        data = namespace.payload
        country_id = data.get('countryId')
        state_id = data.get('stateId')
        city_id = data.get('cityId')
        event_id = data.get('eventId')

        if country_id:
            Country.query.get_or_404(country_id, 'Country not found')
            venue.countryId = country_id

        if state_id:
            State.query.get_or_404(state_id, 'State not found')
            venue.stateId = state_id

        if city_id:
            City.query.get_or_404(city_id, 'City not found')
            venue.cityId = city_id

        if event_id:
            Event.query.get_or_404(event_id, 'Event not found')
            venue.eventId = event_id

        for key, value in data.items():
            if key not in ['countryId', 'stateId', 'cityId', 'eventId']:
                setattr(venue, key, value)

        db.session.commit()
        return venue

    @namespace.response(204, 'Venue deleted')
    @jwt_required()
    def delete(self, id):
        venue = Venue.query.get_or_404(id, 'Venue not found')
        db.session.delete(venue)
        db.session.commit()
        return '', 204
