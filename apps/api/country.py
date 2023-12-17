from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.models import Country
from extensions import db

namespace = Namespace(name='country', description='Countries operations')

country_model = namespace.model('Country', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
})

country_response_model = namespace.model('Country response', {
    'id': fields.Integer(),
    'name': fields.String(),
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class CountryList(Resource):
    @namespace.marshal_list_with(country_response_model)
    @jwt_required()
    def get(self):
        countries = Country.query.all()
        return countries

    @namespace.expect(country_model)
    @namespace.marshal_with(country_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        new_country = Country(**data)
        db.session.add(new_country)
        db.session.commit()
        return new_country, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Country')
@namespace.doc(security='Bearer', )
class CountryApi(Resource):
    @namespace.marshal_with(country_response_model)
    @jwt_required()
    def get(self, id):
        country = Country.query.get_or_404(id, 'Country not found')
        return country

    @namespace.expect(country_model)
    @namespace.marshal_with(country_response_model)
    @jwt_required()
    def put(self, id):
        country = Country.query.get_or_404(id, 'Country not found')

        data = namespace.payload

        for key, value in data.items():
            setattr(country, key, value)

        db.session.commit()
        return country

    @namespace.response(204, 'Country deleted')
    @jwt_required()
    def delete(self, id):
        country = Country.query.get_or_404(id, 'Country not found')
        db.session.delete(country)
        db.session.commit()
        return '', 204
