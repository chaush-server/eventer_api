from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask_restx.reqparse import RequestParser
from flask import request
from apps.api.event import event_response_model
from apps.api.user import user_response_model
from apps.models import Feedback, Event, User, Organizer
from extensions import db

PER_PAGE = 15

namespace = Namespace(name='feedback', description='Feedback operations')

feedback_model = namespace.model('Feedback', {
    'id': fields.Integer(readonly=True),
    'description': fields.String(required=True),
    'rate': fields.Integer(required=True),
    'dateTime': fields.DateTime(required=True),
    'photos': fields.List(fields.String()),
    'eventId': fields.Integer(),
    'userId': fields.Integer()
})

feedback_response_model = namespace.model('Feedback response', {
    'id': fields.Integer(),
    'description': fields.String(),
    'rate': fields.Integer(),
    'dateTime': fields.DateTime(),
    'photos': fields.List(fields.String()),
    'event': fields.Nested(event_response_model),
    'user': fields.Nested(user_response_model)
})
feedback_req_parser = RequestParser(bundle_errors=True)
feedback_req_parser.add_argument(name="organizerId", type=int, location="args")
feedback_req_parser.add_argument(name="page", type=int, nullable=False, location="args")


@namespace.route('/')
@namespace.doc(security='Bearer', )
class FeedbackList(Resource):
    @namespace.marshal_list_with(feedback_response_model)
    @namespace.expect(feedback_req_parser)
    @jwt_required()
    def get(self):
        orginzer_id = request.args.get('organizerId')
        page = request.args.get('page')
        feedbacks = Feedback.query
        if orginzer_id:
            feedbacks = feedbacks.filter(
                Feedback.eventId == Event.id,
                Event.organizerId == Organizer.id,
                Organizer.id == orginzer_id
            )
        if page:
            return feedbacks.paginate(page=int(page), per_page=PER_PAGE).items
        else:
            return feedbacks.all()

    @namespace.expect(feedback_model)
    @namespace.marshal_with(feedback_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        Event.query.get_or_404(data['eventId'], 'Event not found')
        User.query.get_or_404(data['userId'], 'User not found')
        new_feedback = Feedback(**data)
        db.session.add(new_feedback)
        db.session.commit()
        return new_feedback, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Feedback')
@namespace.doc(security='Bearer', )
class FeedbackApi(Resource):
    @namespace.marshal_with(feedback_response_model)
    @jwt_required()
    def get(self, id):
        feedback = Feedback.query.get_or_404(id, 'Feedback not found')
        return feedback

    @namespace.expect(feedback_model)
    @namespace.marshal_with(feedback_response_model)
    @jwt_required()
    def put(self, id):
        feedback = Feedback.query.get_or_404(id, 'Feedback not found')

        data = namespace.payload
        event_id = data.get('eventId')
        user_id = data.get('userId')

        if event_id:
            Event.query.get_or_404(event_id, 'Event not found')
            feedback.eventId = event_id

        if user_id:
            User.query.get_or_404(user_id, 'User not found')
            feedback.userId = user_id

        for key, value in data.items():
            if key not in ['eventId', 'userId']:
                setattr(feedback, key, value)

        db.session.commit()
        return feedback

    @namespace.response(204, 'Feedback deleted')
    @jwt_required()
    def delete(self, id):
        feedback = Feedback.query.get_or_404(id, 'Feedback not found')
        db.session.delete(feedback)
        db.session.commit()
        return '', 204
