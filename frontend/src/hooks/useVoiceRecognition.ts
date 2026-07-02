import { useState, useRef, useCallback } from 'react';

export function useVoiceRecognition() {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const finalTextRef = useRef('');

  const isSupported = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  const startListening = useCallback(async (): Promise<void> => {
    if (!isSupported) {
      throw new Error('Speech recognition not supported');
    }
    return new Promise((resolve, reject) => {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      finalTextRef.current = '';

      recognition.lang = 'en-US';
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;

      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        finalTextRef.current = transcript;
      };

      recognition.onend = () => {
        setIsListening(false);
        resolve();
      };

      recognition.onerror = (event: any) => {
        setIsListening(false);
        if (event.error === 'no-speech') {
          resolve();
        } else {
          reject(new Error(event.error));
        }
      };

      setIsListening(true);
      recognition.start();
    });
  }, [isSupported]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
  }, []);

  const getRecognizedText = useCallback(() => {
    return finalTextRef.current;
  }, []);

  return { isListening, startListening, stopListening, getRecognizedText, isSupported };
}
