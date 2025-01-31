import { NextResponse } from 'next/server';
import { mistralService } from '@/services/mistralService';

interface Location {
  name: string;
  description: string;
  connections: { [key: string]: string };
  events?: string[];
  npcs?: NPC[];
  items?: Item[];
  discoveredSecrets?: string[];
}

interface NPC {
  name: string;
  description: string;
  attitude: 'friendly' | 'neutral' | 'hostile';
  dialogue: string[];
  quest?: Quest;
}

interface Quest {
  id: string;
  title: string;
  description: string;
  requirements?: { [key: string]: number };
  rewards?: { [key: string]: any };
}

interface Item {
  id: string;
  name: string;
  description: string;
  type: 'weapon' | 'armor' | 'consumable' | 'quest';
  effects?: { [key: string]: number };
}

interface Character {
  status: 'creating' | 'active';
  creationStep: 'initial' | 'gender' | 'race' | 'role' | 'complete';
  gender?: string;
  race?: string;
  role?: string;
  currentLocation?: string;
  lastMessage?: string;
}

const gameLocations: { [key: string]: Location } = {
  'Starting Area': {
    name: 'Starting Area',
    description: 'A peaceful clearing surrounded by ancient stones. This is where all great adventures begin. The air is thick with magic, and you can feel destiny calling.',
    connections: {
      north: 'Misty Mountains',
      east: 'Enchanted Forest',
      west: 'Coastal Path'
    },
    npcs: [
      {
        name: 'Elder Sage',
        description: 'A wise elder who has seen many heroes begin their journey.',
        attitude: 'friendly',
        dialogue: [
          'Welcome, brave soul. The realm of Ederick needs heroes like you.',
          'The ancient stones around us have witnessed countless beginnings. What path will you choose?',
          'Remember, young warrior, your choices will shape not only your destiny but the fate of our realm.'
        ]
      }
    ],
    events: [
      'A mysterious traveler shares tales of distant lands.',
      'The ancient stones pulse with an ethereal energy.',
      'You hear whispers of an ancient prophecy.'
    ]
  },
  'Coastal Path': {
    name: 'Coastal Path',
    description: 'A winding path along the cliffs. The salty breeze carries tales of maritime adventures. Waves crash against the rocks below, and seabirds soar overhead.',
    connections: {
      east: 'Starting Area',
      west: 'Coastal Villages',
      south: 'Hidden Cove'
    },
    npcs: [
      {
        name: 'Weathered Fisherman',
        description: 'An old sailor with sun-weathered skin and stories etched in the wrinkles of his face.',
        attitude: 'friendly',
        dialogue: [
          'Aye, the sea holds many secrets. Some better left undiscovered.',
          'Watch the tides, traveler. They speak to those who know how to listen.',
          'The Hidden Cove? Many treasures wash up there, but so do... other things.'
        ]
      }
    ],
    events: [
      'A merchant caravan passes by, their goods laden with exotic wares.',
      'The wind carries whispers of an ancient sea shanty.',
      'You spot a mysterious ship on the horizon.'
    ]
  },
  'Coastal Villages': {
    name: 'Coastal Villages',
    description: 'A cluster of fishing villages where hardy folk make their living from the sea. The harbor is bustling with activity, and the air is rich with the smell of salt and fresh fish.',
    connections: {
      east: 'Coastal Path'
    },
    npcs: [
      {
        name: 'Harbor Master',
        description: 'A stern woman with sharp eyes and an encyclopedic knowledge of ships and tides.',
        attitude: 'neutral',
        dialogue: [
          'Keep your wits about you here. Not all who sail are honest folk.',
          'The sea gives and takes as she pleases. Best remember that.',
          'Looking for work? The notice board by the docks always has something.'
        ]
      },
      {
        name: 'Mysterious Merchant',
        description: 'A cloaked figure with an array of unusual wares and even stranger stories.',
        attitude: 'neutral',
        dialogue: [
          'Interested in something exotic? I have wares from lands beyond the maps.',
          'Every item has a story. Some are worth more than gold.',
          'The sea brings many treasures to these shores. For the right price, they could be yours.'
        ]
      }
    ],
    events: [
      'A merchant ship has just arrived with exotic goods.',
      'The village elder seeks help with recent mysterious occurrences.',
      'A group of sailors share tales of strange lights seen at sea.',
      'The fish market is especially lively today.'
    ]
  },
  'Hidden Cove': {
    name: 'Hidden Cove',
    description: 'A secretive beach accessible only through the coastal path. Crystal-clear waters lap at the shore, and ancient caves dot the cliff face. The air here feels charged with mystery.',
    connections: {
      north: 'Coastal Path'
    },
    npcs: [
      {
        name: 'Cave Explorer',
        description: 'A curious adventurer mapping the mysterious cave systems.',
        attitude: 'friendly',
        dialogue: [
          'These caves... they seem to go on forever. And the markings on the walls...',
          'I swear I heard singing coming from deep within. But that\'s impossible, right?',
          'Want to help me explore? I\'ll split any treasure we find.'
        ]
      }
    ],
    events: [
      'You discover strange markings carved into the cave walls.',
      'The tide reveals glinting objects in the sand.',
      'Ethereal singing echoes from deep within the caves.'
    ]
  },
  'Misty Mountains': {
    name: 'Misty Mountains',
    description: 'Towering peaks shrouded in eternal mist. The air is thin but filled with ancient magic. Snow-capped summits pierce the clouds, and mountain paths wind treacherously upward.',
    connections: {
      south: 'Starting Area'
    },
    npcs: [
      {
        name: 'Mountain Sage',
        description: 'A mysterious figure who seems as ancient as the mountains themselves.',
        attitude: 'neutral',
        dialogue: [
          'The mists hide more than just the peaks. They hide truths older than time.',
          'Listen to the wind, traveler. It speaks of things to come.',
          'Seek the ancient shrines, if you dare. But beware their trials.'
        ]
      }
    ],
    events: [
      'An eagle soars overhead, carrying something glinting in its talons.',
      'The mists part briefly, revealing an ancient shrine.',
      'You hear the distant sound of drums from high in the mountains.'
    ]
  },
  'Enchanted Forest': {
    name: 'Enchanted Forest',
    description: 'An ancient woodland where the trees whisper secrets. The air sparkles with magical energy, and ethereal lights dance between the ancient trunks. Every path seems to shift and change.',
    connections: {
      west: 'Starting Area'
    },
    npcs: [
      {
        name: 'Forest Guardian',
        description: 'A mystical being that seems to fade in and out of existence like morning mist.',
        attitude: 'neutral',
        dialogue: [
          'The forest remembers all who pass through its realm.',
          'Some paths reveal themselves only to those who are worthy.',
          'The trees speak of darkness growing in the deep woods.'
        ]
      },
      {
        name: 'Lost Scholar',
        description: 'A researcher studying the forest\'s magical properties, though she seems to have strayed from her camp.',
        attitude: 'friendly',
        dialogue: [
          'The magical readings here are off the charts! Simply fascinating!',
          'Have you seen my research camp? I swear it was right here...',
          'These trees... they\'re not just alive, they\'re aware.'
        ]
      }
    ],
    events: [
      'Magical lights dance through the trees, leading somewhere.',
      'You discover a clearing filled with glowing mushrooms.',
      'The trees seem to whisper ancient secrets.',
      'A mystical creature watches you from the shadows.'
    ]
  }
};

// Helper function to check if movement is possible
function canMove(currentLocation: string, direction: string): string | null {
  const location = gameLocations[currentLocation];
  if (!location) return null;
  return location.connections[direction] || null;
}

// Helper function to get available directions
function getAvailableDirections(location: string): string[] {
  const loc = gameLocations[location];
  if (!loc) return [];
  return Object.entries(loc.connections).map(([dir, _]) => dir);
}

// Helper function to process natural language movement
function processMovement(message: string, currentLocation: string): string | null {
  const movementPatterns = [
    /(?:go|move|head|walk|travel)\s+(north|south|east|west)/i,
    /(?:towards|to|into)\s+(?:the\s+)?([a-zA-Z\s]+)/i
  ];

  for (const pattern of movementPatterns) {
    const match = message.match(pattern);
    if (match) {
      if (pattern === movementPatterns[0]) {
        return match[1].toLowerCase();
      } else {
        // Handle location names
        const targetLocation = match[1].toLowerCase();
        const location = gameLocations[currentLocation];
        for (const [direction, connectedLocation] of Object.entries(location.connections)) {
          if (connectedLocation.toLowerCase().includes(targetLocation)) {
            return direction;
          }
        }
      }
    }
  }
  return null;
}

// Generate response based on message and game state
async function generateGameResponse(message: string, gameState: any) {
  const { character } = gameState;

  // Handle character creation flow
  if (character.status === 'creating') {
    switch (character.creationStep) {
      case 'initial':
        if (message.toLowerCase().includes('look') || message.toLowerCase().includes('where')) {
          return {
            response: "You're in complete darkness. You can't see anything, but you can hear a mysterious voice asking about your identity. The voice seems interested in learning more about you.",
            character: {
              ...character,
              creationStep: 'gender'
            }
          };
        }
        break;

      case 'gender':
        if (message.toLowerCase().includes('male') || message.toLowerCase().includes('female') || message.toLowerCase().includes('other')) {
          character.gender = message;
          return {
            response: "The voice acknowledges your response. 'And what race are you?' it asks, curious about your heritage.",
            character: {
              ...character,
              creationStep: 'race'
            }
          };
        }
        break;

      case 'race':
        character.race = message;
        return {
          response: "The voice hums thoughtfully. 'A " + message + "... interesting. And what is your role in this world? Are you a warrior, a mage, perhaps a rogue?'",
          character: {
            ...character,
            creationStep: 'role'
          }
        };

      case 'role':
        character.role = message;
        return {
          response: `The darkness begins to fade, and you find yourself in a dimly lit chamber. As a ${message}, your journey is about to begin. What would you like to do?`,
          character: {
            ...character,
            status: 'active',
            currentLocation: 'Starting Chamber',
            creationStep: 'complete'
          }
        };

      default:
        break;
    }
  }

  // Handle regular game interactions
  try {
    const response = await mistralService.generateResponse(message, {
      currentLocation: character.currentLocation,
      lastEvents: gameState.lastEvents,
      nearbyNPCs: gameState.nearbyNPCs,
      playerState: character
    });

    return {
      response,
      character: {
        ...character,
        lastMessage: message
      }
    };
  } catch (error) {
    console.error('Error generating response:', error);
    return {
      response: 'The ancient magic falters momentarily. (Error generating response)',
      character
    };
  }
}

// Update POST handler to handle async function
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { message, gameState } = body;

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    const response = await generateGameResponse(message, gameState);
    return NextResponse.json(response);
  } catch (error) {
    console.error('Error processing request:', error);
    return NextResponse.json(
      { 
        response: 'The ancient magic falters momentarily. (The game system is experiencing temporary difficulties)',
        gameState: body.gameState 
      },
      { status: 200 }  
    );
  }
}
