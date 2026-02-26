/**
 * Synapse — Conversation Panel Component
 *
 * Left side of the split-screen briefing view.
 * Shows live transcript with speaker labels, text input, and mic controls.
 */

import { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import type { TranscriptEntry, AgentStatus } from '../useVoiceSession';
import SynapseOrb, { OrbState } from './SynapseOrb';

interface ConversationPanelProps {
    transcript: TranscriptEntry[];
    isMicActive: boolean;
    isScreenShared: boolean;
    agentStatus: AgentStatus;
    sessionId: string;
    onToggleMic: () => void;
    onToggleScreenShare: () => void;
    onSendText: (text: string) => void;
    onEndBriefing: () => void;
}

export default function ConversationPanel({
    transcript,
    isMicActive,
    isScreenShared,
    agentStatus,
    sessionId,
    onToggleMic,
    onToggleScreenShare,
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

    // Determine current orb state
    const orbState: OrbState = useMemo(() => {
        if (agentStatus === 'speaking') return 'speaking';
        if (agentStatus === 'thinking') return 'thinking';
        if (isMicActive) return 'listening';
        return 'idle';
    }, [agentStatus, isMicActive]);

    return (
        <div className="conv-panel">
            <div className="conv-panel__header flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <SynapseOrb state={orbState} />
                    <div>
                        <h3>Synapse Agent</h3>
                        <span className="conv-panel__session">
                            {agentStatus === 'speaking' ? 'Speaking...' : agentStatus === 'thinking' ? 'Thinking...' : isMicActive ? 'Listening...' : 'Standing by'}
                        </span>
                    </div>
                </div>
                <span className="conv-panel__session font-mono text-xs opacity-50">Session: {sessionId}</span>
            </div>

            <div className="conv-panel__transcript">
                {transcript.length === 0 && (
                    <div className="conv-panel__empty">
                        <div className="conv-panel__empty-pulse" />
                        <p>Connecting to Synapse...</p>
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
                                {entry.role === 'agent' ? 'Synapse' : 'You'}
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
                    title="Toggle Microphone"
                >
                    <span className="btn__icon">{isMicActive ? '🔴' : '🎤'}</span>
                    <span>{isMicActive ? 'Mic On' : 'Mic Off'}</span>
                </button>
                <button
                    className={`btn btn--mic-lg ${isScreenShared ? 'btn--mic-lg-active' : ''}`}
                    onClick={onToggleScreenShare}
                    title="Share Screen with Gemini Vision (Hackathon)"
                >
                    <span className="btn__icon">{isScreenShared ? '👁️' : '💻'}</span>
                    <span>{isScreenShared ? 'Sharing Vision' : 'Share Screen'}</span>
                </button>
                <button className="btn btn--end-sm" onClick={onEndBriefing}>
                    End Briefing
                </button>
            </div>
        </div>
    );
}
