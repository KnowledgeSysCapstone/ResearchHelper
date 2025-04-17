// api/queryAPI, utilized by all routes to make requests to backend.
// Defaults to expected docker container address if not set in .env.

const API_BASE_URL = process.env.BACKEND_URL || 'http://backend:8000';

// Generalized API call to access fastAPI.
export async function queryAPI<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Backend error ${response.status}: ${errorText}`);
  }

  return await response.json();
}

export async function vectorSearchAPI(text: string, topK: number = 10) {
  try {
    const response = await queryAPI<{ results: any[] }>('/api/search/vector', {
      method: 'POST',
      body: JSON.stringify({
        text: text,
        top_k: topK
      }),
    });

    return response.results; // Assuming response contains 'results'
  } catch (error) {
    console.error('Error during vector search API call:', error);
    throw error;
  }
}

export async function searchByDOI(doi: string, size: number = 10) {
  try {
    const response = await queryAPI<{ results: any[] }>(`/api/search/doi/${encodeURIComponent(doi)}?size=${size}`, {
      method: 'GET',
    });

    return response.results; // Assuming response contains 'results'
  } catch (error) {
    console.error('Error during DOI search API call:', error);
    throw error;
  }
}
