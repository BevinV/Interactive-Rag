import os
import shutil

def reset_index():
    # Remove all index files
    index_files = [
        "storage/index.faiss",
        "storage/index.faiss.mapping.json",
        "storage/metadata.json",
        "storage/export.zip"
    ]
    
    for file_path in index_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed {file_path}")
    
    # Clear the docs directory but keep the folder
    docs_dir = "storage/docs"
    if os.path.exists(docs_dir):
        for filename in os.listdir(docs_dir):
            file_path = os.path.join(docs_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    print("Index reset complete. You can now start with a clean state.")

if __name__ == "__main__":
    reset_index()