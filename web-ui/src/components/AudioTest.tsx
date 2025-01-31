'use client';

import { useState } from 'react';

export function AudioTest() {
  const [status, setStatus] = useState('');

  const playTestSound = () => {
    try {
      // Create a simple beep using the Web Audio API
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Set the volume
      gainNode.gain.value = 0.1;
      
      // Set frequency to a clear beep
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(440, audioContext.currentTime);
      
      // Start and stop the sound
      oscillator.start();
      setStatus('Playing test sound...');
      
      setTimeout(() => {
        oscillator.stop();
        audioContext.close();
        setStatus('Test completed. Did you hear a beep?');
      }, 1000);
    } catch (error) {
      setStatus(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const playHtmlAudio = () => {
    try {
      const audio = new Audio();
      audio.src = 'data:audio/wav;base64,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';
      audio.play().catch(e => {
        setStatus(`HTML5 Audio Error: ${e.message}`);
      });
      setStatus('Playing HTML5 audio...');
      
      audio.onended = () => {
        setStatus('HTML5 audio completed. Did you hear anything?');
      };
    } catch (error) {
      setStatus(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="p-4 bg-gray-800 rounded-lg">
      <h2 className="text-lg font-medium mb-4 text-blue-300">Audio Test</h2>
      <div className="flex gap-4">
        <button
          onClick={playTestSound}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Test Web Audio
        </button>
        <button
          onClick={playHtmlAudio}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
        >
          Test HTML5 Audio
        </button>
      </div>
      {status && (
        <p className="mt-2 text-gray-300">{status}</p>
      )}
    </div>
  );
}
