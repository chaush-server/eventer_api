from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from apps.api.category import category_response_model
from apps.api.event import event_response_model
from apps.models import Genre, Category, Event
from extensions import db

namespace = Namespace(name='genre', description='Genre operations')

genre_model = namespace.model('Genre', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'categoryId': fields.Integer(),
})

genre_response_model = namespace.model('Genre response', {
    'id': fields.Integer(),
    'name': fields.String(),
    'category': fields.Nested(category_response_model),
    'events': fields.Nested(event_response_model)
})


@namespace.route('/')
@namespace.doc(security='Bearer', )
class GenreList(Resource):
    @namespace.marshal_list_with(genre_response_model)
    @jwt_required()
    def get(self):
        genres = Genre.query.all()
        return genres

    @namespace.expect(genre_model)
    @namespace.marshal_with(genre_response_model, code=201)
    @jwt_required()
    def post(self):
        data = namespace.payload
        Category.query.get_or_404(data['categoryId'], 'Category not found')
        new_genre = Genre(**data)
        db.session.add(new_genre)
        db.session.commit()
        return new_genre, 201


@namespace.route('/<id>')
@namespace.param('id', 'The unique identifier of a Genre')
@namespace.doc(security='Bearer', )
class GenreApi(Resource):
    @namespace.marshal_with(genre_response_model)
    @jwt_required()
    def get(self, id):
        genre = Genre.query.get_or_404(id, 'Genre not found')
        return genre

    @namespace.expect(genre_model)
    @namespace.marshal_with(genre_response_model)
    @jwt_required()
    def put(self, id):
        genre = Genre.query.get_or_404(id, 'Genre not found')

        data = namespace.payload
        category_id = data.get('category_id')
        event_id = data.get('event_id')

        if category_id:
            Category.query.get_or_404(category_id, 'Category not found')
            genre.categoryId = category_id

        if event_id:
            Event.query.get_or_404(event_id, 'Event not found')
            genre.eventId = event_id

        for key, value in data.items():
            if key not in ['category_id', 'event_id']:
                setattr(genre, key, value)

        db.session.commit()
        return genre

    @namespace.response(204, 'Genre deleted')
    @jwt_required()
    def delete(self, id):
        genre = Genre.query.get_or_404(id, 'Genre not found')
        db.session.delete(genre)
        db.session.commit()
        return '', 204
