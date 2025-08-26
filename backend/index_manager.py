import faiss
import numpy as np
import os
import json
import zipfile
from typing import Dict, List, Tuple

class IndexManager:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.mapping_path = index_path + ".mapping.json"
        self.index = None
        self.id_map = {} 
        self.dimension = None  
        
        # Load existing index if it exists
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            self.dimension = self.index.d 
            self._load_mappings()
        
    
    def _load_mappings(self):
        """Load ID mappings from file"""
        if os.path.exists(self.mapping_path):
            try:
                with open(self.mapping_path, 'r') as f:
                    mapping_data = json.load(f)
                    self.id_map = {int(k): v for k, v in mapping_data.items()}
            except Exception as e:
                print(f"Error loading mappings: {e}")
                self.id_map = {}
    
    def _save_mappings(self):
        """Save ID mappings to file"""
        try:
            with open(self.mapping_path, 'w') as f:
                json.dump(self.id_map, f, indent=2)
        except Exception as e:
            print(f"Error saving mappings: {e}")
    
    def add_vector(self, vector: np.ndarray, chunk_id: str):
        """Add a vector to the index and update mappings"""
        vector = vector.reshape(1, -1)
        current_dim = vector.shape[1]
        
        if self.index is None:
            self.dimension = current_dim
            self.index = faiss.IndexFlatL2(self.dimension)
            print(f"Created new index with dimension: {self.dimension}")
        else:
            if current_dim != self.dimension:
                raise ValueError(f"Vector dimension {current_dim} does not match index dimension {self.dimension}")
        
        idx = self.index.ntotal
        self.index.add(vector)
        self.id_map[idx] = chunk_id
        self._save_mappings()
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar vectors in the index"""
        if self.index is None:
            return []
            
        query_vector = query_vector.reshape(1, -1)
        
       
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self.dimension}")
        
        # Search more results than needed to account for missing mappings
        search_k = min(k * 3, self.index.ntotal)
        distances, indices = self.index.search(query_vector, search_k)
        
        results = []
        seen_chunks = set() 
        
        for i, distance in zip(indices[0], distances[0]):
            if i in self.id_map and i >= 0:  # Check for valid index
                chunk_id = self.id_map[i]
                
                # Skip if we've already seen this chunk
                if chunk_id in seen_chunks:
                    continue
                    
                results.append((chunk_id, float(distance)))
                seen_chunks.add(chunk_id)
                
                if len(results) >= k:  # Stop when we have enough results
                    break
        
        return results
    
    def update_vector(self, chunk_id: str, new_vector: np.ndarray):
        """Update a vector in the index"""
        idx_to_update = None
        for idx, cid in self.id_map.items():
            if cid == chunk_id:
                idx_to_update = idx
                break
        
        if idx_to_update is not None:
            self.add_vector(new_vector, chunk_id)
    
    def delete_vector(self, chunk_id: str):
        """Delete a vector from the index"""
        idx_to_remove = None
        for idx, cid in list(self.id_map.items()):
            if cid == chunk_id:
                idx_to_remove = idx
                break
        
        if idx_to_remove is not None:
            del self.id_map[idx_to_remove]
            self._save_mappings()

    def get_index_stats(self):
        return {
            "index_size": self.index.ntotal,
            "mappings_count": len(self.id_map)
        }
    
    def export_data(self) -> str:
        """Export the index and mappings as a zip file"""
        faiss.write_index(self.index, self.index_path)
        self._save_mappings()
        
        # Create zip file
        zip_path = "storage/export.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(self.index_path, "index.faiss")
            zipf.write(self.mapping_path, "index.mapping.json")  
            zipf.write("storage/metadata.json", "metadata.json")
        
        print(f"Exported data to {zip_path}")
        return zip_path