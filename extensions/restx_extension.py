# from flask import g
# from flask_jwt_extended import get_jwt_identity
from flask_restx import Api

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    title='Eventer',
    version='1.0',
    description='Rest API Eventer',
    # security='jwt',
    authorizations=authorizations,
)
