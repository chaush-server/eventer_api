from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask_restx.reqparse import RequestParser

from apps.api.event import event_response_model
from apps.api.user import user_response_model
from apps.models import EventDonation, User, Event
from extensions import db

namespace = Namespace(name='event_donation', description='Event Donation operations')

event_donation_model = namespace.model('Event Donation', {
    'id': fields.Integer(readonly=True),
    'dateTime': fields.DateTime(required=True),
    'amount': fields.Float(required=True),
    'comment': fields.String(),
    'userId': fields.Integer(),
    'eventId': fields.Integer(),
})

event_donation_response_model = namespace.model('Event Donation response', {
    'id': fields.Integer(),
    'dateTime': fields.DateTime(),
    'amount': fields.Float(),
    'comment': fields.String(),
    'user': fields.Nested(user_response_model),
    'event': fields.Nested(event_response_model)
})

event_req_parser = RequestParser(bundle_errors=True)
event_req_parser.add_argument(name="eventId", type=int, location="args")
event_req_parser.add_argument(name="userId", type=int, location="args")


@namespace.route('/')
@namespace.doc(security='Bearer', )
class EventDonationList(Resource):
    @namespace.marshal_list_with(event_donation_response_model)
    @namespace.expect(event_req_parser)
    @jwt_required()
    def get(self):
        query = EventDonation.query

        event_id = request.args.get('eventId')
        user_id = request.args.get('userId')

        if event_id:
            query = query.filter_by(eventId=int(event_id))
        if user_id:
            query = query.filter_by(userId=int(user_id))

        return query.all()

    @namespace.expect(event_donation_model)
    @namespace.marshal_with(event_donation_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        User.query.get_or_404(data['userId'], 'User not found')
        Event.query.get_or_404(data['eventId'], 'Event not found')
        new_event_donation = EventDonation(**data)
        db.session.add(new_event_donation)
        db.session.commit()
        return new_event_donation, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of an Event Donation')
@namespace.doc(security='Bearer', )
class EventDonationApi(Resource):
    @namespace.marshal_with(event_donation_response_model)
    @jwt_required()
    def get(self, id):
        event_donation = EventDonation.query.get_or_404(id, 'Event Donation not found')
        return event_donation

    @namespace.expect(event_donation_model)
    @namespace.marshal_with(event_donation_response_model)
    @jwt_required()
    def put(self, id):
        event_donation = EventDonation.query.get_or_404(id, 'Event Donation not found')

        data = namespace.payload
        user_id = data.get('userId')
        event_id = data.get('eventId')

        if user_id:
            User.query.get_or_404(user_id, 'User not found')
            event_donation.userId = user_id

        if event_id:
            Event.query.get_or_404(event_id, 'Event not found')
            event_donation.eventId = event_id

        for key, value in data.items():
            if key not in ['userId', 'eventId']:
                setattr(event_donation, key, value)

        db.session.commit()
        return event_donation

    @namespace.response(204, 'Event Donation deleted')
    @jwt_required()
    def delete(self, id):
        event_donation = EventDonation.query.get_or_404(id, 'Event Donation not found')
        db.session.delete(event_donation)
        db.session.commit()
        return '', 204
