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
    if (files && files.length > 0) {
      const file = files[0]
      if (file.type.startsWith('audio/')) {
        setSelectedFile(file)
        setError(null)
      } else {
        setError('Please select an audio file (MP3, WAV, OGG, M4A, etc.)')
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      if (file.type.startsWith('audio/')) {
        setSelectedFile(file)
        setError(null)
      } else {
        setError('Please select an audio file (MP3, WAV, OGG, M4A, etc.)')
      }
    }
  }

  const transcribeAudio = async () => {
    if (!selectedFile) {
      setError('Please select an audio file first')
      return
    }

    setIsLoading(true)
    setError(null)
    setTranscriptionResult(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      console.log('🚀 Starting transcription request...')
      
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData,
      })

      const result = await response.json()

      if (response.ok) {
        setTranscriptionResult(result)
        console.log('✅ Transcription successful:', result)
      } else {
        throw new Error(result.error || 'Transcription failed')
      }
    } catch (error) {
      console.error('❌ Transcription error:', error)
      setError(`Transcription failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  const clearFile = () => {
    setSelectedFile(null)
    setTranscriptionResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8 text-white">
          <h1 className="text-4xl font-bold mb-2">🎯 AI Transcription Service</h1>
          <p className="text-xl text-white/80">Upload audio files and get accurate transcriptions powered by Whisper AI</p>
        </div>

        {/* Navigation Options */}
        <div className="flex justify-center space-x-4 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-1 flex space-x-1">
            <div className="bg-white/20 text-white px-4 py-2 rounded-lg font-semibold flex items-center space-x-2">
              <Upload className="w-4 h-4" />
              <span>File Upload</span>
            </div>
            <a 
              href="/record"
              className="text-white/70 hover:text-white hover:bg-white/10 px-4 py-2 rounded-lg transition-all flex items-center space-x-2"
            >
              <Mic className="w-4 h-4" />
              <span>Voice Recording</span>
            </a>
          </div>
        </div>

        {/* File Upload Area */}
        <div
          className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
            isDragOver
              ? 'border-blue-400 bg-blue-500/10'
              : 'border-white/30 bg-white/5 hover:bg-white/10'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <div className="space-y-4">
            <FileAudio className="mx-auto h-16 w-16 text-white/60" />
            <div className="text-white">
              <h3 className="text-lg font-semibold mb-2">
                {selectedFile ? 'File Selected' : 'Upload Audio File'}
              </h3>
              {selectedFile ? (
                <div className="space-y-2">
                  <p className="text-blue-200 font-medium">{selectedFile.name}</p>
                  <p className="text-white/60">
                    Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <button
                    onClick={clearFile}
                    className="text-red-400 hover:text-red-300 underline"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <div>
                  <p className="text-white/80 mb-4">
                    Drag and drop an audio file here, or click to browse
                  </p>
                  <p className="text-white/60 text-sm">
                    Supports: MP3, WAV, OGG, M4A, MP4, and more
                  </p>
                </div>
              )}
            </div>
            {!selectedFile && (
              <div>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg cursor-pointer transition-colors font-semibold"
                >
                  Choose File
                </label>
              </div>
            )}
          </div>
        </div>

        {/* Transcribe Button */}
        {selectedFile && (
          <div className="text-center mt-8">
            <button
              onClick={transcribeAudio}
              disabled={isLoading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-8 py-4 rounded-xl font-semibold transition-colors text-lg flex items-center space-x-2 mx-auto"
            >
              {isLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <FileAudio className="w-6 h-6" />
              )}
              <span>{isLoading ? 'Transcribing...' : '🚀 Start Transcription'}</span>
            </button>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-6 bg-red-500/20 border border-red-500/50 rounded-xl p-4">
            <div className="flex items-center space-x-2 text-red-200">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Results */}
        {transcriptionResult && (
          <div className="mt-8 bg-white/10 backdrop-blur-lg rounded-2xl p-8">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="w-6 h-6 text-green-400" />
              <h3 className="text-xl font-semibold text-white">Transcription Result</h3>
            </div>
            
            <div className="bg-white/5 rounded-xl p-6 mb-4">
              <p className="text-lg text-white leading-relaxed">
                {transcriptionResult.text}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm text-white/70">
              <div>
                <span className="font-semibold">Confidence:</span>{' '}
                <span className={`${transcriptionResult.confidence > 0.9 ? 'text-green-400' : transcriptionResult.confidence > 0.7 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {(transcriptionResult.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div>
                <span className="font-semibold">Language:</span>{' '}
                <span>{transcriptionResult.language || 'auto-detected'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Features */}
        <div className="mt-12 grid md:grid-cols-3 gap-6 text-white">
          <div className="bg-white/5 rounded-xl p-6 text-center">
            <FileAudio className="w-8 h-8 mx-auto mb-3 text-blue-400" />
            <h4 className="font-semibold mb-2">Multiple Formats</h4>
            <p className="text-white/70 text-sm">
              Support for MP3, WAV, OGG, M4A, and many other audio formats
            </p>
          </div>
          <div className="bg-white/5 rounded-xl p-6 text-center">
            <CheckCircle className="w-8 h-8 mx-auto mb-3 text-green-400" />
            <h4 className="font-semibold mb-2">High Accuracy</h4>
            <p className="text-white/70 text-sm">
              Powered by OpenAI Whisper for industry-leading transcription accuracy
            </p>
          </div>
          <div className="bg-white/5 rounded-xl p-6 text-center">
            <Mic className="w-8 h-8 mx-auto mb-3 text-purple-400" />
            <h4 className="font-semibold mb-2">Real-time Recording</h4>
            <p className="text-white/70 text-sm">
              Record directly from your microphone and get instant transcriptions
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
