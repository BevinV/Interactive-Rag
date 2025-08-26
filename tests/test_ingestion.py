import unittest
from backend.ingestion import process_pdf
import os

class TestIngestion(unittest.TestCase):
    def test_process_pdf(self):
        # Assuming a sample PDF in storage/docs for testing
        test_pdf = os.path.join("storage/docs", "sample.pdf")
        if not os.path.exists(test_pdf):
            self.skipTest("Sample PDF not found for testing.")
        
        chunks = process_pdf(test_pdf)
        self.assertGreater(len(chunks), 0)
        self.assertIn("page", chunks[0])
        self.assertIn("text", chunks[0])
        self.assertTrue(isinstance(chunks[0]["text"], str))

if __name__ == "__main__":
    unittest.main()