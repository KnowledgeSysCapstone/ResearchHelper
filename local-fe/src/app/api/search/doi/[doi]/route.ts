import { NextResponse } from 'next/server';

// API Base URL - Use service name in Docker environment
const API_BASE_URL = 'http://backend:8000';

export async function GET(
  request: Request,
  { params }: { params: { doi: string } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const size = searchParams.get('size') || '10';
    
    const response = await fetch(
      `${API_BASE_URL}/search/doi/${encodeURIComponent(params.doi)}?size=${size}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`Backend API responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in DOI search API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from backend' },
      { status: 500 }
    );
  }
} 