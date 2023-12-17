from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.api.state import state_response_model
from apps.models import City, State
from extensions import db

namespace = Namespace(name='city', description='City operations')

city_model = namespace.model('City', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'stateId': fields.Integer(),
})

city_response_model = namespace.model('City response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'state': fields.Nested(state_response_model)
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class CityList(Resource):
    @namespace.marshal_list_with(city_response_model)
    @jwt_required()
    def get(self):
        cities = City.query.all()
        return cities

    @namespace.expect(city_model)
    @namespace.marshal_with(city_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        State.query.get_or_404(data['stateId'], 'State not found')
        new_city = City(**data)
        db.session.add(new_city)
        db.session.commit()
        return new_city, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a City')
@namespace.doc(security='Bearer', )
class CityApi(Resource):
    @namespace.marshal_with(city_response_model)
    @jwt_required()
    def get(self, id):
        city = City.query.get_or_404(id, 'City not found')
        return city

    @namespace.expect(city_model)
    @namespace.marshal_with(city_response_model)
    @jwt_required()
    def put(self, id):
        city = City.query.get_or_404(id, 'City not found')

        data = namespace.payload
        state_id = data.get('stateId')
        if state_id:
            State.query.get_or_404(state_id, 'State not found')
            city.stateId = state_id

        for key, value in data.items():
            if key not in ['stateId']:
                setattr(city, key, value)

        db.session.commit()
        return city

    @namespace.response(204, 'City deleted')
    @jwt_required()
    def delete(self, id):
        city = City.query.get_or_404(id, 'City not found')
        db.session.delete(city)
        db.session.commit()
        return '', 204
