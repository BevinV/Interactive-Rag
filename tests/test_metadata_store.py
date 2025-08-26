import unittest
import os
import json
from backend.metadata_store import get_metadata, save_metadata, get_next_id

class TestMetadataStore(unittest.TestCase):
    def setUp(self):
        self.test_metadata_path = "test_metadata.json"
        if os.path.exists(self.test_metadata_path):
            os.remove(self.test_metadata_path)

    def tearDown(self):
        if os.path.exists(self.test_metadata_path):
            os.remove(self.test_metadata_path)

    def test_get_metadata_new(self):
        metadata = get_metadata(self.test_metadata_path)
        self.assertEqual(metadata["chunks"], {})
        self.assertEqual(metadata["next_id"], 0)

    def test_save_and_get_metadata(self):
        metadata = {"chunks": {0: {"doc": "test.pdf", "page": 1, "text": "test"}}, "next_id": 1}
        save_metadata(metadata, self.test_metadata_path)
        loaded_metadata = get_metadata(self.test_metadata_path)
        self.assertEqual(loaded_metadata["chunks"][0]["text"], "test")
        self.assertEqual(loaded_metadata["next_id"], 1)

    def test_get_next_id(self):
        metadata = get_metadata(self.test_metadata_path)
        id1 = get_next_id(metadata)
        self.assertEqual(id1, 0)
        self.assertEqual(metadata["next_id"], 1)
        id2 = get_next_id(metadata)
        self.assertEqual(id2, 1)
        self.assertEqual(metadata["next_id"], 2)

if __name__ == "__main__":
    unittest.main()