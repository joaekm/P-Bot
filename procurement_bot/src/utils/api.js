/**
 * API utility för att hantera anrop till backend
 * Använder VITE_API_URL i produktion, fallback till relativ URL i dev
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Wrapper för fetch som hanterar API base URL
 * Används för JSON-anrop med Content-Type: application/json
 */
export const apiFetch = async (endpoint, options = {}) => {
  const url = API_BASE_URL 
    ? `${API_BASE_URL}${endpoint}` 
    : endpoint; // Fallback till relativ URL (använder Vite proxy i dev)
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
};

/**
 * För FormData-uploads (behåller Content-Type som undefined så browser sätter boundary)
 */
export const apiFetchFormData = async (endpoint, formData) => {
  const url = API_BASE_URL 
    ? `${API_BASE_URL}${endpoint}` 
    : endpoint;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      // Inga headers här - låt browser sätta Content-Type med boundary
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return response;
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
};

