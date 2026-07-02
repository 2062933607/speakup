import type { Character } from '../types';
import './CharacterCard.css';

interface Props {
  character: Character;
  selected?: boolean;
  onClick: () => void;
}

export default function CharacterCard({ character, selected, onClick }: Props) {
  const accentLabel: Record<string, string> = {
    american: '🇺🇸 American',
    british: '🇬🇧 British',
    australian: '🇦🇺 Australian',
  };

  return (
    <div
      className={`character-card ${selected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="character-avatar">{character.avatar}</div>
      <div className="character-info">
        <h3 className="character-name">{character.name}</h3>
        <p className="character-role">{character.role}</p>
        <div className="character-meta">
          <span className="character-accent">
            {accentLabel[character.accent] || character.accent}
          </span>
          <span className="character-scenarios">
            {character.scenario_count} scenarios
          </span>
        </div>
      </div>
      {selected && <div className="check-mark">✓</div>}
    </div>
  );
}
