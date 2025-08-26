import os 
import zipfile
import argparse

STORAGE_DIR = "../storage"
INDEX_PATH = os.path.join(STORAGE_DIR, "index.faiss")
METADATA_PATH = os.path.join(STORAGE_DIR, "metadata.json")
OUTPUT_DIR = "."


def export_data(output_file="export.zip"):
	output_path = os.path.join(OUTPUT_DIR, output_file)
	with zipfile.Zipfile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
		if os.path.exists(INDEX_PATH):
            zipf.write(INDEX_PATH, arcname="index.faiss")
        else:
            print("Warning: index.faiss not found.")
        
        if os.path.exists(METADATA_PATH):
            zipf.write(METADATA_PATH, arcname="metadata.json")
        else:
            print("Warning: metadata.json not found.")

    print(f"Export completed: {output_patht}")



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Export FAISS index and metadata as zip")
	parser.add_argument("--output", default="export.zip", help="Output zip file name (default: export.zip)")
	args = parser.parse_args()
	export_data(args.output)
	
