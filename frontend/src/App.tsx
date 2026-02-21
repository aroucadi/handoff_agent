/**
 * Handoff Voice UI — Main App Component
 *
 * Minimal but functional voice briefing interface.
 * "Start Briefing" connects to Gemini Live via WebSocket.
 * Shows live transcript, tool calls, current node, and speaking indicator.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useVoiceSession } from './useVoiceSession';

export default function App() {
    const {
        isConnected,
        isMicActive,
        isAgentSpeaking,
        transcript,
        toolCalls,
        currentNode,
        connect,
        disconnect,
        toggleMic,
        sendText,
    } = useVoiceSession();

    const [clientId, setClientId] = useState('');
    const [csmName, setCsmName] = useState('');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [textInput, setTextInput] = useState('');
    const [isStarting, setIsStarting] = useState(false);

    const transcriptEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll transcript
    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [transcript]);

    const handleStartBriefing = useCallback(async () => {
        if (!clientId.trim()) return;
        setIsStarting(true);

        try {
            const res = await fetch('/api/sessions/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ client_id: clientId, csm_name: csmName || 'CSM' }),
            });
            const data = await res.json();
            setSessionId(data.session_id);
            connect(data.session_id);
        } catch (err) {
            console.error('Failed to start session:', err);
        } finally {
            setIsStarting(false);
        }
    }, [clientId, csmName, connect]);

    const handleEndBriefing = useCallback(() => {
        disconnect();
        setSessionId(null);
    }, [disconnect]);

    const handleSendText = useCallback(() => {
        if (!textInput.trim()) return;
        sendText(textInput);
        setTextInput('');
    }, [textInput, sendText]);

    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendText();
        }
    }, [handleSendText]);

    // Keyboard shortcut: Space to toggle mic
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (e.code === 'Space' && isConnected && e.target === document.body) {
                e.preventDefault();
                toggleMic();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [isConnected, toggleMic]);

    return (
        <div className="app">
            <header className="header">
                <div className="header__brand">
                    <h1 className="header__title">Handoff</h1>
                    <span className="header__subtitle">Voice Agent</span>
                </div>
                {isConnected && (
                    <div className="header__status">
                        <div className={`status-dot ${isAgentSpeaking ? 'status-dot--speaking' : ''}`} />
                        <span>{isAgentSpeaking ? 'Agent speaking...' : 'Listening'}</span>
                    </div>
                )}
            </header>

            {!isConnected ? (
                /* ─── Setup Panel ─────────────────────────────────── */
                <div className="setup">
                    <div className="setup__card">
                        <h2 className="setup__title">Start a Briefing</h2>
                        <p className="setup__desc">
                            Enter the client ID to begin your pre-kickoff voice briefing with Handoff.
                        </p>

                        <div className="setup__field">
                            <label>Client ID</label>
                            <input
                                type="text"
                                placeholder="e.g. opp-2026-gm001"
                                value={clientId}
                                onChange={e => setClientId(e.target.value)}
                            />
                        </div>

                        <div className="setup__field">
                            <label>Your Name</label>
                            <input
                                type="text"
                                placeholder="e.g. Sarah"
                                value={csmName}
                                onChange={e => setCsmName(e.target.value)}
                            />
                        </div>

                        <button
                            className="btn btn--primary"
                            onClick={handleStartBriefing}
                            disabled={!clientId.trim() || isStarting}
                        >
                            {isStarting ? 'Connecting...' : '🎙️ Start Briefing'}
                        </button>
                    </div>
                </div>
            ) : (
                /* ─── Briefing Session ────────────────────────────── */
                <div className="session">
                    {/* Left: Conversation */}
                    <div className="conversation">
                        <div className="conversation__header">
                            <h3>Conversation</h3>
                            <span className="conversation__session-id">Session: {sessionId}</span>
                        </div>

                        <div className="transcript">
                            {transcript.length === 0 && (
                                <div className="transcript__empty">
                                    Waiting for agent to start the briefing...
                                </div>
                            )}
                            {transcript.map((entry, i) => (
                                <div key={i} className={`transcript__entry transcript__entry--${entry.role}`}>
                                    <span className="transcript__role">
                                        {entry.role === 'agent' ? '🤖 Handoff' : '👤 You'}
                                    </span>
                                    <p className="transcript__text">{entry.text}</p>
                                </div>
                            ))}
                            <div ref={transcriptEndRef} />
                        </div>

                        {/* Text input fallback */}
                        <div className="conversation__input">
                            <input
                                type="text"
                                placeholder="Type a message (or press Space to toggle mic)..."
                                value={textInput}
                                onChange={e => setTextInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                            />
                            <button className="btn btn--send" onClick={handleSendText}>Send</button>
                        </div>

                        {/* Controls */}
                        <div className="controls">
                            <button
                                className={`btn btn--mic ${isMicActive ? 'btn--mic-active' : ''}`}
                                onClick={toggleMic}
                            >
                                {isMicActive ? '🔴 Mic On' : '🎤 Mic Off'}
                            </button>
                            <button className="btn btn--end" onClick={handleEndBriefing}>
                                End Briefing
                            </button>
                        </div>
                    </div>

                    {/* Right: Graph Activity */}
                    <div className="sidebar">
                        <div className="sidebar__section">
                            <h3>Current Node</h3>
                            {currentNode ? (
                                <div className="node-badge">{currentNode}</div>
                            ) : (
                                <div className="sidebar__empty">No node selected</div>
                            )}
                        </div>

                        <div className="sidebar__section">
                            <h3>Tool Calls ({toolCalls.length})</h3>
                            <div className="tool-log">
                                {toolCalls.map((tc, i) => (
                                    <div key={i} className="tool-log__entry">
                                        <span className="tool-log__name">{tc.name}</span>
                                        <span className="tool-log__args">
                                            {Object.entries(tc.args)
                                                .filter(([k]) => k !== 'client_id')
                                                .map(([k, v]) => `${k}=${v}`)
                                                .join(', ')}
                                        </span>
                                    </div>
                                ))}
                                {toolCalls.length === 0 && (
                                    <div className="sidebar__empty">No tool calls yet</div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
