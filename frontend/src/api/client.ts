import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export async function getCharacters() {
  const { data } = await api.get('/characters');
  return data;
}

export async function getCharacterDetail(id: string) {
  const { data } = await api.get(`/characters/${id}`);
  return data;
}

export async function getScenarios(characterId?: string) {
  const { data } = await api.get('/scenarios', {
    params: characterId ? { character_id: characterId } : {},
  });
  return data;
}

export async function startConversation(characterId: string, scenarioId?: string) {
  const { data } = await api.post('/chat/start', null, {
    params: { character_id: characterId, scenario_id: scenarioId },
  });
  return data;
}

export async function sendMessage(conversationId: string, text: string) {
  const { data } = await api.post('/chat/send', {
    conversation_id: conversationId,
    text,
  });
  return data;
}

export async function sendVoice(
  conversationId: string,
  audioBlob: Blob,
  expectedText?: string
) {
  const formData = new FormData();
  formData.append('conversation_id', conversationId);
  formData.append('audio', audioBlob, 'recording.webm');
  if (expectedText) {
    formData.append('expected_text', expectedText);
  }
  const { data } = await api.post('/chat/send-voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  });
  return data;
}

export async function getConversations() {
  const { data } = await api.get('/chat/conversations');
  return data;
}

export async function getConversation(id: string) {
  const { data } = await api.get(`/chat/conversations/${id}`);
  return data;
}

export async function getTtsAudio(conversationId: string, messageIndex: number) {
  const { data } = await api.get(
    `/chat/tts/${conversationId}/${messageIndex}`,
    { responseType: 'blob' }
  );
  return data;
}
