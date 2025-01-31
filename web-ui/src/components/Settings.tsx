'use client';

import React from 'react';
import { mistralService } from '@/services/mistralService';

interface SettingsProps {
  className?: string;
}

export function Settings({ className = '' }: SettingsProps) {
  const [verbosity, setVerbosity] = React.useState(mistralService.getVerbosityLevel());

  const handleVerbosityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    setVerbosity(newValue);
    mistralService.setVerbosityLevel(newValue);
  };

  const getVerbosityLabel = (value: number): string => {
    if (value < 0.3) return 'Concise';
    if (value < 0.7) return 'Balanced';
    return 'Detailed';
  };

  return (
    <div className={`p-4 bg-gray-800 rounded-lg ${className}`}>
      <h3 className="text-lg font-semibold mb-4 text-gray-200">Game Settings</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Response Style: {getVerbosityLabel(verbosity)}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={verbosity}
            onChange={handleVerbosityChange}
            className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>Concise</span>
            <span>Balanced</span>
            <span>Detailed</span>
          </div>
        </div>
      </div>
    </div>
  );
}
