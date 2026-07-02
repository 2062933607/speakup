import { create } from 'zustand';
import type { Character, Scenario, Message, ConversationListItem } from '../types';

interface ChatState {
  // 当前对话
  conversationId: string | null;
  characterId: string | null;
  scenarioId: string | null;
  messages: Message[];
  isRecording: boolean;
  isProcessing: boolean;

  // 选择状态
  selectedCharacter: Character | null;
  selectedScenario: Scenario | null;

  // 历史列表
  conversations: ConversationListItem[];

  // Actions
  setConversationId: (id: string | null) => void;
  setCharacterId: (id: string | null) => void;
  setScenarioId: (id: string | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateLastAssistantMessage: (updates: Partial<Message>) => void;
  setIsRecording: (v: boolean) => void;
  setIsProcessing: (v: boolean) => void;
  setSelectedCharacter: (c: Character | null) => void;
  setSelectedScenario: (s: Scenario | null) => void;
  setConversations: (list: ConversationListItem[]) => void;
  resetChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  conversationId: null,
  characterId: null,
  scenarioId: null,
  messages: [],
  isRecording: false,
  isProcessing: false,
  selectedCharacter: null,
  selectedScenario: null,
  conversations: [],

  setConversationId: (id) => set({ conversationId: id }),
  setCharacterId: (id) => set({ characterId: id }),
  setScenarioId: (id) => set({ scenarioId: id }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  updateLastAssistantMessage: (updates) =>
    set((state) => {
      const messages = [...state.messages];
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].role === 'assistant') {
          messages[i] = { ...messages[i], ...updates };
          break;
        }
      }
      return { messages };
    }),
  setIsRecording: (v) => set({ isRecording: v }),
  setIsProcessing: (v) => set({ isProcessing: v }),
  setSelectedCharacter: (c) => set({ selectedCharacter: c }),
  setSelectedScenario: (s) => set({ selectedScenario: s }),
  setConversations: (list) => set({ conversations: list }),
  resetChat: () =>
    set({
      conversationId: null,
      characterId: null,
      scenarioId: null,
      messages: [],
      isRecording: false,
      isProcessing: false,
    }),
}));
