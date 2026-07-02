import { useState, useCallback } from 'react';
import type { Message } from '../types';
import './ChatBubble.css';
import PronunciationFeedback from './PronunciationFeedback';

interface Props {
  message: Message;
  characterName?: string;
  characterAvatar?: string;
}

export default function ChatBubble({ message, characterName, characterAvatar }: Props) {
  const [playing, setPlaying] = useState(false);

  const speakWithBrowser = useCallback((text: string) => {
    if (!('speechSynthesis' in window)) return;

    // 停止当前播放
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;

    // 选择英语语音
    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(v => v.lang.startsWith('en-') && v.name.includes('Female'))
      || voices.find(v => v.lang.startsWith('en-'))
      || voices[0];
    if (englishVoice) utterance.voice = englishVoice;

    utterance.onstart = () => setPlaying(true);
    utterance.onend = () => setPlaying(false);
    utterance.onerror = () => setPlaying(false);

    window.speechSynthesis.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    window.speechSynthesis.cancel();
    setPlaying(false);
  }, []);

  const handlePlay = () => {
    if (playing) {
      stopSpeaking();
    } else {
      speakWithBrowser(message.text);
    }
  };

  const isAssistant = message.role === 'assistant';

  return (
    <div className={`chat-bubble ${isAssistant ? 'assistant' : 'user'}`}>
      {isAssistant && (
        <div className="bubble-header">
          <span className="bubble-avatar">{characterAvatar || '🤖'}</span>
          <span className="bubble-name">{characterName || 'Speaker'}</span>
        </div>
      )}
      <p>{message.text}</p>

      {isAssistant && (
        <button
          className={`bubble-play-btn ${playing ? 'playing' : ''}`}
          onClick={handlePlay}
        >
          {playing ? '⏸ Stop' : '🔊 Read aloud'}
        </button>
      )}

      {message.role === 'user' && message.pronunciation_score && (
        <PronunciationFeedback score={message.pronunciation_score} />
      )}
    </div>
  );
}
