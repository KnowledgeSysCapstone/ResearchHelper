/**
 * Generic API fetch wrapper.
 * @param path Path to route. e.g. '/api/search/vector' or '/api/search/doi/' 
 * @param options - Fetch API options (method, headers, body, etc).
 * https://developer.mozilla.org/en-US/docs/Web/API/RequestInit
 * @returns The parsed JSON response.
 * @throws Error on network failure.
 */
async function queryAPI<T>(path: string, options: RequestInit = {}): Promise<T> {
  // Try + Catch to generally catch network errors.
  try {
    // Store the response from fetch.
    const response = await fetch(path, {
      ...options,
      // Always use this header.
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    // If the response isn't ok (boolean indicating success).
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    // Return the response as json.
    return await response.json();
  } catch (err) {
    console.error('API component [queryAPI] error: ', err);
    throw err;
  }
}

/**
 * Vector search fetch.
 * @param text Search text.
 * @param topK - Number of hits returned.
 * @returns The parsed JSON response.results.
 */
export async function vectorSearchAPI(text: string, topK: number = 10) {
  // Utilize the Vector Search route:
  const response = await queryAPI<{ results: any[] }>('/api/search/vector', {
    method: 'POST',
    // Set body as input params.
    body: JSON.stringify({
      text: text,
      top_k: topK
    }),
  });
  return response.results;
}