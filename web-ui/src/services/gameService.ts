const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface CharacterData {
  name: string;
  gender: string;
  race: string;
  role: string;
  time_period: string;
  resources: {
    health: number;
    credits: number;
  };
  inventory: string[];
  relationships: Record<string, string>;
}

export interface GameResponse {
  message: string;
  character_data: CharacterData;
}

export interface CharacterCreationResponse {
  step: string;
  prompt: string;
  options?: string[];
  character_data: CharacterData;
}

class GameService {
  async createCharacter(name: string, step: string, input_value?: string): Promise<CharacterCreationResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/character/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          step,
          input_value,
        }),
        credentials: 'omit', // Don't send credentials for now
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API Error:', response.status, errorData);
        throw new Error(`API error: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Error in createCharacter:', error);
      throw error;
    }
  }

  async getCharacter(name: string): Promise<CharacterData> {
    try {
      const response = await fetch(`${API_BASE_URL}/character/${name}`, {
        credentials: 'omit',
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API Error:', response.status, errorData);
        throw new Error(`API error: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Error in getCharacter:', error);
      throw error;
    }
  }

  async performGameAction(characterName: string, action: string, inputText: string, context?: Record<string, any>): Promise<GameResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/game/action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_name: characterName,
          action,
          input_text: inputText,
          context,
        }),
        credentials: 'omit',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API Error:', response.status, errorData);
        throw new Error(`API error: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Error in performGameAction:', error);
      throw error;
    }
  }
}

export const gameService = new GameService();
