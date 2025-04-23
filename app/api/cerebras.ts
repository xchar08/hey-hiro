import { NextRequest, NextResponse } from 'next/server'
import { Cerebras } from '@cerebras/cerebras_cloud_sdk'

const client = new Cerebras({ apiKey: process.env.NEXT_PUBLIC_CEREBRAS_API_KEY! })

export async function POST(req: NextRequest) {
  const { prompt, max_tokens = 200, temperature = 0.5 } = await req.json()
  if (!prompt) return NextResponse.json({ error: 'Missing prompt' }, { status: 400 })
  try {
    const resp = await client.chat.completions.create({
      model: 'llama-4-scout-17b-16e-instruct',
      messages: [{ role: 'user', content: prompt }],
      max_completion_tokens: max_tokens,
      temperature,
    })
    return NextResponse.json(resp)
  } catch (err: any) {
    console.error(err)
    return NextResponse.json({ error: err.message }, { status: err.status || 500 })
  }
}