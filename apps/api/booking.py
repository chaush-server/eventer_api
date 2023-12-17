from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask_restx.reqparse import RequestParser
from flask import request

from apps.api.event import event_response_model
from apps.models import Booking, Event, User, EventDates, TicketTypeEnum, Ticket
from extensions import db

namespace = Namespace(name='booking', description='Booking operations')

ticket_expect_model = namespace.model('Ticket booking_expect', {
    'id': fields.Integer(readonly=True),
    'ticketType': fields.String(enum=[enum.value for enum in TicketTypeEnum]),
    'seat': fields.Integer(),
    'eventDatesId': fields.Integer()
})

user_booking_response_model = namespace.model('User booking_response', {
    'id': fields.Integer(),
    'firstName': fields.String(),
    'lastName': fields.String(),
    'email': fields.String(),
    'avatar': fields.String(),
})

booking_expect_model = namespace.model('Booking', {
    'id': fields.Integer(readonly=True),
    'userId': fields.Integer(),
    'eventId': fields.Integer(),
    'ticket': fields.Nested(ticket_expect_model),
})

booking_response_model = namespace.model('Booking response', {
    'id': fields.Integer(),
    'user': fields.Nested(user_booking_response_model),
    'event': fields.Nested(event_response_model),
    'tickets': fields.List(fields.Nested(ticket_expect_model))
})

booking_parser = RequestParser(bundle_errors=True)
booking_parser.add_argument(name="eventDatesId", type=int, location='args')
booking_parser.add_argument(name="eventId", type=int, location='args')
booking_parser.add_argument(name="userId", type=int, location='args')


@namespace.route('/')
@namespace.doc(security='Bearer', )
class BookingList(Resource):
    @namespace.marshal_list_with(booking_response_model)
    @namespace.expect(booking_parser)
    @jwt_required()
    def get(self):
        bookings = Booking.query

        event_id = request.args.get('eventId')
        user_id = request.args.get('userId')

        if event_id:
            bookings = bookings.filter_by(eventId=int(event_id))
        if user_id:
            bookings = bookings.filter_by(userId=int(user_id))
        bookings = bookings.all()
        return bookings

    @namespace.expect(booking_expect_model)
    @namespace.marshal_with(booking_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        ticket = data.pop('ticket')

        user_id: int = data['userId']
        event_id: int = data['eventId']
        event_dates_id: int = ticket['eventDatesId']

        User.query.get_or_404(user_id, 'User not found')
        EventDates.query.get_or_404(event_dates_id, 'EventDates not found')

        booking_exist = Booking.query.filter_by(userId=user_id, eventId=event_id).first()

        if booking_exist is None:
            new_booking = Booking(**data)
            db.session.add(new_booking)
            db.session.flush()
        else:
            new_booking = booking_exist

        ticket = Ticket(**ticket, bookingId=new_booking.id)
        db.session.add(ticket)

        db.session.commit()
        return new_booking, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Booking')
@namespace.doc(security='Bearer', )
class BookingApi(Resource):
    @namespace.marshal_with(booking_response_model)
    @jwt_required()
    def get(self, id):
        booking = Booking.query.get_or_404(id, 'Booking not found')
        return booking

    @namespace.expect(booking_expect_model)
    @namespace.marshal_with(booking_response_model)
    @jwt_required()
    def put(self, id):
        booking = Booking.query.get_or_404(id, 'Booking not found')

        data = namespace.payload
        event_id = data.get('eventId')
        user_id = data.get('userId')

        if event_id:
            Event.query.get_or_404(event_id, 'Event not found')
            booking.dateTime = event_id

        if user_id:
            User.query.get_or_404(user_id, 'User not found')
            booking.userId = user_id

        for key, value in data.items():
            if key not in ['eventId', 'userId']:
                setattr(booking, key, value)

        db.session.commit()
        return booking

    @namespace.response(204, 'Booking deleted')
    @jwt_required()
    def delete(self, id):
        booking = Booking.query.get_or_404(id, 'Booking not found')
        db.session.delete(booking)
        db.session.commit()
        return '', 204
