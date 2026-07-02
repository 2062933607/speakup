import { useState, useEffect } from 'react';
import { getConversations, getCharacters } from '../api/client';
import type { ConversationListItem } from '../types';
import './HistoryPage.css';

export default function HistoryPage() {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [characterNames, setCharacterNames] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [convData, charData] = await Promise.all([
        getConversations(),
        getCharacters(),
      ]);

      const nameMap: Record<string, string> = {};
      charData.characters.forEach((c: { id: string; name: string }) => {
        nameMap[c.id] = c.name;
      });
      setCharacterNames(nameMap);
      setConversations(convData.conversations || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);

    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return d.toLocaleDateString();
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h1>History</h1>
        <p className="page-subtitle">Your conversation history</p>
      </div>

      {loading ? (
        <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: 40 }}>
          Loading...
        </p>
      ) : conversations.length === 0 ? (
        <div className="history-empty">
          <div className="history-empty-icon">📝</div>
          <p className="history-empty-text">No conversations yet. Start practicing!</p>
        </div>
      ) : (
        <div className="history-list">
          {conversations.map((c) => (
            <div key={c.id} className="history-item">
              <div className="history-header">
                <span className="history-date">{formatDate(c.created_at)}</span>
                <span className="history-count">{c.message_count} messages</span>
              </div>
              {c.preview && (
                <p className="history-preview">{c.preview}</p>
              )}
              <span className="history-character">
                {characterNames[c.character_id] || c.character_id}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
