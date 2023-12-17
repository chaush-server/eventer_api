from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.models import Category
from extensions import db

namespace = Namespace(name='category', description='Categories operations')

category_model = namespace.model('Category', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
})

category_response_model = namespace.model('Category response', {
    'id': fields.Integer(),
    'name': fields.String()
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class CategoryList(Resource):
    @namespace.marshal_list_with(category_response_model)
    @jwt_required()
    def get(self):
        categories = Category.query.all()
        return categories

    @namespace.expect(category_model)
    @namespace.marshal_with(category_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        new_category = Category(**data)
        db.session.add(new_category)
        db.session.commit()
        return new_category, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Category')
@namespace.doc(security='Bearer', )
class CategoryApi(Resource):
    @namespace.marshal_with(category_response_model)
    @jwt_required()
    def get(self, id):
        category = Category.query.get_or_404(id, 'Category not found')
        return category

    @namespace.expect(category_model)
    @namespace.marshal_with(category_response_model)
    @jwt_required()
    def put(self, id):
        category = Category.query.get_or_404(id, 'Category not found')

        data = namespace.payload

        for key, value in data.items():
            setattr(category, key, value)

        db.session.commit()
        return category

    @namespace.response(204, 'Category deleted')
    @jwt_required()
    def delete(self, id):
        category = Category.query.get_or_404(id, 'Category not found')
        db.session.delete(category)
        db.session.commit()
        return '', 204
