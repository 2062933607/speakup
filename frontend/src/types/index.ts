export interface Character {
  id: string;
  name: string;
  avatar: string;
  role: string;
  accent: string;
  personality: string;
  scenario_count: number;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  opening_line: string;
  expected_responses: string[];
  character_id?: string;
  character_name?: string;
}

export interface CharacterDetail extends Character {
  scenarios: Scenario[];
  system_prompt: string;
  voice: string;
}

export interface WordScore {
  word: string;
  score: number;
  level: 'excellent' | 'good' | 'needs_work';
}

export interface PronunciationScore {
  overall_score: number;
  overall_level: 'excellent' | 'good' | 'needs_work';
  expected_text: string;
  recognized_text: string;
  word_scores: WordScore[];
  stats: {
    excellent: number;
    good: number;
    needs_work: number;
    total: number;
  };
  fluency: number;
  accuracy: number;
}

export interface Message {
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
  has_audio?: boolean;
  audio_base64?: string;
  pronunciation_score?: PronunciationScore | null;
  audio_played?: boolean;
}

export interface Conversation {
  id: string;
  character_id: string;
  scenario_id: string | null;
  messages: Message[];
  created_at: string;
}

export interface ConversationListItem {
  id: string;
  character_id: string;
  scenario_id: string | null;
  message_count: number;
  created_at: string;
  preview: string;
}
