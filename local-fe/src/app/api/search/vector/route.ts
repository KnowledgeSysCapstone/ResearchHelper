import { NextResponse } from 'next/server';

// API Base URL - Use service name in Docker environment
const API_BASE_URL = 'http://backend:8000';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    console.log("Frontend API received request body:", body);
    
    const response = await fetch(`${API_BASE_URL}/search/vector`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend API response error ${response.status}:`, errorText);
      throw new Error(`Backend API responded with status: ${response.status}, body: ${errorText}`);
    }
    
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