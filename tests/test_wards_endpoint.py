import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class WardsEndpointTests(unittest.TestCase):
    def test_wards_endpoint_returns_options(self):
        with TestClient(app) as client:
            response = client.get("/wards/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsInstance(payload, list)
        self.assertTrue(payload)
        self.assertTrue(all("id" in ward and "name" in ward for ward in payload))


if __name__ == "__main__":
    unittest.main()
