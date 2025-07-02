import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Transcription Outpost</h1>
        <p>Your Real-time Audio Transcription Service</p>
      </header>
      <main className="App-main">
        <div className="transcription-container">
          <button className="start-recording">
            Start Recording
          </button>
          <div className="transcription-output">
            <p>Transcription will appear here...</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
