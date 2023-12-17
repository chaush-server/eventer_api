from datetime import datetime
from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from flask_restx.reqparse import RequestParser
from sqlalchemy import func

from apps.api.user import user_response_model
from apps.models import Organizer, User, FavouriteOrganizer, Event, Feedback
from extensions import db
from flask_jwt_extended import get_jwt_identity

namespace = Namespace(name='organizer', description='Organizers operations')

organizer_model = namespace.model('Organizer', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'logo': fields.String(required=True),
    'background': fields.String(),
    'description': fields.String(),
    'cardNumber': fields.String(required=True),
    'cardHolderName': fields.String(required=True),
    'facebook': fields.String(),
    'telegram': fields.String(),
    'vk': fields.String(),
    'twitter': fields.String(),
    'instagram': fields.String(),
    'userId': fields.Integer(),
})

organizer_response_model = namespace.model('Organizer response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'logo': fields.String(),
    'background': fields.String(),
    'description': fields.String(),
    'cardNumber': fields.String(),
    'cardHolderName': fields.String(),
    'facebook': fields.String(),
    'telegram': fields.String(),
    'vk': fields.String(),
    'twitter': fields.String(),
    'instagram': fields.String(),
    'user': fields.Nested(user_response_model)
})

organizer_info_response_model = namespace.model('OrganizerInfo response', {
    'countOfSubscribers': fields.Integer(),
    'countOfEvents': fields.Integer(),
    "averageRate": fields.Float(),
    'isSubscribed': fields.Boolean(),
})

organizer_info_parser = RequestParser(bundle_errors=True)
organizer_info_parser.add_argument(
    name="toggle_subscribe", type=bool, required=True, nullable=False, default=True, location='args'
)


@namespace.route('/')
@namespace.doc(security='Bearer', )
class OrganizerList(Resource):
    @namespace.marshal_list_with(organizer_response_model)
    @jwt_required()
    def get(self):
        organizers = Organizer.query.all()
        return organizers

    @namespace.expect(organizer_model)
    @namespace.marshal_with(organizer_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        User.query.get_or_404(data['userId'], 'User not found')
        new_organizer = Organizer(**data)
        db.session.add(new_organizer)
        db.session.commit()
        return new_organizer, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of an Organizer')
@namespace.doc(security='Bearer', )
class OrganizerApi(Resource):
    @namespace.marshal_with(organizer_response_model)
    @jwt_required()
    def get(self, id):
        organizer = Organizer.query.get_or_404(id, 'Organizer not found')
        return organizer

    @namespace.expect(organizer_model)
    @namespace.marshal_with(organizer_response_model)
    @jwt_required()
    def put(self, id):
        organizer = Organizer.query.get_or_404(id, 'Organizer not found')

        data = namespace.payload
        user_id = data.get('userId')

        if user_id:
            User.query.get_or_404(user_id, 'User not found')
            organizer.userId = user_id

        for key, value in data.items():
            print(key)
            if key not in ['userId']:
                setattr(organizer, key, value)

        db.session.commit()
        return organizer

    @namespace.response(204, 'Organizer deleted')
    @jwt_required()
    def delete(self, id):
        organizer = Organizer.query.get_or_404(id, 'Organizer not found')
        db.session.delete(organizer)
        db.session.commit()
        return '', 204


@namespace.route('/info/<id>')
@namespace.param('id', 'The unique identifier of an Organizer')
@namespace.doc(security='Bearer', )
class OrganizerInfo(Resource):
    @namespace.marshal_with(organizer_info_response_model)
    @namespace.expect(organizer_info_parser)
    @jwt_required()
    def get(self, id):
        Organizer.query.get_or_404(id, 'Organizer not found')

        user_id = get_jwt_identity()['userId']
        toggle_subscribe = request.args.get('toggle_subscribe', default=False, type=lambda v: v.lower() == 'true')

        is_subscribed = True if FavouriteOrganizer.query.filter_by(organizerId=id, userId=user_id).first() else False

        if toggle_subscribe:
            if is_subscribed:
                favourite_organizer = FavouriteOrganizer.query.filter_by(organizerId=id, userId=user_id).first()
                db.session.delete(favourite_organizer)
                is_subscribed = False
            else:
                favourite_organizer = FavouriteOrganizer(dateTime=datetime.now(), userId=user_id, organizerId=id)
                db.session.add(favourite_organizer)
                is_subscribed = True

        db.session.commit()

        count_of_subscribers = FavouriteOrganizer.query.filter_by(organizerId=id).count()
        count_of_events = Event.query.filter_by(organizerId=id).count()
        average_rate = db.session.query(func.avg(Feedback.rate)).join(Event).join(Organizer).filter(
            Organizer.id == id).scalar()

        return {
            'countOfSubscribers': count_of_subscribers,
            'countOfEvents': count_of_events,
            "averageRate": average_rate,
            'isSubscribed': is_subscribed,
        }
