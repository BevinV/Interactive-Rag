from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from config import EMBEDDING_MODELS

# Global model cache
model_cache = {}

def get_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    global model_cache
    
    if model_name not in model_cache:
        print(f"Loading model: {model_name}")
        model_cache[model_name] = SentenceTransformer(model_name, device='cpu')
    
    model = model_cache[model_name]
    return model.encode(texts)

def get_available_models():
    return EMBEDDING_MODELS