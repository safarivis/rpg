import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await fetch('http://localhost:8000/api/character/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error('Failed to create character');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in character creation:', error);
    return NextResponse.json({ error: 'Failed to create character' }, { status: 500 });
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const name = searchParams.get('name');
    
    if (!name) {
      return NextResponse.json({ error: 'Name is required' }, { status: 400 });
    }

    const response = await fetch(`http://localhost:8000/api/character/${name}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch character');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching character:', error);
    return NextResponse.json({ error: 'Failed to fetch character' }, { status: 500 });
  }
}
