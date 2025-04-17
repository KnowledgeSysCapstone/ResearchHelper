import { NextResponse } from 'next/server';
import { queryAPI } from '@/api/queryAPI';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const data = await queryAPI('/search/vector', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return NextResponse.json(data);
  } catch (error) {
    console.error('Vector search error:', error);
    return NextResponse.json({ error: 'Vector search failed' }, { status: 500 });
  }
}
