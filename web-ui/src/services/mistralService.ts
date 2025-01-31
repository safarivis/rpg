interface ChatMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
}

interface ChatResponse {
  choices: {
    message: {
      content: string;
    };
  }[];
}

export class MistralService {
  private static instance: MistralService;
  private apiKey: string;
  private model: string = 'mistral-tiny';
  private verbosityLevel: number = 0.7; // 0 = very concise, 1 = very detailed

  private constructor() {
    this.apiKey = process.env.MISTRAL_API_KEY || '';
    if (!this.apiKey) {
      console.warn('MISTRAL_API_KEY not found in environment variables');
    }
  }

  public static getInstance(): MistralService {
    if (!MistralService.instance) {
      MistralService.instance = new MistralService();
    }
    return MistralService.instance;
  }

  public setVerbosityLevel(level: number) {
    this.verbosityLevel = Math.max(0, Math.min(1, level)); // Clamp between 0 and 1
  }

  public getVerbosityLevel(): number {
    return this.verbosityLevel;
  }

  private buildSystemPrompt(): string {
    const verbosityGuide = this.verbosityLevel < 0.3 
      ? "Keep your responses very brief and to the point. Focus on essential information only."
      : this.verbosityLevel < 0.7 
        ? "Provide balanced responses with moderate detail. Include key descriptions while staying concise."
        : "Create rich, detailed responses with vivid descriptions and extensive world-building.";

    return `You are an AI game master in the realm of Ederick, a fantasy world filled with magic, mystery, and adventure. 
Your role is to create engaging responses to player actions, describing the world, NPCs, and events.

Response Style Guide:
${verbosityGuide}

Guidelines:
1. Stay in character as a fantasy game master
2. ${this.verbosityLevel < 0.3 ? 'Focus on actions and outcomes' : 'Provide sensory descriptions'}
3. Reference the world's lore
4. Maintain consistent NPC personalities
5. Create contextual responses
${this.verbosityLevel > 0.7 ? '6. Include ambient details and atmosphere' : ''}`;
  }

  private async makeRequest(messages: ChatMessage[]): Promise<ChatResponse> {
    try {
      const response = await fetch('https://api.mistral.ai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: this.model,
          messages: messages,
          temperature: this.verbosityLevel
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error calling Mistral API:', error);
      throw error;
    }
  }

  public async generateResponse(
    playerAction: string,
    context: {
      currentLocation: string;
      lastEvents?: string[];
      nearbyNPCs?: string[];
      playerState?: any;
    }
  ): Promise<string> {
    const messages: ChatMessage[] = [
      {
        role: 'system',
        content: this.buildSystemPrompt()
      },
      {
        role: 'user',
        content: `Current location: ${context.currentLocation}
${context.nearbyNPCs ? `Nearby NPCs: ${context.nearbyNPCs.join(', ')}` : ''}
${context.lastEvents ? `Recent events: ${context.lastEvents.join(', ')}` : ''}
Player action: ${playerAction}

Generate an immersive response describing what happens next.`
      }
    ];

    try {
      const response = await this.makeRequest(messages);
      return response.choices[0].message.content;
    } catch (error) {
      console.error('Failed to generate response:', error);
      return 'The ancient magic seems to falter. (Error generating response)';
    }
  }
}

export const mistralService = MistralService.getInstance();
