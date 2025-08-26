import zipfile
import json
import sys

def check_export(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zipf:
            file_list = zipf.namelist()
            print("Files in export zip:")
            for file in file_list:
                print(f"  - {file}")
            
            # Check if required files are present
            required_files = ['index.faiss', 'mappings.json', 'metadata.json']
            missing_files = [f for f in required_files if f not in file_list]
            
            if missing_files:
                print(f"Missing files: {missing_files}")
            else:
                print("All required files are present.")
                
            # Try to read the mappings file
            if 'mappings.json' in file_list:
                with zipf.open('mappings.json') as f:
                    mappings = json.load(f)
                    print(f"Mappings file contains {len(mappings)} entries")
            
            # Try to read the metadata file
            if 'metadata.json' in file_list:
                with zipf.open('metadata.json') as f:
                    metadata = json.load(f)
                    print(f"Metadata file contains {len(metadata)} entries")
                
    except Exception as e:
        print(f"Error checking export file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_export(sys.argv[1])
    else:
        check_export("storage/export.zip")