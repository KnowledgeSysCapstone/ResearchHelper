import { NextResponse } from 'next/server';
import { queryAPI } from '@/api/queryAPI';

export async function GET() {
  try {
    const data = await queryAPI('/health');
    return NextResponse.json(data);
  } catch (error) {
    console.error('Health check error:', error);
    return NextResponse.json({ error: 'Health check failed' }, { status: 500 });
  }
}
