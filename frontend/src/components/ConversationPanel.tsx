/**
 * Handoff — Conversation Panel Component
 *
 * Left side of the split-screen briefing view.
 * Shows live transcript with speaker labels, text input, and mic controls.
 */

import { useRef, useEffect, useState, useCallback } from 'react';
import type { TranscriptEntry } from '../useVoiceSession';

interface ConversationPanelProps {
    transcript: TranscriptEntry[];
    isMicActive: boolean;
    isAgentSpeaking: boolean;
    sessionId: string;
    onToggleMic: () => void;
    onSendText: (text: string) => void;
    onEndBriefing: () => void;
}

export default function ConversationPanel({
    transcript,
    isMicActive,
    isAgentSpeaking,
    sessionId,
    onToggleMic,
    onSendText,
    onEndBriefing,
}: ConversationPanelProps) {
    const [textInput, setTextInput] = useState('');
    const transcriptEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [transcript]);

    const handleSend = useCallback(() => {
        if (!textInput.trim()) return;
        onSendText(textInput);
        setTextInput('');
    }, [textInput, onSendText]);

    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }, [handleSend]);

    return (
        <div className="conv-panel">
            <div className="conv-panel__header">
                <div className="conv-panel__title-row">
                    <h3>Conversation</h3>
                    <div className="conv-panel__speaking">
                        {isAgentSpeaking && (
                            <div className="speaking-indicator">
                                <div className="speaking-indicator__bars">
                                    <span /><span /><span /><span /><span />
                                </div>
                                <span className="speaking-indicator__label">Agent speaking</span>
                            </div>
                        )}
                    </div>
                </div>
                <span className="conv-panel__session">Session: {sessionId}</span>
            </div>

            <div className="conv-panel__transcript">
                {transcript.length === 0 && (
                    <div className="conv-panel__empty">
                        <div className="conv-panel__empty-pulse" />
                        <p>Connecting to Handoff agent...</p>
                        <p className="conv-panel__hint">The agent will start the briefing automatically</p>
                    </div>
                )}

                {transcript.map((entry, i) => (
                    <div
                        key={i}
                        className={`msg msg--${entry.role}`}
                        style={{ animationDelay: `${Math.min(i * 30, 300)}ms` }}
                    >
                        <div className="msg__header">
                            <span className="msg__avatar">
                                {entry.role === 'agent' ? '🤖' : '👤'}
                            </span>
                            <span className="msg__name">
                                {entry.role === 'agent' ? 'Handoff' : 'You'}
                            </span>
                            <span className="msg__time">
                                {new Date(entry.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                        <p className="msg__text">{entry.text}</p>
                    </div>
                ))}
                <div ref={transcriptEndRef} />
            </div>

            <div className="conv-panel__input">
                <input
                    type="text"
                    placeholder="Type a message or press Space for mic..."
                    value={textInput}
                    onChange={e => setTextInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button className="btn btn--send-sm" onClick={handleSend}>↑</button>
            </div>

            <div className="conv-panel__controls">
                <button
                    className={`btn btn--mic-lg ${isMicActive ? 'btn--mic-lg-active' : ''}`}
                    onClick={onToggleMic}
                >
                    <span className="btn__icon">{isMicActive ? '🔴' : '🎤'}</span>
                    <span>{isMicActive ? 'Mic On' : 'Mic Off'}</span>
                </button>
                <button className="btn btn--end-sm" onClick={onEndBriefing}>
                    End Briefing
                </button>
            </div>
        </div>
    );
}
