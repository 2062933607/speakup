import type { PronunciationScore } from '../types';
import './PronunciationFeedback.css';

interface Props {
  score: PronunciationScore | null;
}

export default function PronunciationFeedback({ score }: Props) {
  if (!score) return null;

  return (
    <div className="pronunciation-feedback">
      <div className="pf-header">
        <span className="pf-label">Pronunciation</span>
        <span className={`pf-score ${score.overall_level}`}>
          {score.overall_score}
        </span>
      </div>
      <div className="pf-words">
        {score.word_scores.map((ws, i) => (
          <span key={i} className={`pf-word ${ws.level}`}>
            {ws.word}
          </span>
        ))}
      </div>
      {score.recognized_text !== score.expected_text && (
        <p className="pf-recognized">
          Heard: "{score.recognized_text}"
        </p>
      )}
      <div className="pf-stats">
        <div className="pf-stat-item">
          <span className="pf-dot excellent" />
          {score.stats.excellent}
        </div>
        <div className="pf-stat-item">
          <span className="pf-dot good" />
          {score.stats.good}
        </div>
        <div className="pf-stat-item">
          <span className="pf-dot needs_work" />
          {score.stats.needs_work}
        </div>
      </div>
    </div>
  );
}
