# backend/metadata_store.py
import json
import os

class MetadataStore:
    def __init__(self, metadata_path: str):
        self.metadata_path = metadata_path
        self.metadata = {}
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
    
    def add_chunk(self, chunk_id: str, metadata: dict):
        self.metadata[chunk_id] = metadata
        self._save()
    
    def get_chunk(self, chunk_id: str) -> dict:
        return self.metadata.get(chunk_id, {})
    
    def update_chunk(self, chunk_id: str, metadata: dict):
        if chunk_id in self.metadata:
            self.metadata[chunk_id] = metadata
            self._save()
    
    def delete_chunk(self, chunk_id: str):
        if chunk_id in self.metadata:
            del self.metadata[chunk_id]
            self._save()
    
    def _save(self):
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)