/**
 * Synapse — Conversation Panel Component
 *
 * Left side of the split-screen briefing view.
 * Shows live transcript with speaker labels, text input, and mic controls.
 */

import { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import type { TranscriptEntry, AgentStatus } from '../useVoiceSession';
import SynapseOrb, { OrbState } from './SynapseOrb';
import { Bot, User, Mic, MicOff, MonitorSmartphone, MonitorOff, Send, XCircle } from 'lucide-react';

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
        <div className="conv-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', background: '#09090b', borderRight: '1px solid rgba(255,255,255,0.05)' }}>
            {/* BIG Centered Orb Area */}
            <div style={{ flex: '0 0 320px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'radial-gradient(circle at center, rgba(168, 85, 247, 0.08) 0%, transparent 60%)', position: 'relative' }}>
                <div style={{ transform: 'scale(2.5)', marginBottom: '3rem' }}>
                    <SynapseOrb state={orbState} />
                </div>
                <div style={{
                    fontSize: '0.875rem',
                    letterSpacing: '0.25em',
                    color: agentStatus === 'speaking' ? '#10b981' : agentStatus === 'thinking' ? '#a855f7' : isMicActive ? '#38bdf8' : 'var(--text-muted)',
                    fontStyle: 'italic',
                    fontWeight: '600',
                    opacity: 0.9,
                    textTransform: 'uppercase'
                }}>
                    {agentStatus === 'speaking' ? 'Synapse Speaking' : agentStatus === 'thinking' ? 'Synapse Thinking' : isMicActive ? 'Synapse Voice Active' : 'Agent Standby'}
                </div>
            </div>

            <div className="conv-panel__transcript" style={{ flex: 1, overflowY: 'auto', padding: '2rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
                        Multimodal Context
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted-sm)', fontFamily: 'monospace' }}>Session: {sessionId.slice(-6)}</span>
                </div>

                {transcript.length === 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3rem 1rem', color: 'var(--text-muted-sm)', textAlign: 'center', border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '16px' }}>
                        <p style={{ margin: 0, fontSize: '0.875rem' }}>Awaiting context...</p>
                    </div>
                )}

                {transcript.map((entry, i) => (
                    <div
                        key={i}
                        className={`msg msg--${entry.role}`}
                        style={{
                            animationDelay: `${Math.min(i * 30, 300)}ms`,
                            alignSelf: entry.role === 'agent' ? 'flex-start' : 'flex-end',
                            width: '100%',
                            background: entry.role === 'agent' ? 'rgba(255,255,255,0.02)' : 'rgba(56, 189, 248, 0.05)',
                            padding: '1.25rem',
                            borderRadius: '16px',
                            border: entry.role === 'agent' ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(56, 189, 248, 0.15)'
                        }}
                    >
                        <div className="msg__header" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <span className="msg__avatar" style={{ padding: '0.25rem', background: entry.role === 'agent' ? 'rgba(255,255,255,0.1)' : 'rgba(56, 189, 248, 0.2)', borderRadius: '50%', color: entry.role === 'agent' ? '#fff' : '#38bdf8' }}>
                                {entry.role === 'agent' ? <Bot size={14} /> : <User size={14} />}
                            </span>
                            <span className="msg__name" style={{ fontWeight: '600', fontSize: '0.875rem', color: entry.role === 'agent' ? '#fff' : '#38bdf8' }}>
                                {entry.role === 'agent' ? 'Synapse' : 'You'}
                            </span>
                            <span className="msg__time font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted-sm)', marginLeft: 'auto' }}>
                                {new Date(entry.timestamp).toLocaleTimeString()}
                            </span>
                        </div>
                        <p className="msg__text" style={{ margin: 0, lineHeight: '1.6', color: entry.role === 'agent' ? 'rgba(255,255,255,0.8)' : 'rgba(255,255,255,0.9)', fontSize: '0.9375rem', fontStyle: entry.role === 'agent' ? 'italic' : 'normal' }}>
                            {entry.role === 'agent' ? `"${entry.text}"` : entry.text}
                        </p>
                    </div>
                ))}
                <div ref={transcriptEndRef} />
            </div>

            <div className="conv-panel__input" style={{ padding: '1.25rem 1.5rem', borderTop: '1px solid rgba(255,255,255,0.05)', background: 'rgba(0,0,0,0.4)', display: 'flex', gap: '1rem' }}>
                <input
                    type="text"
                    placeholder="Type a message..."
                    value={textInput}
                    onChange={e => setTextInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    style={{ flex: 1, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '0.75rem 1rem', color: '#fff', outline: 'none', transition: 'all 0.2s', fontSize: '0.875rem' }}
                    onFocus={e => e.target.style.borderColor = 'rgba(255,255,255,0.3)'}
                    onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
                />
                <button className="btn btn--send-sm glass-btn glow-cyan" onClick={handleSend} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 1rem', borderRadius: '12px' }} disabled={!textInput.trim()}>
                    <Send size={16} />
                </button>
            </div>

            {/* Premium Controls Row */}
            <div className="conv-panel__controls" style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', padding: '1.5rem', background: '#000', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <button
                    className={`btn ${isScreenShared ? 'btn--mic-lg-active glow-magenta' : 'glass-btn-outline'}`}
                    onClick={onToggleScreenShare}
                    title="Share Screen with Gemini Vision"
                    style={{ width: '56px', height: '56px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', border: isScreenShared ? '1px solid var(--neon-magenta)' : '1px solid rgba(255,255,255,0.1)', background: isScreenShared ? 'rgba(217, 70, 239, 0.1)' : 'rgba(255,255,255,0.03)', color: isScreenShared ? 'var(--neon-magenta)' : '#fff', transition: 'all 0.2s' }}
                >
                    {isScreenShared ? <MonitorSmartphone size={24} /> : <MonitorOff size={24} />}
                </button>

                <button
                    className={`btn ${isMicActive ? 'btn--mic-lg-active glow-cyan' : 'glass-btn-outline'}`}
                    onClick={onToggleMic}
                    title="Toggle Microphone (Spacebar)"
                    style={{ width: '72px', height: '72px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', border: isMicActive ? '1px solid var(--neon-cyan)' : '1px solid rgba(255,255,255,0.2)', background: isMicActive ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255,255,255,0.05)', color: isMicActive ? 'var(--neon-cyan)' : '#fff', transition: 'all 0.2s', transform: isMicActive ? 'scale(1.05)' : 'scale(1)' }}
                >
                    {isMicActive ? <Mic size={32} /> : <MicOff size={32} />}
                </button>

                <button
                    className="btn"
                    onClick={onEndBriefing}
                    title="End Session"
                    style={{ width: '56px', height: '56px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#f43f5e', transition: 'all 0.2s' }}
                >
                    <XCircle size={24} />
                </button>
            </div>
        </div>
    );
}
