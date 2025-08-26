EMBEDDING_MODELS = {
    "all-MiniLM-L6-v2": {
        "name": "all-MiniLM-L6-v2",
        "dimensions": 384,
        "description": "Fast and efficient model for general purpose embedding"
    },
    "all-mpnet-base-v2": {
        "name": "all-mpnet-base-v2", 
        "dimensions": 768,
        "description": "Higher quality model with better performance but slower"
    },
    "multi-qa-MiniLM-L6-cos-v1": {
        "name": "multi-qa-MiniLM-L6-cos-v1",
        "dimensions": 384,
        "description": "Optimized for question answering tasks"
    }
}

CHUNKING_METHODS = {
    "fixed_size": {
        "name": "Fixed Size Chunks",
        "description": "Split text into fixed size chunks with optional overlap"
    },
    "sentence_aware": {
        "name": "Sentence Aware Chunks", 
        "description": "Split text at sentence boundaries for more coherent chunks"
    },
    "paragraph_aware": {
        "name": "Paragraph Aware Chunks",
        "description": "Split text at paragraph boundaries"
    },
    "recursive_character": {
        "name": "Recursive Character Text Splitter",
        "description": "Recursively split text using different separators"
    }
}