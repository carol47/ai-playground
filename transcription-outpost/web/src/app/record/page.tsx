'use client'

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Mic, MicOff, Square, Play, Loader2, CheckCircle, AlertCircle, Volume2, Copy, Check } from 'lucide-react'

interface TranscriptionResult {
  text: string
  confidence: number
  language?: string
  processing_time?: number
}

export default function RecordPage() {
  const [isRecording, setIsRecording] = useState(false)
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  const [transcriptionResult, setTranscriptionResult] = useState<TranscriptionResult | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recordingDuration, setRecordingDuration] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null)
  const [isClient, setIsClient] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [isCopied, setIsCopied] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const analyzerRef = useRef<AnalyserNode | null>(null)
  const animationRef = useRef<number | null>(null)

  // Check if we're on client side and detect mobile
  useEffect(() => {
    setIsClient(true)
    setIsMobile(detectMobileDevice())
  }, [])

  const detectMobileDevice = () => {
    if (typeof window === 'undefined') return false
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  }

  // Request microphone permission on component mount
  useEffect(() => {
    if (!isClient) return // Wait for client-side hydration
    
    // Don't auto-request on mobile - wait for user interaction
    if (!isMobile) {
      requestMicrophonePermission()
    }
    return () => {
      cleanup()
    }
  }, [isClient, isMobile])

  const requestMicrophonePermission = async () => {
    try {
      setError(null) // Clear any previous errors
      setHasPermission(null) // Set to loading state
      
      // Check for MediaRecorder support
      if (!window.MediaRecorder) {
        setHasPermission(false)
        setError('Your browser doesn\'t support audio recording. Please try using Chrome, Firefox, or Safari.')
        return
      }
      
      // Check if we're on HTTPS or localhost (including local network IPs for development)
      const isLocalDev = window.location.hostname.includes('localhost') || 
                        window.location.hostname.includes('127.0.0.1') ||
                        window.location.hostname.startsWith('192.168.') ||
                        window.location.hostname.startsWith('10.') ||
                        window.location.hostname.startsWith('172.')
      
      if (window.location.protocol !== 'https:' && !isLocalDev) {
        setHasPermission(false)
        setError('Microphone access requires HTTPS. Please use a secure connection or access via localhost for development.')
        return
      }
      
      console.log('🎤 Requesting microphone permission...', {
        hostname: window.location.hostname,
        protocol: window.location.protocol,
        isLocalDev,
        isMobile
      })
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      })
      
      console.log('✅ Microphone permission granted!')
      setHasPermission(true)
      streamRef.current = stream
      setupAudioAnalyzer(stream)
    } catch (error: any) {
      console.error('❌ Microphone permission error:', error)
      setHasPermission(false)
      
      // Provide specific error messages based on the error type
      if (error.name === 'NotAllowedError') {
        if (isMobile) {
          setError('Microphone access was denied. On mobile devices, please check your browser settings and allow microphone access for this site.')
        } else {
          setError('Microphone access was denied. Please click the microphone icon in your browser\'s address bar to allow access, then try again.')
        }
      } else if (error.name === 'NotFoundError') {
        setError('No microphone found. Please connect a microphone and try again.')
      } else if (error.name === 'NotSupportedError') {
        setError('Your browser doesn\'t support microphone access. Please try using a different browser.')
      } else if (error.name === 'OverconstrainedError') {
        setError('Microphone constraints could not be satisfied. Please try again.')
      } else {
        setError(`Microphone access failed: ${error.message || 'Unknown error'}. Please check your browser settings and try again.`)
      }
    }
  }

  const setupAudioAnalyzer = (stream: MediaStream) => {
    const audioContext = new AudioContext()
    const analyzer = audioContext.createAnalyser()
    const microphone = audioContext.createMediaStreamSource(stream)
    
    analyzer.fftSize = 256
    microphone.connect(analyzer)
    analyzerRef.current = analyzer
    
    updateAudioLevel()
  }

  const updateAudioLevel = () => {
    if (!analyzerRef.current) return

    const dataArray = new Uint8Array(analyzerRef.current.frequencyBinCount)
    analyzerRef.current.getByteFrequencyData(dataArray)
    
    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length
    setAudioLevel(average / 255 * 100)
    
    animationRef.current = requestAnimationFrame(updateAudioLevel)
  }

  const startRecording = async () => {
    // Prevent starting if already recording
    if (isRecording) {
      console.log('Recording already in progress')
      return
    }

    // Clear any previous errors and results
    setError(null)
    setTranscriptionResult(null)
    setRecordedBlob(null)
    chunksRef.current = []

    try {
      // Request microphone permission if not available
      if (!streamRef.current) {
        console.log('Requesting microphone permission...')
        await requestMicrophonePermission()
        
        if (!streamRef.current) {
          setError('Microphone access denied. Please allow microphone access and try again.')
          return
        }
      }

      // Validate the stream is still active
      if (!streamRef.current.active) {
        console.log('Stream inactive, requesting new permission...')
        await requestMicrophonePermission()
        
        if (!streamRef.current || !streamRef.current.active) {
          setError('Microphone stream is not active. Please refresh and allow microphone access.')
          return
        }
      }

      // Try different mime types for better browser compatibility
      const supportedMimeTypes = [
        'audio/ogg;codecs=opus',
        'audio/webm;codecs=opus', 
        'audio/webm',
        'audio/mp4',
        'audio/wav'
      ]

      let selectedMimeType = ''
      for (const mimeType of supportedMimeTypes) {
        if (MediaRecorder.isTypeSupported(mimeType)) {
          selectedMimeType = mimeType
          console.log('Using mime type:', mimeType)
          break
        }
      }

      if (!selectedMimeType) {
        setError('No supported audio format found on this browser.')
        return
      }

      // Create MediaRecorder with supported mime type
      const mediaRecorder = new MediaRecorder(streamRef.current, {
        mimeType: selectedMimeType
      })

      // Enhanced event handlers
      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data)
          console.log(`Data chunk received: ${event.data.size} bytes`)
        }
      }

      mediaRecorder.onstop = () => {
        if (chunksRef.current.length > 0) {
          const blob = new Blob(chunksRef.current, { type: selectedMimeType })
          setRecordedBlob(blob)
          console.log('Recording stopped successfully, blob size:', blob.size, 'bytes')
        } else {
          console.warn('No audio data recorded')
          setError('No audio data was recorded. Please try again.')
        }
      }

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event)
        setError('Recording error occurred. Please try again.')
        setIsRecording(false)
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
      }

      // Start recording with smaller chunks for better responsiveness
      mediaRecorder.start(250) // Collect data every 250ms
      mediaRecorderRef.current = mediaRecorder
      setIsRecording(true)
      setRecordingDuration(0)

      // Start duration timer
      intervalRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1)
      }, 1000)

      console.log('Recording started successfully with mime type:', selectedMimeType)

    } catch (error) {
      console.error('Error starting recording:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      setError(`Failed to start recording: ${errorMessage}`)
      
      // Clean up on error
      setIsRecording(false)
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }

  const sendToTranscription = async () => {
    if (!recordedBlob) {
      setError('No recording available to transcribe')
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
          // Determine correct file extension based on MIME type
    const getFileExtension = (mimeType: string): string => {
      if (mimeType.includes('webm')) return 'webm'
      if (mimeType.includes('ogg')) return 'ogg' 
      if (mimeType.includes('mp4')) return 'mp4'
      if (mimeType.includes('wav')) return 'wav'
      return 'webm' // fallback
    }
    
    const fileExtension = getFileExtension(recordedBlob.type)
    const formData = new FormData()
    formData.append('file', recordedBlob, `recording-${Date.now()}.${fileExtension}`)

      console.log('🎙️ Sending recorded audio to transcription...')
      
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
      setIsProcessing(false)
    }
  }

  const cleanup = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const copyToClipboard = async () => {
    if (!transcriptionResult?.text) return
    
    try {
      await navigator.clipboard.writeText(transcriptionResult.text)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000) // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
      setError('Failed to copy to clipboard. Please try selecting and copying the text manually.')
    }
  }

  // Don't render anything until client-side hydration is complete
  if (!isClient) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="text-center text-white">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4" />
          <p className="text-xl">Loading...</p>
        </div>
      </div>
    )
  }

  if (hasPermission === null) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="text-center text-white max-w-md">
          {isMobile ? (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
              <Mic className="w-16 h-16 mx-auto mb-4 text-blue-400" />
              <h2 className="text-2xl font-bold mb-4">Ready to Record</h2>
              <p className="text-white/80 mb-6">
                Tap the button below to request microphone access and start recording.
              </p>
              <button 
                onClick={requestMicrophonePermission}
                className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
              >
                <Mic className="w-5 h-5" />
                <span>Request Microphone Access</span>
              </button>
              <p className="text-xs text-white/60 mt-4">
                📱 Make sure to allow microphone access when prompted by your browser.
              </p>
            </div>
          ) : (
            <>
              <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4" />
              <p className="text-xl">Requesting microphone access...</p>
            </>
          )}
        </div>
      </div>
    )
  }

  if (hasPermission === false) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center text-white max-w-md">
          <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
          <h2 className="text-2xl font-bold mb-4">Microphone Access Required</h2>
          <p className="text-white/80 mb-6">
            {isMobile ? "To use voice recording on mobile, we need microphone access. Please allow it in your browser settings or when prompted."
              : "To use voice recording, we need access to your microphone. Please click the button below to grant permission, or check your browser settings if the permission was previously denied."
            }
          </p>
          <div className="space-y-3">
            <button 
              onClick={requestMicrophonePermission}
              className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
            >
              <Mic className="w-5 h-5" />
              <span>Request Microphone Permission</span>
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="w-full bg-gray-600 hover:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              Refresh Page
            </button>
          </div>
          <p className="text-xs text-white/60 mt-4">
            {isMobile ? "📱 If blocked, try refreshing and tapping 'Allow' when your browser asks for microphone access."
              : "💡 If permission is blocked, look for a microphone icon in your browser's address bar and click it to allow access."
            }
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8 text-white">
          <h1 className="text-4xl font-bold mb-2">🎙️ Voice Recorder</h1>
          <p className="text-xl text-white/80">Record your voice and get instant transcriptions!</p>
        </div>

        {/* Recording Controls */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-6">
          <div className="text-center">
            {/* Audio Level Visualization */}
            <div className="mb-6">
              <div className="flex justify-center items-center space-x-2 mb-4">
                <Volume2 className={`w-6 h-6 text-white ${audioLevel > 10 ? 'animate-pulse' : ''}`} />
                <div className="w-48 h-3 bg-white/20 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-400 to-blue-500 transition-all duration-100"
                    style={{ width: `${Math.min(audioLevel, 100)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Recording Duration */}
            {(isRecording || recordedBlob) && (
              <div className="text-2xl font-mono text-white mb-6">
                {formatDuration(recordingDuration)}
              </div>
            )}

            {/* Control Buttons */}
            <div className="flex justify-center space-x-4">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  disabled={isProcessing}
                  className={`${isMobile ? 'px-12 py-6' : 'px-8 py-4'} bg-red-600 hover:bg-red-700 disabled:bg-gray-500 text-white rounded-full font-semibold transition-colors flex items-center space-x-2 text-lg min-h-[64px]`}
                >
                  <Mic className={`${isMobile ? 'w-8 h-8' : 'w-6 h-6'}`} />
                  <span>Start Recording</span>
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className={`${isMobile ? 'px-12 py-6' : 'px-8 py-4'} bg-gray-600 hover:bg-gray-700 text-white rounded-full font-semibold transition-colors flex items-center space-x-2 text-lg animate-pulse min-h-[64px]`}
                >
                  <Square className={`${isMobile ? 'w-8 h-8' : 'w-6 h-6'}`} />
                  <span>Stop Recording</span>
                </button>
              )}

              {recordedBlob && !isRecording && (
                <button
                  onClick={sendToTranscription}
                  disabled={isProcessing}
                  className={`${isMobile ? 'px-12 py-6' : 'px-8 py-4'} bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-full font-semibold transition-colors flex items-center space-x-2 text-lg min-h-[64px]`}
                >
                  {isProcessing ? (
                    <Loader2 className={`${isMobile ? 'w-8 h-8' : 'w-6 h-6'} animate-spin`} />
                  ) : (
                    <Play className={`${isMobile ? 'w-8 h-8' : 'w-6 h-6'}`} />
                  )}
                  <span>{isProcessing ? 'Transcribing...' : 'Get Transcription'}</span>
                </button>
              )}
            </div>

            {/* Recording Status */}
            {isRecording && (
              <div className="mt-4 flex items-center justify-center space-x-2 text-red-400">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                <span className="font-semibold">Recording in progress...</span>
              </div>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4 mb-6">
            <div className="flex items-center space-x-2 text-red-200">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Transcription Results */}
        {transcriptionResult && (
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="w-6 h-6 text-green-400" />
              <h3 className="text-xl font-semibold text-white">Transcription Result</h3>
            </div>
            
            <div className="bg-white/5 rounded-xl p-6 mb-4">
              <p className="text-lg text-white leading-relaxed">
                {transcriptionResult.text}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm text-white/70 mb-4">
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

            {/* Copy Button */}
            <div className="flex justify-center">
              <button
                onClick={copyToClipboard}
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                  isCopied 
                    ? 'bg-green-600 text-white' 
                    : 'bg-blue-600 hover:bg-blue-700 text-white hover:scale-105'
                }`}
                disabled={isCopied}
              >
                {isCopied ? (
                  <>
                    <Check className="w-5 h-5" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-5 h-5" />
                    <span>Copy to Clipboard</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="text-center mt-8">
          <a 
            href="/"
            className="text-white/70 hover:text-white transition-colors underline"
          >
            ← Back to File Upload
          </a>
        </div>
      </div>
    </div>
  )
} 