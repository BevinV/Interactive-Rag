from fastapi import FastAPI, File, UploadFile, HTTPException, Body, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
from pydantic import BaseModel
import faiss 
import tempfile
import zipfile
import shutil
import os
from typing import List
import json
import uuid
from datetime import datetime


from ingestion import process_pdf, get_available_chunking_methods
from embeddings import get_embeddings, get_available_models
from index_manager import IndexManager
from metadata_store import MetadataStore
from config import EMBEDDING_MODELS, CHUNKING_METHODS

app = FastAPI(title="Interactive RAG Backend")

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

class QueryRequest(BaseModel):
    query: str
    k: int = 5


class UpdateChunkRequest(BaseModel):
    new_text: str


class IngestRequest(BaseModel):
    model_name: str = "all-MiniLM-L6-v2"
    chunking_method: str = "fixed_size"
    chunk_size: int = 500
    chunk_overlap: int = 50



vector_stores = {}


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
index_manager = IndexManager("storage/index.faiss")
metadata_store = MetadataStore("storage/metadata.json")

@app.post("/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    model_name: str = Form("all-MiniLM-L6-v2"),
    chunking_method: str = Form("fixed_size"),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(50)
):
    try:
        print(f"Processing file: {file.filename} with model: {model_name}, chunking: {chunking_method}")
        
        # Check if we already have an index with a different model
        if index_manager.index is not None and index_manager.index.ntotal > 0:
            if metadata_store.metadata:
                first_chunk_id = next(iter(metadata_store.metadata))
                existing_model = metadata_store.metadata[first_chunk_id].get("model", "all-MiniLM-L6-v2")
                
                if existing_model != model_name:
                    error_msg = f"Cannot use model '{model_name}'. Index already contains documents embedded with '{existing_model}'. Please reset the index to use a different model."
                    print(error_msg)
                    raise HTTPException(status_code=400, detail=error_msg)
        
        # Save uploaded file
        file_path = f"storage/docs/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        print(f"File saved to: {file_path}")
        
        # Process PDF with selected chunking method
        chunks = process_pdf(
            file_path, 
            chunking_method=chunking_method,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        print(f"Extracted {len(chunks)} chunks from PDF using {chunking_method}")
        
        # Generate embeddings with selected model
        texts = [chunk["text"] for chunk in chunks]
        print(f"Generating embeddings using {model_name}...")
        embeddings = get_embeddings(texts, model_name)
        print(f"Generated {len(embeddings)} embeddings")
        
        # Add to index and metadata
        chunk_ids = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{file.filename}_{i}"
            
            try:
                index_manager.add_vector(embedding, chunk_id)
            except ValueError as e:
                if "dimension" in str(e):
                    error_msg = f"Dimension mismatch: {e}. Please reset the index to use a different embedding model."
                    print(error_msg)
                    raise HTTPException(status_code=400, detail=error_msg)
                else:
                    raise
            
            metadata_store.add_chunk(chunk_id, {
                "document": file.filename,
                "page": chunk["page"],
                "text": chunk["text"],
                "start_index": chunk["start_index"],
                "model": model_name,
                "chunking_method": chunking_method
            })
            chunk_ids.append(chunk_id)
        
        print(f"Successfully ingested {len(chunk_ids)} chunks")
        return {"message": "File ingested successfully", "chunk_ids": chunk_ids}
    
    except Exception as e:
        print(f"Error in ingest_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_documents(request: QueryRequest):
    try:
        query = request.query
        k = request.k
        
        print(f"Received query: '{query}' with k={k}")
        
        # Get the model used for the index from metadata
        if not metadata_store.metadata:
            raise HTTPException(status_code=400, detail="No documents indexed yet")
            
        # Get the model from the first chunk's metadata
        first_chunk_id = next(iter(metadata_store.metadata))
        model_name = metadata_store.metadata[first_chunk_id].get("model", "all-MiniLM-L6-v2")
        
        print(f"Using model '{model_name}' for query embedding")
        
        # Embed query using the same model that was used for indexing
        query_embedding = get_embeddings([query], model_name)[0]
        
        # Search index
        results = index_manager.search(query_embedding, k)
        
        # Get metadata for results
        enriched_results = []
        for chunk_id, score in results:
            metadata = metadata_store.get_chunk(chunk_id)
            if metadata:  # Only add if metadata exists
                enriched_results.append({
                    "chunk_id": chunk_id,
                    "score": score,
                    "text": metadata["text"],
                    "document": metadata["document"],
                    "page": metadata["page"],
                    "start_index": metadata["start_index"],
                    "model": metadata.get("model", "unknown"),
                    "chunking_method": metadata.get("chunking_method", "unknown")
                })
        
        print(f"Returning {len(enriched_results)} results")
        return {"results": enriched_results}
    
    except Exception as e:
        print(f"Error in query_documents: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/available_models")
async def get_available_embedding_models():
    return get_available_models()


@app.get("/available_chunking_methods")
async def get_available_chunking_methods_endpoint():
    return get_available_chunking_methods()


@app.post("/update_chunk/{chunk_id}")
async def update_chunk(chunk_id: str, request: UpdateChunkRequest):
    try:
        new_text = request.new_text
        
        # Get the current metadata to find which model was used
        metadata = metadata_store.get_chunk(chunk_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        model_name = metadata.get("model", "all-MiniLM-L6-v2")
        print(f"Updating chunk {chunk_id} using model {model_name}")
        
        # Update metadata
        metadata["text"] = new_text
        metadata_store.update_chunk(chunk_id, metadata)
        
        # Re-embed using the same model that was originally used
        new_embedding = get_embeddings([new_text], model_name)[0]
        index_manager.update_vector(chunk_id, new_embedding)
        
        return {"message": "Chunk updated successfully"}
    
    except Exception as e:
        print(f"Error in update_chunk: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_chunk/{chunk_id}")
async def delete_chunk(chunk_id: str):
    try:
        metadata_store.delete_chunk(chunk_id)
        index_manager.delete_vector(chunk_id)
        return {"message": "Chunk deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export")
async def export_data():
    try:
        # Create zip file with index and metadata
        export_path = index_manager.export_data()
        return FileResponse(export_path, media_type="application/zip")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/index_status")
async def index_status():
    """Get information about the current index state"""
    return index_manager.get_index_stats()

@app.post("/fix_mappings")
async def fix_mappings():
    """Fix mismatched ID mappings between index and metadata"""
    try:
        # Get current stats
        stats_before = index_manager.get_index_stats()
        
        # Rebuild mappings from metadata
        rebuilt_count = index_manager.rebuild_mappings_from_metadata(metadata_store)
        
        # Get stats after fix
        stats_after = index_manager.get_index_stats()
        
        return {
            "message": f"Mappings rebuilt for {rebuilt_count} chunks",
            "stats_before": stats_before,
            "stats_after": stats_after
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset_index")
async def reset_index():
    try:
        # Delete index files
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
        
        # Reinitialize the index manager
        global index_manager
        index_manager = IndexManager("storage/index.faiss")
        
        # Reinitialize the metadata store
        global metadata_store
        metadata_store = MetadataStore("storage/metadata.json")
        
        return {"message": "Index reset successfully. You can now use a different embedding model."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/health")
async def health_check():
    """Check the health of the index and mappings"""
    stats = index_manager.get_index_stats()
    metadata_count = len(metadata_store.metadata)
    
    # Check for consistency
    index_size = stats["index_size"]
    mappings_count = stats["mappings_count"]
    is_consistent = index_size == mappings_count == metadata_count
    
    return {
        "status": "healthy" if is_consistent else "inconsistent",
        "index_size": index_size,
        "mappings_count": mappings_count,
        "metadata_count": metadata_count,
        "is_consistent": is_consistent
    }


@app.post("/test_export")
async def test_export(file: UploadFile = File(...), query: str = Body(...), k: int = Body(5)):
    try:
        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded zip file
            zip_path = os.path.join(temp_dir, "uploaded_export.zip")
            with open(zip_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"Files in export zip: {file_list}")
                zip_ref.extractall(temp_dir)
            
            # Check for required files with different possible names
            extracted_index_path = os.path.join(temp_dir, "index.faiss")
            
            # Check for mapping file with different possible names
            mapping_names = ["index.mapping.json", "mappings.json"]
            extracted_mapping_path = None
            for name in mapping_names:
                path = os.path.join(temp_dir, name)
                if os.path.exists(path):
                    extracted_mapping_path = path
                    break
            
            extracted_metadata_path = os.path.join(temp_dir, "metadata.json")
            
            # Check if all required files exist
            missing_files = []
            if not os.path.exists(extracted_index_path):
                missing_files.append("index.faiss")
            if not extracted_mapping_path:
                missing_files.append("mapping file (index.mapping.json or mappings.json)")
            if not os.path.exists(extracted_metadata_path):
                missing_files.append("metadata.json")
            
            if missing_files:
                error_msg = f"Export zip is missing required files: {', '.join(missing_files)}. Found files: {file_list}"
                print(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Load the index
            index = faiss.read_index(extracted_index_path)
            
            # Load mappings
            with open(extracted_mapping_path, 'r') as f:
                mappings = json.load(f)
                # Convert string keys to integers
                mappings = {int(k): v for k, v in mappings.items()}
            
            # Load metadata
            with open(extracted_metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Determine which model was used for the index by checking the first chunk's metadata
            model_name = "all-MiniLM-L6-v2"  # Default fallback
            if metadata:
                first_chunk_id = next(iter(metadata))
                model_name = metadata[first_chunk_id].get("model", "all-MiniLM-L6-v2")
            
            print(f"Using model '{model_name}' for query embedding in test export")
            
            # Embed query using the same model that was used for the index
            query_embedding = get_embeddings([query], model_name)[0]
            
            # Check if the query vector dimension matches the index dimension
            if query_embedding.shape[0] != index.d:
                error_msg = f"Query vector dimension {query_embedding.shape[0]} does not match index dimension {index.d}. Please use the same model that was used to create the index."
                print(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Search in the extracted index
            query_vector = query_embedding.reshape(1, -1)
            
            # Search more results than needed to account for duplicates
            search_k = min(k * 3, index.ntotal)
            distances, indices = index.search(query_vector, search_k)
            
            # Get metadata for results with deduplication
            enriched_results = []
            seen_chunks = set()  
            
            for i, distance in zip(indices[0], distances[0]):
                if i in mappings and i >= 0:  
                    chunk_id = mappings[i]
                    
                    if chunk_id in seen_chunks:
                        continue
                        
                    if chunk_id in metadata:
                        result_data = {
                            "chunk_id": chunk_id,
                            "score": float(distance),
                            "text": metadata[chunk_id]["text"],
                            "document": metadata[chunk_id]["document"],
                            "page": metadata[chunk_id]["page"],
                            "start_index": metadata[chunk_id]["start_index"],
                            "model": metadata[chunk_id].get("model", "unknown"),
                            "chunking_method": metadata[chunk_id].get("chunking_method", "unknown")
                        }
                        enriched_results.append(result_data)
                        seen_chunks.add(chunk_id)
                        
                        if len(enriched_results) >= k:  
                            break
            
            return {"results": enriched_results}
    
    except Exception as e:
        print(f"Error in test_export: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_vector_store")
async def upload_vector_store(
    file: UploadFile = File(...),
    model_name: str = Form("all-MiniLM-L6-v2")
):
    try:
        # Create a directory for external vector stores
        vector_store_id = str(uuid.uuid4())
        store_dir = f"storage/vector_stores/{vector_store_id}"
        os.makedirs(store_dir, exist_ok=True)
        
        # Save the uploaded zip file
        zip_path = f"{store_dir}/uploaded.zip"
        with open(zip_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(store_dir)
        
        # Check if the required files exist
        extracted_index_path = f"{store_dir}/index.faiss"
        extracted_metadata_path = f"{store_dir}/metadata.json"
        extracted_mapping_path = f"{store_dir}/index.mapping.json"
        
        # Check for mapping file with alternative names
        if not os.path.exists(extracted_mapping_path):
            alt_mapping_path = f"{store_dir}/mappings.json"
            if os.path.exists(alt_mapping_path):
                extracted_mapping_path = alt_mapping_path
            else:
                shutil.rmtree(store_dir)
                raise HTTPException(status_code=400, detail="Vector store must contain index.faiss, metadata.json, and a mapping file")
        
        if not os.path.exists(extracted_index_path) or not os.path.exists(extracted_metadata_path):
            shutil.rmtree(store_dir)
            raise HTTPException(status_code=400, detail="Vector store must contain index.faiss and metadata.json")
        
        # Store the vector store information
        vector_stores[vector_store_id] = {
            "model_name": model_name,
            "store_dir": store_dir,
            "index_path": extracted_index_path,
            "metadata_path": extracted_metadata_path,
            "mapping_path": extracted_mapping_path,
            "created_at": datetime.now().isoformat()
        }
        
        return {"message": "Vector store uploaded successfully", "vector_store_id": vector_store_id}
    
    except Exception as e:
        print(f"Error in upload_vector_store: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query_vector_store/{vector_store_id}")
async def query_vector_store(
    vector_store_id: str,
    request: QueryRequest
):
    try:
        if vector_store_id not in vector_stores:
            raise HTTPException(status_code=404, detail="Vector store not found")
        
        store_info = vector_stores[vector_store_id]
        query = request.query
        k = request.k
        
        # Load the index, metadata, and mappings for this vector store
        index = faiss.read_index(store_info["index_path"])
        
        with open(store_info["metadata_path"], 'r') as f:
            metadata = json.load(f)
        
        # Load mappings
        with open(store_info["mapping_path"], 'r') as f:
            mappings = json.load(f)
            # Convert string keys to integers
            mappings = {int(k): v for k, v in mappings.items()}
        
        # Embed query using the specified model
        query_embedding = get_embeddings([query], store_info["model_name"])[0]
        
        # Check dimension compatibility
        if query_embedding.shape[0] != index.d:
            error_msg = f"Query vector dimension {query_embedding.shape[0]} does not match index dimension {index.d}. Please select the correct embedding model."
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Search in the vector store index
        query_vector = query_embedding.reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        
        # Get metadata for results using the mappings
        enriched_results = []
        for i, distance in zip(indices[0], distances[0]):
            if i in mappings and i >= 0:  # Check for valid index
                chunk_id = mappings[i]
                if chunk_id in metadata:
                    result_data = {
                        "chunk_id": chunk_id,
                        "score": float(distance),
                        "text": metadata[chunk_id]["text"],
                        "document": metadata[chunk_id]["document"],
                        "page": metadata[chunk_id]["page"],
                        "start_index": metadata[chunk_id]["start_index"],
                        "model": metadata[chunk_id].get("model", "unknown"),
                        "chunking_method": metadata[chunk_id].get("chunking_method", "unknown")
                    }
                    enriched_results.append(result_data)
        
        return {"results": enriched_results, "vector_store_id": vector_store_id}
    
    except Exception as e:
        print(f"Error in query_vector_store: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/update_vector_store_chunk/{vector_store_id}/{chunk_id}")
async def update_vector_store_chunk(
    vector_store_id: str,
    chunk_id: str,
    request: UpdateChunkRequest
):
    try:
        if vector_store_id not in vector_stores:
            raise HTTPException(status_code=404, detail="Vector store not found")
        
        store_info = vector_stores[vector_store_id]
        new_text = request.new_text
        
        # Load metadata
        with open(store_info["metadata_path"], 'r') as f:
            metadata = json.load(f)
        
        if chunk_id not in metadata:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        # Update metadata
        metadata[chunk_id]["text"] = new_text
        
        # Save updated metadata
        with open(store_info["metadata_path"], 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Re-embed using the same model
        new_embedding = get_embeddings([new_text], store_info["model_name"])[0]
        
        # Update the index (this is complex with FAISS - we'd need to implement update functionality)
        # For now, we'll just update the metadata and note that the index is now out of sync
        # In a production system, you'd want to implement proper index updating
        
        return {"message": "Chunk updated successfully (metadata only - index not updated)"}
    
    except Exception as e:
        print(f"Error in update_vector_store_chunk: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list_vector_stores")
async def list_vector_stores():
    return vector_stores


@app.delete("/delete_vector_store/{vector_store_id}")
async def delete_vector_store(vector_store_id: str):
    try:
        if vector_store_id not in vector_stores:
            raise HTTPException(status_code=404, detail="Vector store not found")
        
        # Delete the vector store directory
        store_info = vector_stores[vector_store_id]
        shutil.rmtree(store_info["store_dir"])
        
        # Remove from the stores dictionary
        del vector_stores[vector_store_id]
        
        return {"message": "Vector store deleted successfully"}
    
    except Exception as e:
        print(f"Error in delete_vector_store: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add_to_vector_store/{vector_store_id}")
async def add_to_vector_store(
    vector_store_id: str,
    text: str = Form(...),
    document: str = Form("custom"),
    page: int = Form(1),
    start_index: int = Form(0)
):
    try:
        if vector_store_id not in vector_stores:
            raise HTTPException(status_code=404, detail="Vector store not found")
        
        store_info = vector_stores[vector_store_id]
        
        # Generate embedding for the new text
        embedding = get_embeddings([text], store_info["model_name"])[0]
        
        # Load the existing index
        index = faiss.read_index(store_info["index_path"])
        
        # Load metadata
        with open(store_info["metadata_path"], 'r') as f:
            metadata = json.load(f)
        
        # Load mappings
        with open(store_info["mapping_path"], 'r') as f:
            mappings = json.load(f)
            # Convert string keys to integers
            mappings = {int(k): v for k, v in mappings.items()}
        
        # Add the new vector to the index
        new_index = index.ntotal
        index.add(embedding.reshape(1, -1))
        
        # Create a new chunk ID
        chunk_id = f"{document}_{new_index}"
        
        # Update mappings
        mappings[new_index] = chunk_id
        
        # Update metadata
        metadata[chunk_id] = {
            "text": text,
            "document": document,
            "page": page,
            "start_index": start_index,
            "model": store_info["model_name"],
            "chunking_method": "manual_addition"
        }
        
        # Save updated index, metadata, and mappings
        faiss.write_index(index, store_info["index_path"])
        
        with open(store_info["metadata_path"], 'w') as f:
            json.dump(metadata, f, indent=2)
        
        with open(store_info["mapping_path"], 'w') as f:
            json.dump(mappings, f, indent=2)
        
        return {"message": "Chunk added successfully", "chunk_id": chunk_id}
    
    except Exception as e:
        print(f"Error in add_to_vector_store: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str)


@app.delete("/delete_from_vector_store/{vector_store_id}/{chunk_id}")
async def delete_from_vector_store(vector_store_id: str, chunk_id: str):
    try:
        if vector_store_id not in vector_stores:
            raise HTTPException(status_code=404, detail="Vector store not found")
        
        store_info = vector_stores[vector_store_id]
        
        # Load metadata
        with open(store_info["metadata_path"], 'r') as f:
            metadata = json.load(f)
        
        # Load mappings
        with open(store_info["mapping_path"], 'r') as f:
            mappings = json.load(f)
            mappings = {int(k): v for k, v in mappings.items()}
        
        # Find the index for this chunk ID
        index_to_remove = None
        for idx, cid in mappings.items():
            if cid == chunk_id:
                index_to_remove = idx
                break
        
        if index_to_remove is None:
            raise HTTPException(status_code=404, detail="Chunk not found")
        
        # Remove from metadata and mappings
        if chunk_id in metadata:
            del metadata[chunk_id]
        
        if index_to_remove in mappings:
            del mappings[index_to_remove]
        
        # Save updated metadata and mappings
        with open(store_info["metadata_path"], 'w') as f:
            json.dump(metadata, f, indent=2)
        
        with open(store_info["mapping_path"], 'w') as f:
            json.dump(mappings, f, indent=2)
        
        return {"message": "Chunk deleted successfully"}
    
    except Exception as e:
        print(f"Error in delete_from_vector_store: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export_vector_store/{vector_store_id}")
async def export_vector_store(vector_store_id: str):
    try:
        if vector_store_id not in vector_stores:
            raise HTTPException(status_code=404, detail="Vector store not found")
        
        store_info = vector_stores[vector_store_id]
        
        # Create a zip file with the vector store contents
        zip_path = f"{store_info['store_dir']}/export.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(store_info["index_path"], "index.faiss")
            zipf.write(store_info["mapping_path"], "index.mapping.json")
            zipf.write(store_info["metadata_path"], "metadata.json")
        
        return FileResponse(zip_path, media_type="application/zip", filename=f"vector_store_{vector_store_id}.zip")
    
    except Exception as e:
        print(f"Error in export_vector_store: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)