/**
 * Synapse — Conversation Panel Component
 *
 * Left side of the split-screen briefing view.
 * Shows live transcript with speaker labels, text input, and mic controls.
 */

import { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import type { TranscriptEntry, AgentStatus } from '../useVoiceSession';
import SynapseOrb, { OrbState } from './SynapseOrb';
import { Bot, User, Mic, MicOff, MonitorSmartphone, MonitorOff, Send, XCircle, Sparkles, Activity } from 'lucide-react';

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
        <div className="flex flex-col h-full bg-black/40 rounded-2xl overflow-hidden ring-1 ring-white/10 min-h-0">
            {/* BIG Centered Orb Area */}
            <div className="flex-[0_0_auto] min-h-[180px] max-h-[280px] flex flex-col items-center justify-center border-b border-white/5 bg-radial-at-c from-primary-purple/10 to-transparent relative overflow-hidden py-8">
                <div className="absolute inset-0 pointer-events-none opacity-20 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]" />
                <div className="absolute inset-0 bg-primary-purple/5 animate-glow-pulse pointer-events-none" />
                <div className="scale-[1.6] mb-8 relative z-10 transition-transform duration-700">
                    <SynapseOrb state={orbState} />
                </div>
                <div className="flex flex-col items-center gap-1.5 relative z-10">
                    <div className="flex items-center gap-2">
                        <Sparkles size={12} className={agentStatus === 'speaking' || agentStatus === 'thinking' ? 'text-primary-purple animate-pulse' : 'text-white/20'} />
                        <span className={`text-[10px] uppercase tracking-[0.3em] font-black transition-colors ${agentStatus === 'speaking' ? 'text-emerald-400' :
                            agentStatus === 'thinking' ? 'text-primary-purple' :
                                isMicActive ? 'text-sky-400' : 'text-white/30'
                            }`}>
                            {agentStatus === 'speaking' ? 'Synapse Active' :
                                agentStatus === 'thinking' ? 'Neural Processing' :
                                    isMicActive ? 'Voice Intercept' : 'System Standby'}
                        </span>
                    </div>
                    <div className="h-[2px] w-8 bg-white/10 rounded-full" />
                </div>
            </div>

            {/* Transcript Area */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 custom-scrollbar">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-black uppercase tracking-widest text-white/30">Intelligence Transcript</span>
                    <span className="text-[10px] font-mono text-white/15">SESS: {sessionId.slice(-8).toUpperCase()}</span>
                </div>

                {transcript.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-20 text-center border border-dashed border-white/5 rounded-2xl px-6">
                        <Activity size={32} className="text-white/10 mb-4 animate-pulse" />
                        <p className="text-xs font-bold text-white/30 tracking-widest uppercase">Initializing Context Matrix...</p>
                    </div>
                )}

                {transcript.map((entry, i) => (
                    <div
                        key={i}
                        className={`group relative flex flex-col gap-2 p-4 rounded-xl transition-all duration-300 ${entry.role === 'agent'
                            ? 'bg-white/[0.03] border border-white/5 self-start mr-8'
                            : 'bg-primary-purple/5 border border-primary-purple/10 self-end ml-8'
                            }`}
                        style={{ animation: 'fade-in-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards', animationDelay: `${Math.min(i * 60, 600)}ms` }}
                    >
                        <div className="flex items-center gap-3">
                            <div className={`p-1.5 rounded-full ${entry.role === 'agent' ? 'bg-white/10 text-white' : 'bg-primary-purple/20 text-primary-purple'
                                }`}>
                                {entry.role === 'agent' ? <Bot size={12} /> : <User size={12} />}
                            </div>
                            <span className={`text-[11px] font-black uppercase tracking-widest ${entry.role === 'agent' ? 'text-white/60' : 'text-primary-purple'
                                }`}>
                                {entry.role === 'agent' ? 'Synapse AI' : 'Operator'}
                            </span>
                            <span className="text-[9px] font-mono text-white/20 ml-auto">
                                {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                            </span>
                        </div>
                        <p className={`text-sm leading-relaxed ${entry.role === 'agent' ? 'text-white/80 font-medium font-inter italic' : 'text-white font-bold'
                            }`}>
                            {entry.role === 'agent' ? `"${entry.text}"` : entry.text}
                        </p>
                    </div>
                ))}
                <div ref={transcriptEndRef} />
            </div>

            {/* Input & Controls */}
            <div className="shrink-0 p-4 bg-black/60 border-t border-white/5 space-y-4">
                <div className="flex gap-3">
                    <input
                        type="text"
                        placeholder="Transmit intelligence protocol..."
                        value={textInput}
                        onChange={e => setTextInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        className="flex-1 bg-white/5 border border-white/10 rounded-xl px-5 py-3 text-sm font-medium text-white placeholder:text-white/20 focus:outline-none focus:border-primary-purple/50 transition-colors"
                    />
                    <button
                        className="bg-primary-purple hover:bg-primary-purple/80 text-white p-3 rounded-xl transition-all disabled:opacity-20 disabled:grayscale"
                        onClick={handleSend}
                        disabled={!textInput.trim()}
                    >
                        <Send size={18} />
                    </button>
                </div>

                <div className="flex items-center justify-center gap-6 pt-1">
                    <button
                        className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 border ${isScreenShared
                            ? 'bg-rose-500/20 border-rose-500/50 text-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.3)]'
                            : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20 hover:text-white'
                            }`}
                        onClick={onToggleScreenShare}
                        title="Vision Sync"
                    >
                        {isScreenShared ? <MonitorSmartphone size={20} /> : <MonitorOff size={20} />}
                    </button>

                    <button
                        className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-500 border-2 ${isMicActive
                            ? 'bg-primary-purple border-primary-purple text-white shadow-[0_0_30px_rgba(123,57,252,0.5)] scale-110'
                            : 'bg-white/5 border-white/10 text-white/20 hover:border-white/30 hover:text-white'
                            }`}
                        onClick={onToggleMic}
                        title="Voice Uplink (Space)"
                    >
                        {isMicActive ? <Mic size={28} /> : <MicOff size={28} />}
                    </button>

                    <button
                        className="w-12 h-12 rounded-full flex items-center justify-center bg-white/5 border border-white/10 text-white/40 hover:bg-rose-500/10 hover:border-rose-500/50 hover:text-rose-500 transition-all group"
                        onClick={onEndBriefing}
                        title="Terminate Session"
                    >
                        <XCircle size={20} className="group-hover:rotate-90 transition-transform duration-300" />
                    </button>
                </div>
            </div>
        </div>
    );
}
