from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from apps.models import FavouriteOrganizer, Organizer, User
from extensions import db

namespace = Namespace(name='favourite_organizer', description='Favourite Organizer operations')

user_response_model = namespace.model('User favourite_organizer_response', {
    'id': fields.Integer(),
    'firstName': fields.String(),
    'lastName': fields.String(),
    'middleName': fields.String(),
    'birthday': fields.Date(),
    # 'password': fields.String(),
    'email': fields.String(),
    'avatar': fields.String(),
    'trusted': fields.Boolean(),
    'provider': fields.String(),
    'roleId': fields.Integer(),
})

organizer_response_model = namespace.model('Organizer favourite_organizer_response', {
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
})

favourite_organizer_model = namespace.model('Favourite Organizer', {
    'id': fields.Integer(readonly=True),
    'dateTime': fields.DateTime(required=True),
    'userId': fields.Integer(),
    'organizerId': fields.Integer(),
})

favourite_organizer_response_model = namespace.model('Favourite Organizer response', {
    'id': fields.Integer(),
    'dateTime': fields.DateTime(),
    'user': fields.Nested(user_response_model),
    'organizer': fields.Nested(organizer_response_model)
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class FavouriteOrganizerList(Resource):
    @namespace.marshal_list_with(favourite_organizer_response_model)
    @jwt_required()
    def get(self):
        favourite_organizers = FavouriteOrganizer.query.all()
        return favourite_organizers

    @namespace.expect(favourite_organizer_model)
    @namespace.marshal_with(favourite_organizer_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        user_id = data.get('userId')
        organizer_id = data.get('organizerId')
        if user_id:
            User.query.get_or_404(user_id, 'User not found')
        if organizer_id:
            Organizer.query.get_or_404(organizer_id, 'Organizer not found')
        new_favourite_organizer = FavouriteOrganizer(**data)
        db.session.add(new_favourite_organizer)
        db.session.commit()
        return new_favourite_organizer, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Favourite Organizer')
@namespace.doc(security='Bearer', )
class FavouriteOrganizerApi(Resource):
    @namespace.marshal_with(favourite_organizer_response_model)
    @jwt_required()
    def get(self, id):
        favourite_organizer = FavouriteOrganizer.query.get_or_404(id, 'Favourite Organizer not found')
        return favourite_organizer

    @namespace.expect(favourite_organizer_model)
    @namespace.marshal_with(favourite_organizer_response_model)
    @jwt_required()
    def put(self, id):
        favourite_organizer = FavouriteOrganizer.query.get_or_404(id, 'Favourite Organizer not found')

        data = namespace.payload
        user_id = data.get('userId')
        organizer_id = data.get('organizerId')

        if user_id:
            User.query.get_or_404(user_id, 'User not found')
            favourite_organizer.userId = user_id

        if organizer_id:
            Organizer.query.get_or_404(organizer_id, 'Organizer not found')
            favourite_organizer.organizerId = organizer_id

        for key, value in data.items():
            if key not in ['userId', 'organizerId']:
                setattr(favourite_organizer, key, value)

        db.session.commit()
        return favourite_organizer

    @namespace.response(204, 'Favourite Organizer deleted')
    @jwt_required()
    def delete(self, id):
        favourite_organizer = FavouriteOrganizer.query.get_or_404(id, 'Favourite Organizer not found')
        db.session.delete(favourite_organizer)
        db.session.commit()
        return '', 204


@namespace.route('/user_favourite_organizers')
@namespace.doc(security='Bearer', )
class UserFavorites(Resource):
    @namespace.marshal_with(favourite_organizer_response_model)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()['userId']
        favourite_organizers = FavouriteOrganizer.query.filter_by(userId=user_id).all()
        return favourite_organizers
