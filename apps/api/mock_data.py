from flask import jsonify
from flask_restx import Resource, Namespace
from tests.database_mock import mock_database

namespace = Namespace(name='mock_data')


@namespace.route("/generate", endpoint="mock_data")
class MockData(Resource):
    @staticmethod
    def post():
        mock_database()
        return jsonify(message='success')
