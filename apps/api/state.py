from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.api.country import country_response_model
from apps.models import State, Country
from extensions import db

namespace = Namespace(name='state', description='State operations')

state_model = namespace.model('State', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'countryId': fields.Integer(),
})

state_response_model = namespace.model('State response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'country': fields.Nested(country_response_model),
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class StateList(Resource):
    @namespace.marshal_list_with(state_response_model)
    @jwt_required()
    def get(self):
        states = State.query.all()
        return states

    @namespace.expect(state_model)
    @namespace.marshal_with(state_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        Country.query.get_or_404(data['countryId'], 'Country not found')
        new_state = State(**data)
        db.session.add(new_state)
        db.session.commit()
        return new_state, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a State')
@namespace.doc(security='Bearer', )
class StateApi(Resource):
    @namespace.marshal_with(state_response_model)
    @jwt_required()
    def get(self, id):
        state = State.query.get_or_404(id, 'State not found')
        return state

    @namespace.expect(state_model)
    @namespace.marshal_with(state_response_model)
    @jwt_required()
    def put(self, id):
        state = State.query.get_or_404(id, 'State not found')

        data = namespace.payload
        country_id = data.get('countryId')

        if country_id:
            Country.query.get_or_404(country_id, 'Country not found')
            state.countryId = country_id

        for key, value in data.items():
            if key not in ['countryId']:
                setattr(state, key, value)

        db.session.commit()
        return state

    @namespace.response(204, 'State deleted')
    @jwt_required()
    def delete(self, id):
        state = State.query.get_or_404(id, 'State not found')
        db.session.delete(state)
        db.session.commit()
        return '', 204
