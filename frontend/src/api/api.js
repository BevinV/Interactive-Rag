import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (formData) => {
  try {
    const response = await api.post('/ingest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading document:', error);
    
    // More detailed error logging
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
    }
    
    throw error;
  }
};


export const queryDocuments = async (query, k = 5) => {
  try {
    console.log("Sending query:", query, "k:", k);
    const response = await api.post('/query', { query, k });
    console.log("Query response:", response.data);
    return response.data;
  } catch (error) {
    console.error('Error querying documents:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      
      // Show a more specific error message for model mismatch
      if (error.response.status === 400 && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
    }
    throw error;
  }
};


export const updateChunk = async (chunkId, newText) => {
  try {
    const response = await api.post(`/update_chunk/${chunkId}`, { new_text: newText });
    return response.data;
  } catch (error) {
    console.error('Error updating chunk:', error);
    throw error;
  }
};

export const deleteChunk = async (chunkId) => {
  try {
    const response = await api.delete(`/delete_chunk/${chunkId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting chunk:', error);
    throw error;
  }
};

export const exportData = async () => {
  try {
    const response = await api.get('/export', {
      responseType: 'blob', // Important for file download
    });
    return response.data;
  } catch (error) {
    console.error('Error exporting data:', error);
    throw error;
  }
};

export const testExport = async (formData) => {
  try {
    const response = await api.post('/test_export', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error testing export:', error);
    throw error;
  }
};

export const resetIndex = async () => {
  try {
    const response = await api.post('/reset_index');
    return response.data;
  } catch (error) {
    console.error('Error resetting index:', error);
    throw error;
  }
};

export const uploadVectorStore = async (formData) => {
  try {
    const response = await api.post('/upload_vector_store', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  } catch (error) {
    console.error('Error uploading vector store:', error);
    throw error;
  }
};

export const queryVectorStore = async (vectorStoreId, query, k = 5) => {
  try {
    console.log(`Querying vector store ${vectorStoreId} with query: ${query}`);
    const response = await api.post(`/query_vector_store/${vectorStoreId}`, { query, k });
    console.log("Vector store query response:", response);
    return response;
  } catch (error) {
    console.error('Error querying vector store:', error);
    if (error.response) {
      console.error('Error response data:', error.response.data);
      console.error('Error response status:', error.response.status);
    }
    throw error;
  }
};


export const updateVectorStoreChunk = async (vectorStoreId, chunkId, newText) => {
  try {
    const response = await api.post(`/update_vector_store_chunk/${vectorStoreId}/${chunkId}`, { new_text: newText });
    return response;
  } catch (error) {
    console.error('Error updating vector store chunk:', error);
    throw error;
  }
};

export const deleteVectorStore = async (vectorStoreId) => {
  try {
    const response = await api.delete(`/delete_vector_store/${vectorStoreId}`);
    return response;
  } catch (error) {
    console.error('Error deleting vector store:', error);
    throw error;
  }
};

export const listVectorStores = async () => {
  try {
    const response = await api.get('/list_vector_stores');
    return response;
  } catch (error) {
    console.error('Error listing vector stores:', error);
    throw error;
  }
};

export const addToVectorStore = async (vectorStoreId, formData) => {
  try {
    const response = await api.post(`/add_to_vector_store/${vectorStoreId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error adding to vector store:', error);
    throw error;
  }
};

export const deleteFromVectorStore = async (vectorStoreId, chunkId) => {
  try {
    const response = await api.delete(`/delete_from_vector_store/${vectorStoreId}/${chunkId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting from vector store:', error);
    throw error;
  }
};

export const exportVectorStore = async (vectorStoreId) => {
  try {
    const response = await api.get(`/export_vector_store/${vectorStoreId}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error exporting vector store:', error);
    throw error;
  }
};


export default api;