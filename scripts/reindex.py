import os
import argparse
from backend.ingestion import process_pdf
from backend.embeddings import get_embedding_model, embed_text
from backend.index_manager import get_index, save_index, DIMENSION
from backend.metadata_store import get_metadata, save_metadata, get_next_id

STORAGE_DIR = "../storage"
DOCS_DIR = os.path.join(STORAGE_DIR, "docs")
INDEX_PATH = os.path.join(STORAGE_DIR, "index.faiss")
METADATA_PATH = os.path.join(STORAGE_DIR, "metadata.json")


def reindex_docs(doc_names=None):
	model = get_embedding_model()
	index = faiss.IndexFlatL2(DIMENSION)
	metadata = {"chunks": {}, "next_id": 0}

	if doc_names is None:
		doc_names = [f for f in os.listdir(DOCS_DIR) if f.endswith('.pdf')]

	for filename in doc_names:
		doc_path = os.path.join(DOCS_DIR, filename)
		if not os.path.exists(doc_path):
			print(f"Warning: {filename} not found, skipping.")
            continue

        chunks = process_pdf(doc_path)

        for chunk in chunks:
        	text = chunk["text"]
        	page = chunk["page"]
        	embedding = embed_text(model, text)

        	chunk_id = get_next_id(metadata)
        	metadata["chunks"][chunk_id] = {
        		"doc": filename
        		"page": page
        		"text": text 
        	}
        	index.add_with_ids(np.array([embedding]), np.array([chunk_id], dtype=np.int64))

    save_index(index, INDEX_PATH)
    save_metadata(metadata, METADATA_PATH)
    print("Reindexing completed successfully")


if __name__ == "__main__":
	import faiss
	parser = argparse.ArgumentParser(description="Reindex PDF documents.")
	parser.add_argument("--docs", nargs="+", help="Specific document names to reindex (default: all PDFs)")
    args = parser.parse_args()
    reindex_docs(args.docs)
