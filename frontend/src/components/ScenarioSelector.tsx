import type { Scenario } from '../types';
import './ScenarioSelector.css';

interface Props {
  scenarios: Scenario[];
  selectedId?: string;
  onSelect: (scenario: Scenario) => void;
}

export default function ScenarioSelector({ scenarios, selectedId, onSelect }: Props) {
  return (
    <div className="scenario-list">
      <h3 className="scenario-title">Choose a Scenario</h3>
      {scenarios.map((s) => (
        <div
          key={s.id}
          className={`scenario-item ${selectedId === s.id ? 'selected' : ''}`}
          onClick={() => onSelect(s)}
        >
          <div className="scenario-header">
            <span className="scenario-name">{s.name}</span>
            {selectedId === s.id && <span className="check-mark">✓</span>}
          </div>
          <p className="scenario-desc">{s.description}</p>
          <p className="scenario-opening">
            "{s.opening_line}"
          </p>
        </div>
      ))}
    </div>
  );
}
