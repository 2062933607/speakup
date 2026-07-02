import { useCallback } from 'react';
import { useChatStore } from '../store/chatStore';
import * as api from '../api/client';
import type { Message } from '../types';

export function useChat() {
  const store = useChatStore();

  const startChat = useCallback(
    async (characterId: string, scenarioId?: string) => {
      store.setIsProcessing(true);
      try {
        const res = await api.startConversation(characterId, scenarioId);
        store.setConversationId(res.conversation_id);
        store.setCharacterId(characterId);
        if (scenarioId) store.setScenarioId(scenarioId);

        const msg: Message = {
          ...res.message,
          role: res.message.role,
          has_audio: res.has_audio,
          audio_played: false,
        };
        store.setMessages([msg]);
      } finally {
        store.setIsProcessing(false);
      }
    },
    [store]
  );

  const sendText = useCallback(
    async (text: string) => {
      if (!store.conversationId) return;
      store.setIsProcessing(true);
      try {
        const res = await api.sendMessage(store.conversationId, text);
        store.addMessage(res.user_message);
        store.addMessage({
          ...res.assistant_message,
          has_audio: true,
          audio_played: false,
        });
      } finally {
        store.setIsProcessing(false);
      }
    },
    [store.conversationId, store]
  );

  const sendVoice = useCallback(
    async (audioBlob: Blob, expectedText?: string) => {
      if (!store.conversationId) return;
      store.setIsProcessing(true);
      try {
        const res = await api.sendVoice(
          store.conversationId,
          audioBlob,
          expectedText
        );

        store.addMessage({
          ...res.user_message,
          role: 'user',
        });

        store.addMessage({
          ...res.assistant_message,
          role: 'assistant',
          has_audio: true,
          audio_played: false,
          audio_base64: res.assistant_message.audio_base64,
        });
      } finally {
        store.setIsProcessing(false);
      }
    },
    [store.conversationId, store]
  );

  return { startChat, sendText, sendVoice };
}
