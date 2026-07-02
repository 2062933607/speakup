import './VoiceButton.css';

interface Props {
  isRecording: boolean;
  isProcessing: boolean;
  onStart: () => void;
  onStop: () => void;
}

export default function VoiceButton({ isRecording, isProcessing, onStart, onStop }: Props) {
  const handleMouseDown = () => {
    if (!isRecording && !isProcessing) {
      onStart();
    }
  };

  const handleMouseUp = () => {
    if (isRecording) {
      onStop();
    }
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    if (!isRecording && !isProcessing) {
      onStart();
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    if (isRecording) {
      onStop();
    }
  };

  return (
    <div className="voice-btn-container">
      {isRecording ? (
        <div className="wave-indicator">
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
        </div>
      ) : null}

      <button
        className={`voice-btn ${isRecording ? 'recording' : ''}`}
        disabled={isProcessing}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        {isProcessing ? '⏳' : isRecording ? '🔴' : '🎤'}
      </button>

      <span className={isRecording ? 'recording-text' : 'voice-btn-text'}>
        {isProcessing
          ? 'Processing...'
          : isRecording
          ? 'Release to send'
          : 'Hold to talk'}
      </span>
    </div>
  );
}
