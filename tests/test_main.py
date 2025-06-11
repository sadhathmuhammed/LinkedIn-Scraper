import unittest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch
from app.linkedin import LinkedInScraper

class TestMain(unittest.TestCase):
    def setUp(self):
        """
        Initialize the test client and mock out the LinkedIn API calls.

        The ``_load_session`` method of the ``LinkedInScraper`` class is mocked to
        always return ``True``. This is necessary because the test runs in an environment
        where the session file is not present, so it needs to be mocked out to prevent
        the test from crashing.

        The ``fetch_connections`` method of the ``LinkedInScraper`` class is also
        mocked out to return a canned response. This is necessary because the test
        is not allowed to make real API calls.
        """
        self.client = TestClient(app)
        self.auth = ("admin", "secret")
        patcher = patch.object(LinkedInScraper, '_load_session', return_value=True)
        self.mock_load_session = patcher.start()
        self.addCleanup(patcher.stop)

        patcher_fetch = patch.object(LinkedInScraper, 'fetch_connections',
                                     return_value=[{
                                         "name": "Jane Doe",
                                         "title": "Software Engineer",
                                         "profile_url": "https://www.linkedin.com/in/janedoe/"
                                     }])
        self.mock_fetch = patcher_fetch.start()
        self.addCleanup(patcher_fetch.stop)

    def test_connections_unauthorized(self):
        """
        Test unauthorized access to the connections endpoint.

        This test ensures that a request to the /connections endpoint without
        proper authentication returns a 401 Unauthorized status code.
        """
        response = self.client.get("/connections")
        self.assertEqual(response.status_code, 401)

    def test_connections_authorized(self):
        """
        Test authorized access to the connections endpoint.

        This test ensures that a request to the /connections endpoint with
        proper authentication returns a 200 OK status code and a JSON response
        with a 'connections' key that contains a list of connections.
        """
        response = self.client.get("/connections?start=0&count=1", auth=self.auth)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn('connections', data)
        self.assertIsInstance(data['connections'], list)
