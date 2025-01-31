'use client';

import { useState, KeyboardEvent, useEffect, useRef } from 'react';
import { gameService, CharacterData } from '@/services/gameService';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function Conversation() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [inputText, setInputText] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [character, setCharacter] = useState<CharacterData | null>(null);
  const [characterCreation, setCharacterCreation] = useState({
    step: 'initial',
    options: [] as string[],
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleCharacterCreation = async (input: string) => {
    try {
      setIsConnecting(true);
      setError(null);

      const response = await gameService.createCharacter(
        character?.name || input,
        characterCreation.step,
        input
      );

      setCharacterCreation({
        step: response.step,
        options: response.options || [],
      });

      if (response.character_data) {
        setCharacter(response.character_data);
      }

      setMessages(prev => [
        ...prev,
        { role: 'user', content: input },
        { role: 'assistant', content: response.prompt },
      ]);

      if (response.step === 'complete') {
        setCharacterCreation({ step: 'playing', options: [] });
      }
    } catch (error) {
      console.error('Error in character creation:', error);
      setError('Failed to process character creation');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleGameplay = async (input: string) => {
    try {
      setIsConnecting(true);
      setError(null);

      if (!character?.name) {
        throw new Error('No active character');
      }

      const response = await gameService.performGameAction(
        character.name,
        'interact',
        input
      );

      setMessages(prev => [
        ...prev,
        { role: 'user', content: input },
        { role: 'assistant', content: response.message },
      ]);

      if (response.character_data) {
        setCharacter(response.character_data);
      }
    } catch (error) {
      console.error('Error in gameplay:', error);
      setError('Failed to process game action');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleSubmit = async () => {
    if (!inputText.trim() || isConnecting) return;

    const input = inputText.trim();
    setInputText('');

    if (!character) {
      // Initialize character creation with name
      setCharacter({
        name: input,
        gender: '',
        race: '',
        role: '',
        time_period: '',
        resources: {
          health: 100,
          credits: 0,
        },
        inventory: [],
        relationships: {},
      });
      handleCharacterCreation(input);
    } else if (characterCreation.step !== 'playing') {
      handleCharacterCreation(input);
    } else {
      handleGameplay(input);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-gray-800 rounded-lg p-4 overflow-hidden">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-2 rounded ${
              message.role === 'user'
                ? 'bg-blue-600 ml-auto'
                : 'bg-gray-700'
            }`}
          >
            {message.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      {characterCreation.options.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {characterCreation.options.map((option) => (
            <button
              key={option}
              onClick={() => {
                setInputText(option);
                handleSubmit();
              }}
              className="px-3 py-1 bg-blue-500 rounded hover:bg-blue-600"
            >
              {option}
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            !character 
              ? "Enter your character's name..." 
              : characterCreation.step === 'playing'
              ? 'What would you like to do?'
              : 'Choose your response...'
          }
          disabled={isConnecting}
          className="flex-1 p-2 bg-gray-700 rounded resize-none"
          rows={2}
        />
        <button
          onClick={handleSubmit}
          disabled={isConnecting || !inputText.trim()}
          className="px-4 py-2 bg-blue-500 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Send
        </button>
      </div>
      
      {error && (
        <div className="mt-2 text-red-500 text-sm">{error}</div>
      )}

      {character && characterCreation.step === 'playing' && (
        <div className="mt-4 p-2 bg-gray-700 rounded text-sm">
          <h3 className="font-bold mb-1">Character Status</h3>
          <div className="grid grid-cols-2 gap-2">
            <div>Health: {character.resources.health}</div>
            <div>Credits: {character.resources.credits}</div>
          </div>
        </div>
      )}
    </div>
  );
}
