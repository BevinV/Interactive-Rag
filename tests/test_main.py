import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ingest(self):
        # Note: For full testing, need a sample file, but skipping upload test here
        pass  # Implement with mock file if needed

    def test_query(self):
        response = self.client.post("/query", json={"query": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.json())

    # Add more endpoint tests as needed

if __name__ == "__main__":
    unittest.main()