import unittest
from apps import create_app


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

    def auth_header(self):
        pass

    def testGetUser(self):
        print(self.client.get('/api/v1/event/').data.decode('unicode-escape'))


if __name__ == '__main__':
    unittest.main()
