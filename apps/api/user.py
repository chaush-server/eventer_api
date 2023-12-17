from flask import abort
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash

from apps.models import User
from extensions import db

namespace = Namespace(name='user', description='Users operations')

user_model = namespace.model('User', {
    'id': fields.Integer(readonly=True),
    'firstName': fields.String(required=True),
    'lastName': fields.String(required=True),
    'middleName': fields.String(required=True),
    'birthday': fields.DateTime(),
    'password': fields.String(required=True),
    'email': fields.String(required=True),
    'avatar': fields.String(),
    'trusted': fields.Boolean(default=False),
    'provider': fields.String(default='SYSTEM', enum=['SYSTEM', 'ESIA', 'GOOGLE'])
})

organizer_list_response_model = namespace.model('Organizer response', {
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

user_response_model = namespace.model('User response', {
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
    'organizers': fields.List(fields.Nested(organizer_list_response_model)),
    'roleId': fields.Integer(),
})


@namespace.route('/')
class UserList(Resource):
    @namespace.marshal_list_with(user_response_model)
    def get(self):
        users = User.query.all()
        return users

    @namespace.expect(user_model)
    @namespace.marshal_with(user_response_model, code=201)
    def post(self):
        data = namespace.payload
        if User.query.filter_by(email=data['email']).first():
            abort(401, 'Email exists')
        new_user = User(**data)
        new_user.password = generate_password_hash(new_user.password)
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a User')
class UserApi(Resource):
    @namespace.marshal_with(user_response_model)
    def get(self, id):
        user = User.query.get_or_404(id, 'User not found')
        return user

    @namespace.expect(user_model)
    @namespace.marshal_with(user_response_model)
    @namespace.doc(security='Bearer', )
    @jwt_required()
    def put(self, id):
        user = User.query.get_or_404(id, 'User not found')
        data = namespace.payload

        for key, value in data.items():
            print(key, value)
            if key == 'password':
                value = generate_password_hash(value)
            setattr(user, key, value)

        db.session.commit()
        return user

    @namespace.response(204, 'User deleted')
    @namespace.doc(security='Bearer', )
    @jwt_required()
    def delete(self, id):
        user = User.query.get_or_404(id, 'User not found')
        db.session.delete(user)
        db.session.commit()
        return '', 204
