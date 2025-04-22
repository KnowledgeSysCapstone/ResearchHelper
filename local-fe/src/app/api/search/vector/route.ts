import { NextResponse } from 'next/server';

// TODO: API Base URL, future .env
const API_BASE_URL = 'http://backend:8000';

/**
 * Handles POST requests for vector search.
 * Forwards the request to the FastAPI backend and returns the response.
 * 
 * @param request - Incoming HTTP request from the front-end client.
 * @returns JSON response from backend or error object.
 */
export async function POST(request: Request) {
  try {
    // Parse JSON requestion.
    const body = await request.json();
    console.log("Frontend API received request body:", body);
    
    // Forward request to FastAPI.
    const response = await fetch(`${API_BASE_URL}/search/vector`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    // If bad response, log it and throw an error.
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend API response error ${response.status}:`, errorText);
      throw new Error(`Backend API responded with status: ${response.status}, body: ${errorText}`);
    }
    
    // Parse and then pack innto NextReponse.json.
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error in vector search API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from backend' },
      { status: 500 }
    );
  }
} 