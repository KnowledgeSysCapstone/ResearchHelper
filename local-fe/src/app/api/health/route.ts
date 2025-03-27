import { NextResponse } from 'next/server';

// API基础URL - 在Docker环境中使用服务名称
const API_BASE_URL = 'http://backend:8000';

export async function GET() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Backend API responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in health API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from backend', status: 'error' },
      { status: 500 }
    );
  }
} 