import flask
from apps import create_app
# import unittest
# from tests import test_api
#
# suite = unittest.TestLoader().loadTestsFromModule(test_api)
# unittest.TextTestRunner(verbosity=2).run(suite)

app = create_app()


@app.route('/')
def redirect():
    return flask.redirect('/api/v1/')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
