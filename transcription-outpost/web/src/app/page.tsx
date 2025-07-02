'use client'

import React, { useState, useCallback } from 'react'
import { Upload, Mic, FileAudio, Loader2, CheckCircle, AlertCircle } from 'lucide-react'

interface TranscriptionResult {
  text: string
  confidence: number
  language?: string
  processing_time?: number
}

export default function TranscriptionApp() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [transcriptionResult, setTranscriptionResult] = useState<TranscriptionResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = e.dataTransfer.files
    if (files && files[0]) {
      const file = files[0]
      if (isAudioFile(file)) {
        setSelectedFile(file)
        setError(null)
        setTranscriptionResult(null)
      } else {
        setError('Please select a valid audio file (MP3, WAV, OGG, M4A, MP4)')
      }
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (isAudioFile(file)) {
        setSelectedFile(file)
        setError(null)
        setTranscriptionResult(null)
      } else {
        setError('Please select a valid audio file (MP3, WAV, OGG, M4A, MP4)')
      }
    }
  }, [])

  const isAudioFile = (file: File): boolean => {
    const audioTypes = [
      'audio/mpeg', 
      'audio/wav', 
      'audio/wave', 
      'audio/x-wav',
      'audio/ogg', 
      'audio/mp4', 
      'audio/m4a',
      'audio/x-m4a'
    ]
    return audioTypes.includes(file.type) || 
           /\.(mp3|wav|ogg|m4a|mp4)$/i.test(file.name)
  }

  const transcribeAudio = async () => {
    if (!selectedFile) {
      setError('Please select an audio file first')
      return
    }

    console.log('🎵 [Frontend] Starting transcription for:', selectedFile.name)
    setIsLoading(true)
    setError(null)
    setTranscriptionResult(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      console.log('📤 [Frontend] Sending request to Next.js API route...')
      const startTime = Date.now()

      // Call our Next.js API route instead of FastAPI directly
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData,
      })

      const endTime = Date.now()
      const requestTime = endTime - startTime

      console.log('📨 [Frontend] API response received:', {
        status: response.status,
        requestTime: `${requestTime}ms`
      })

      const result = await response.json()

      if (!response.ok) {
        console.error('❌ [Frontend] API error:', result)
        throw new Error(result.error || 'Transcription failed')
      }

      console.log('✅ [Frontend] Transcription successful!', result)
      setTranscriptionResult(result)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
      console.error('💥 [Frontend] Transcription error:', err)
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const resetForm = () => {
    setSelectedFile(null)
    setTranscriptionResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Mic className="h-12 w-12 text-white mr-4" />
            <h1 className="text-4xl font-bold text-white">
              Transcription Outpost
            </h1>
          </div>
          <p className="text-xl text-purple-100">
            Transform your audio into text with AI precision
          </p>
        </div>

        {/* Main Card */}
        <div className="max-w-4xl mx-auto bg-white/10 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-8">
          
          {/* File Upload Area */}
          <div 
            className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 mb-8 ${
              isDragOver 
                ? 'border-yellow-400 bg-yellow-400/10' 
                : selectedFile 
                  ? 'border-green-400 bg-green-400/10'
                  : 'border-white/30 hover:border-white/50 hover:bg-white/5'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <div className="flex flex-col items-center space-y-6">
              {selectedFile ? (
                <>
                  <FileAudio className="h-16 w-16 text-green-400" />
                  <div className="text-white">
                    <p className="text-lg font-semibold">{selectedFile.name}</p>
                    <p className="text-sm opacity-75">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <Upload className="h-16 w-16 text-white/60" />
                  <div className="text-white">
                    <p className="text-xl font-semibold mb-2">
                      Drop your audio file here
                    </p>
                    <p className="text-sm opacity-75 mb-4">
                      Support for MP3, WAV, OGG, M4A, MP4 files
                    </p>
                  </div>
                </>
              )}
              
              <label className="cursor-pointer bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-xl font-medium transition-all duration-200 inline-flex items-center space-x-2">
                <Upload className="h-5 w-5" />
                <span>{selectedFile ? 'Change File' : 'Browse Files'}</span>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <button
              onClick={transcribeAudio}
              disabled={!selectedFile || isLoading}
              className={`flex-1 py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-200 flex items-center justify-center space-x-3 ${
                !selectedFile || isLoading
                  ? 'bg-gray-500/50 text-gray-300 cursor-not-allowed'
                  : 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02]'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-6 w-6 animate-spin" />
                  <span>Transcribing...</span>
                </>
              ) : (
                <>
                  <Mic className="h-6 w-6" />
                  <span>🚀 Start Transcription</span>
                </>
              )}
            </button>

            {(selectedFile || transcriptionResult || error) && (
              <button
                onClick={resetForm}
                className="px-6 py-4 bg-white/20 hover:bg-white/30 text-white rounded-xl font-medium transition-all duration-200"
              >
                Reset
              </button>
            )}
          </div>

          {/* Results */}
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-6 mb-6">
              <div className="flex items-center space-x-3">
                <AlertCircle className="h-6 w-6 text-red-400 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-red-300 mb-2">Error</h3>
                  <p className="text-red-200">{error}</p>
                </div>
              </div>
            </div>
          )}

          {transcriptionResult && (
            <div className="bg-green-500/20 border border-green-500/50 rounded-xl p-6">
              <div className="flex items-start space-x-3 mb-4">
                <CheckCircle className="h-6 w-6 text-green-400 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="font-semibold text-green-300 mb-2">
                    Transcription Complete!
                  </h3>
                  
                  {/* Transcribed Text */}
                  <div className="bg-black/20 rounded-lg p-4 mb-4">
                    <p className="text-white text-lg leading-relaxed">
                      "{transcriptionResult.text}"
                    </p>
                  </div>

                  {/* Metadata */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                    <div className="text-center p-3 bg-white/10 rounded-lg">
                      <p className="text-green-300 font-semibold">Confidence</p>
                      <p className="text-white">
                        {(transcriptionResult.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                    {transcriptionResult.language && (
                      <div className="text-center p-3 bg-white/10 rounded-lg">
                        <p className="text-green-300 font-semibold">Language</p>
                        <p className="text-white">{transcriptionResult.language}</p>
                      </div>
                    )}
                    {transcriptionResult.processing_time && (
                      <div className="text-center p-3 bg-white/10 rounded-lg">
                        <p className="text-green-300 font-semibold">Processing Time</p>
                        <p className="text-white">
                          {transcriptionResult.processing_time.toFixed(2)}s
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-purple-200">
          <p>Powered by Whisper AI • Built with Next.js & FastAPI</p>
        </div>
      </div>
    </div>
  )
}
