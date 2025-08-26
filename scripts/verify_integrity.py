# scripts/verify_integrity.py
import os
import json
import faiss

def verify_integrity():
    # Check if index exists
    index_path = "storage/index.faiss"
    mapping_path = index_path + ".mapping.json"
    metadata_path = "storage/metadata.json"
    
    if not os.path.exists(index_path):
        print("Index file does not exist")
        return False
    
    if not os.path.exists(mapping_path):
        print("Mapping file does not exist")
        return False
    
    if not os.path.exists(metadata_path):
        print("Metadata file does not exist")
        return False
    
    # Load index
    index = faiss.read_index(index_path)
    index_size = index.ntotal
    
    # Load mappings
    with open(mapping_path, 'r') as f:
        mapping_data = json.load(f)
        id_map = {int(k): v for k, v in mapping_data.get("id_map", {}).items()}
    
    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Check consistency
    mappings_count = len(id_map)
    metadata_count = len(metadata)
    
    print(f"Index size: {index_size}")
    print(f"Mappings count: {mappings_count}")
    print(f"Metadata count: {metadata_count}")
    
    # Check if all indices in the mapping exist in the index
    valid_mappings = all(0 <= idx < index_size for idx in id_map.keys())
    
    # Check if all chunk IDs in metadata have mappings
    all_chunks_have_mappings = all(chunk_id in mapping_data.get("reverse_id_map", {}) for chunk_id in metadata.keys())
    
    is_consistent = (index_size == mappings_count == metadata_count and 
                    valid_mappings and all_chunks_have_mappings)
    
    print(f"Data is consistent: {is_consistent}")
    
    if not is_consistent:
        # Find missing mappings
        missing_mappings = [chunk_id for chunk_id in metadata.keys() if chunk_id not in mapping_data.get("reverse_id_map", {})]
        print(f"Missing mappings for {len(missing_mappings)} chunks")
        
        # Find invalid indices
        invalid_indices = [idx for idx in id_map.keys() if idx < 0 or idx >= index_size]
        print(f"Invalid indices in mapping: {invalid_indices}")
    
    return is_consistent

if __name__ == "__main__":
    verify_integrity()