import unittest
import faiss
import os
import numpy as np
from backend.index_manager import get_index, save_index, DIMENSION

class TestIndexManager(unittest.TestCase):
    def setUp(self):
        self.test_index_path = "test_index.faiss"
        if os.path.exists(self.test_index_path):
            os.remove(self.test_index_path)

    def tearDown(self):
        if os.path.exists(self.test_index_path):
            os.remove(self.test_index_path)

    def test_get_index_new(self):
        index = get_index(self.test_index_path, DIMENSION)
        self.assertIsInstance(index, faiss.IndexFlatL2)
        self.assertEqual(index.d, DIMENSION)

    def test_save_and_get_index(self):
        index = faiss.IndexFlatL2(DIMENSION)
        vectors = np.random.random((5, DIMENSION)).astype(np.float32)
        index.add(vectors)
        save_index(index, self.test_index_path)
        loaded_index = get_index(self.test_index_path, DIMENSION)
        self.assertEqual(loaded_index.ntotal, 5)

if __name__ == "__main__":
    unittest.main()