import os
import shutil
import argparse

STORAGE_DIR = "../storage"
DOCS_DIR = os.path.join(STORAGE_DIR, "docs")
INDEX_PATH = os.path.join(STORAGE_DIR, "index.faiss")
METADATA_PATH = os.path.join(STORAGE_DIR, "metadata.json")

def reset_storage(keep_docs=False):
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)
        print("Removed index.faiss")
    
    if os.path.exists(METADATA_PATH):
        os.remove(METADATA_PATH)
        print("Removed metadata.json")
    
    if not keep_docs and os.path.exists(DOCS_DIR):
        shutil.rmtree(DOCS_DIR)
        print("Removed docs directory")
        os.makedirs(DOCS_DIR)  # Recreate empty docs dir
    
    print("Reset completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset storage.")
    parser.add_argument("--keep-docs", action="store_true", help="Keep original PDFs (default: remove all)")
    args = parser.parse_args()
    reset_storage(args.keep_docs)