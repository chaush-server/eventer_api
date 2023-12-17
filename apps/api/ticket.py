from datetime import datetime

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.models import Ticket, Event, TicketTypeEnum, Booking
from extensions import db

namespace = Namespace(name='ticket', description='Ticket operations')

ticket_model = namespace.model('Ticket', {
    'id': fields.Integer(readonly=True),
    'ticketType': fields.String(enum=[enum.value for enum in TicketTypeEnum]),
    'seat': fields.Integer(),
    'eventDatesId': fields.Integer(),
    'bookingId': fields.Integer()
})

event_response_model = namespace.model('Event booking_response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'description': fields.String(),
    'expectedAmount': fields.Float(),
    'recommendedDonation': fields.Float(),
    'validateStatus': fields.String(),
    'countOfMembers': fields.Integer(),
    'status': fields.String(),
    'concession': fields.String(),
    'genreId': fields.Integer(),
    'organizerId': fields.Integer(),
    'eventDatesId': fields.Integer(),
    'venuesId': fields.Integer(),
})

event_dates_response_model = namespace.model('EventDates ticket_response', {
    'id': fields.Integer(),
    'startDateTime': fields.DateTime(),
    'endDateTime': fields.DateTime(),
    'eventId': fields.Integer(),
})

user_response_model = namespace.model('User booking_response', {
    'id': fields.Integer(),
    'firstName': fields.String(),
    'lastName': fields.String(),
    'middleName': fields.String(),
    'email': fields.String(),
    'avatar': fields.String(),
})

booking_response_model = namespace.model('Booking ticket_response', {
    'id': fields.Integer(),
    'user': fields.Nested(user_response_model),
    'event': fields.Nested(event_response_model),
})

ticket_response_model = namespace.model('Ticket response', {
    'id': fields.Integer(),
    'ticketType': fields.String(),
    'seat': fields.Integer(),
    'booking': fields.Nested(booking_response_model),
    'eventDates': fields.Nested(event_dates_response_model),
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class TicketList(Resource):
    @namespace.marshal_list_with(ticket_response_model)
    @jwt_required()
    def get(self):
        tickets = Ticket.query.all()
        return tickets

    @namespace.expect(ticket_model)
    @namespace.marshal_with(ticket_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        Event.query.get_or_404(data['eventDatesId'], 'Event not found')
        Booking.query.get_or_404(data['bookingId'], 'Booking not found')
        new_ticket = Ticket(**data, dateTime=datetime.now())
        db.session.add(new_ticket)
        db.session.commit()
        return new_ticket, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Ticket')
@namespace.doc(security='Bearer', )
class TicketApi(Resource):
    @namespace.marshal_with(ticket_response_model)
    @jwt_required()
    def get(self, id):
        ticket = Ticket.query.get_or_404(id, 'Ticket not found')
        return ticket

    @namespace.expect(ticket_model)
    @namespace.marshal_with(ticket_response_model)
    @jwt_required()
    def put(self, id):
        data = namespace.payload

        ticket = Ticket.query.get_or_404(id, 'Ticket not found')
        Event.query.get_or_404(data.get('eventDatesId'), 'EventDates not found')
        Booking.query.get_or_404(data.get('bookingId'), 'Booking not found')

        for key, value in data.items():
            setattr(ticket, key, value)

        db.session.commit()
        return ticket

    @namespace.response(204, 'Ticket deleted')
    @jwt_required()
    def delete(self, id):
        ticket = Ticket.query.get_or_404(id, 'Ticket not found')
        db.session.delete(ticket)
        db.session.commit()
        return '', 204
