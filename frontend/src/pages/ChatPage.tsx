import { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import ChatBubble from '../components/ChatBubble';
import VoiceButton from '../components/VoiceButton';
import { useChatStore } from '../store/chatStore';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { useChat } from '../hooks/useChat';
import { getCharacterDetail } from '../api/client';
import type { CharacterDetail } from '../types';
import './ChatPage.css';

export default function ChatPage() {
  const { characterId } = useParams<{ characterId: string }>();
  const [searchParams] = useSearchParams();
  const scenarioId = searchParams.get('scenario') || undefined;
  const navigate = useNavigate();

  const store = useChatStore();
  const { startChat, sendVoice, sendText } = useChat();
  const { startRecording, stopRecording } = useAudioRecorder();

  const [character, setCharacter] = useState<CharacterDetail | null>(null);
  const [textInput, setTextInput] = useState('');
  const [initialized, setInitialized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!characterId || initialized) return;
    const init = async () => {
      try {
        const detail = await getCharacterDetail(characterId);
        setCharacter(detail);
        await startChat(characterId, scenarioId);
        setInitialized(true);
      } catch (err) {
        console.error('Failed to init chat:', err);
      }
    };
    init();
  }, [characterId, scenarioId, startChat, initialized]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [store.messages]);

  const handleStartRecording = useCallback(async () => {
    try {
      await startRecording();
      store.setIsRecording(true);
    } catch {
      // 权限被拒绝
    }
  }, [startRecording, store]);

  const handleStopRecording = useCallback(async () => {
    if (!store.conversationId) {
      store.setIsRecording(false);
      return;
    }
    try {
      const blob = await stopRecording();
      store.setIsRecording(false);
      if (blob.size > 0) {
        await sendVoice(blob);
      }
    } catch (err) {
      store.setIsRecording(false);
      console.error('Failed to process voice:', err);
    }
  }, [stopRecording, store, sendVoice]);

  const handleSendText = async () => {
    if (!textInput.trim()) return;
    const text = textInput.trim();
    setTextInput('');
    await sendText(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  const handleBack = () => {
    store.resetChat();
    navigate('/');
  };

  if (!initialized || !character) {
    return (
      <div className="chat-page">
        <div className="chat-loading">Loading conversation...</div>
      </div>
    );
  }

  return (
    <div className="chat-page">
      <div className="chat-topbar">
        <button className="chat-back-btn" onClick={handleBack}>←</button>
        <span className="chat-topbar-avatar">{character.avatar}</span>
        <div className="chat-topbar-info">
          <div className="chat-topbar-name">{character.name}</div>
          <div className="chat-topbar-role">{character.role}</div>
        </div>
      </div>

      <div className="chat-messages">
        {store.messages.map((msg, i) => (
          <ChatBubble
            key={i}
            message={msg}
            characterName={character.name}
            characterAvatar={character.avatar}
          />
        ))}
        {store.isProcessing && (
          <div className="chat-bubble assistant">
            <div className="bubble-header">
              <span className="bubble-avatar">{character.avatar}</span>
              <span className="bubble-name">{character.name}</span>
            </div>
            <p style={{ opacity: 0.6 }}>Typing...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <VoiceButton
          isRecording={store.isRecording}
          isProcessing={store.isProcessing}
          onStart={handleStartRecording}
          onStop={handleStopRecording}
        />
        <div className="text-fallback" style={{ marginLeft: 12 }}>
          <input
            className="text-input"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Or type your message..."
            disabled={store.isProcessing}
          />
          <button
            className="send-btn"
            disabled={!textInput.trim() || store.isProcessing}
            onClick={handleSendText}
          >
            ↑
          </button>
        </div>
      </div>
    </div>
  );
}
