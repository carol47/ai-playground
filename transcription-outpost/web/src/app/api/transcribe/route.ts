import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  console.log('🚀 [API Route] Transcription request received')
  
  try {
    // Get the form data from the request
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      console.error('❌ [API Route] No file provided in request')
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    console.log('📁 [API Route] File details:', {
      name: file.name,
      type: file.type,
      size: file.size
    })

    // Create a new FormData to send to FastAPI
    const backendFormData = new FormData()
    backendFormData.append('file', file)

    console.log('📤 [API Route] Sending request to FastAPI backend...')
    
    // Make request to FastAPI backend
    const rawUrl = process.env.FASTAPI_URL || 'http://localhost:8000'
    console.log('🔍 [API Route] Raw FASTAPI_URL:', JSON.stringify(rawUrl))
    const fastApiUrl = rawUrl.trim()
    console.log('🔍 [API Route] Trimmed FASTAPI_URL:', JSON.stringify(fastApiUrl))
    const fullUrl = `${fastApiUrl}/api/v1/transcription/`
    const startTime = Date.now()
    
    console.log('🔗 [API Route] Backend URL:', JSON.stringify(fullUrl))
    
    const response = await fetch(fullUrl, {
      method: 'POST',
      body: backendFormData,
    })

    const endTime = Date.now()
    const requestTime = endTime - startTime

    console.log('📨 [API Route] FastAPI response received:', {
      status: response.status,
      statusText: response.statusText,
      requestTime: `${requestTime}ms`,
      headers: Object.fromEntries(response.headers.entries())
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ [API Route] FastAPI error response:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      })
      
      return NextResponse.json(
        { 
          error: `Transcription failed: ${response.status} ${response.statusText}`,
          details: errorText,
          fastApiError: true
        },
        { status: response.status }
      )
    }

    // Parse the successful response
    const result = await response.json()
    console.log('✅ [API Route] Transcription successful:', {
      textLength: result.text?.length || 0,
      confidence: result.confidence,
      processingTime: result.processing_time,
      language: result.language
    })

    // Return the result to the frontend
    return NextResponse.json(result)

  } catch (error) {
    console.error('💥 [API Route] Unexpected error:', error)
    
    if (error instanceof Error) {
      return NextResponse.json(
        { 
          error: 'Internal server error',
          details: error.message,
          stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
        },
        { status: 500 }
      )
    }

    return NextResponse.json(
      { error: 'Unknown error occurred' },
      { status: 500 }
    )
  }
} 