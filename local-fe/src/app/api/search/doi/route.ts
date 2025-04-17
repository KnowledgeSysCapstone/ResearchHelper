import { NextResponse } from 'next/server';
import { queryAPI } from '@/api/queryAPI';

export async function GET(
  request: Request,
  { params }: { params: { doi: string } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const size = searchParams.get('size') || '10';
    const path = `/search/doi/${encodeURIComponent(params.doi)}?size=${size}`;

    const data = await queryAPI(path);
    return NextResponse.json(data);
  } catch (error) {
    console.error('DOI search error:', error);
    return NextResponse.json({ error: 'DOI search failed' }, { status: 500 });
  }
}
