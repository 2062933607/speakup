import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CharacterCard from '../components/CharacterCard';
import ScenarioSelector from '../components/ScenarioSelector';
import { useChatStore } from '../store/chatStore';
import { getCharacters, getCharacterDetail } from '../api/client';
import type { Character, CharacterDetail, Scenario } from '../types';
import './HomePage.css';

export default function HomePage() {
  const navigate = useNavigate();
  const store = useChatStore();

  const [characters, setCharacters] = useState<Character[]>([]);
  const [characterDetail, setCharacterDetail] = useState<CharacterDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    try {
      const data = await getCharacters();
      setCharacters(data.characters);
    } catch (err) {
      console.error('Failed to load characters:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCharacter = async (c: Character) => {
    store.setSelectedCharacter(c);
    store.setSelectedScenario(null);
    try {
      const detail = await getCharacterDetail(c.id);
      setCharacterDetail(detail);
    } catch (err) {
      console.error('Failed to load character detail:', err);
    }
  };

  const handleSelectScenario = (s: Scenario) => {
    store.setSelectedScenario(s);
  };

  const handleStart = () => {
    if (!store.selectedCharacter) return;
    navigate(
      `/chat/${store.selectedCharacter.id}` +
        (store.selectedScenario ? `?scenario=${store.selectedScenario.id}` : '')
    );
  };

  if (loading) {
    return (
      <div className="page-content">
        <p style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-secondary)' }}>
          Loading characters...
        </p>
      </div>
    );
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h1>SpeakUp</h1>
        <p className="page-subtitle">Practice English with AI characters</p>
      </div>

      <h2 className="section-title">👥 Choose a Character</h2>
      <div className="character-list">
        {characters.map((c) => (
          <CharacterCard
            key={c.id}
            character={c}
            selected={store.selectedCharacter?.id === c.id}
            onClick={() => handleSelectCharacter(c)}
          />
        ))}
      </div>

      {characterDetail && characterDetail.scenarios.length > 0 && (
        <>
          <div className="section-divider" />
          <ScenarioSelector
            scenarios={characterDetail.scenarios}
            selectedId={store.selectedScenario?.id}
            onSelect={handleSelectScenario}
          />
        </>
      )}

      {store.selectedCharacter && (
        <div className="start-btn-wrapper">
          <button className="btn-primary fade-in" onClick={handleStart}>
            🚀 Start Conversation with {store.selectedCharacter.name}
          </button>
        </div>
      )}
    </div>
  );
}
