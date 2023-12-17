from datetime import timedelta

from flask import jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from flask_restx import Resource, Namespace
from flask_restx.inputs import email
from flask_restx.reqparse import RequestParser
from werkzeug.security import check_password_hash

from apps.models import User
from extensions import db

namespace = Namespace(name='auth')

EXPIRE_DELTA = timedelta(days=1)

#  login parser
login_parser = RequestParser(bundle_errors=True)
login_parser.add_argument(
    name="email", type=email(), required=True, nullable=False, location='json'
)
login_parser.add_argument(
    name="password", type=str, required=True, nullable=False, location='json'
)


@namespace.route("/login", endpoint="auth_login")
class LoginUser(Resource):
    @namespace.expect(login_parser)
    def post(self):
        data = login_parser.parse_args()
        email = data['email']
        password = data['password']
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404

        if not check_password_hash(user.password, password):
            return {'message': 'Invalid password'}, 401

        # Создаём токен доступа
        access_token = create_access_token(
            identity={
                'email': user.email,
                'userId': user.id,
                'roleId': user.roleId,
            },
            expires_delta=EXPIRE_DELTA,
        )
        refresh_token = create_refresh_token(identity=user.id)
        response = jsonify(
            message="success",
            accessToken=access_token,
            refreshToken=refresh_token,
        )
        return response


@namespace.route('/refresh_token')
@namespace.doc(security='Bearer', )
class JwtRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        new_token = create_access_token(
            identity={
                'email': user.email,
                'userId': user.id,
                'roleId': user.roleId,
            },
            expires_delta=EXPIRE_DELTA,
        )

        refresh_token = create_refresh_token(identity=user.id)
        # Вернуть новый токен в ответе
        response = jsonify(
            message="success",
            accessToken=new_token,
            refreshToken=refresh_token,
        )
        return response
