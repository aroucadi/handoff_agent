import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Synapse — Conversation Panel Component
 *
 * Left side of the split-screen briefing view.
 * Shows live transcript with speaker labels, text input, and mic controls.
 */
import { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import SynapseOrb from './SynapseOrb';
import { Bot, User, Mic, MicOff, MonitorSmartphone, MonitorOff, Send, XCircle, Sparkles, Activity, FileText, Shield, HelpCircle, RefreshCw, BookOpen, Target } from 'lucide-react';
// Role-aware smart action chips
const ROLE_ACTIONS = {
    sales: [
        { label: 'Sales Script', icon: _jsx(FileText, { size: 13 }), command: 'Generate a sales call script for this client' },
        { label: 'Discovery Qs', icon: _jsx(HelpCircle, { size: 13 }), command: 'Generate discovery and qualification questions for this prospect' },
        { label: 'Action Plan', icon: _jsx(Target, { size: 13 }), command: 'Generate a post-session action plan' },
        { label: 'Briefing', icon: _jsx(BookOpen, { size: 13 }), command: 'Generate a briefing summary for this deal' },
    ],
    csm: [
        { label: 'QBR Prep', icon: _jsx(FileText, { size: 13 }), command: 'Generate a QBR discussion guide for this client' },
        { label: 'Action Plan', icon: _jsx(Target, { size: 13 }), command: 'Generate a post-session action plan' },
        { label: 'Risk Report', icon: _jsx(Shield, { size: 13 }), command: 'Generate a risk assessment report for this client' },
        { label: 'Briefing', icon: _jsx(BookOpen, { size: 13 }), command: 'Generate a briefing summary for this deal' },
    ],
    support: [
        { label: 'Support Script', icon: _jsx(FileText, { size: 13 }), command: 'Generate a customer support de-escalation script' },
        { label: 'Onboarding Guide', icon: _jsx(BookOpen, { size: 13 }), command: 'Generate an onboarding walkthrough for this client' },
        { label: 'Action Plan', icon: _jsx(Target, { size: 13 }), command: 'Generate a post-session action plan' },
        { label: 'Risk Report', icon: _jsx(Shield, { size: 13 }), command: 'Generate a risk assessment report' },
    ],
    strategy: [
        { label: 'Recommendations', icon: _jsx(Target, { size: 13 }), command: 'Generate strategic recommendations for this account' },
        { label: 'Renewal Script', icon: _jsx(RefreshCw, { size: 13 }), command: 'Generate a renewal conversation script for this client' },
        { label: 'Risk Report', icon: _jsx(Shield, { size: 13 }), command: 'Generate a risk assessment report' },
        { label: 'Discovery Qs', icon: _jsx(HelpCircle, { size: 13 }), command: 'Generate discovery questions for re-engagement' },
    ],
};
export default function ConversationPanel({ transcript, isMicActive, isScreenShared, agentStatus, sessionId, role = 'csm', onToggleMic, onToggleScreenShare, onSendText, onEndBriefing, onViewArtifacts, }) {
    const [textInput, setTextInput] = useState('');
    const transcriptEndRef = useRef(null);
    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [transcript]);
    const handleSend = useCallback(() => {
        if (!textInput.trim())
            return;
        onSendText(textInput);
        setTextInput('');
    }, [textInput, onSendText]);
    const handleKeyDown = useCallback((e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }, [handleSend]);
    // Determine current orb state
    const orbState = useMemo(() => {
        if (agentStatus === 'speaking')
            return 'speaking';
        if (agentStatus === 'thinking')
            return 'thinking';
        if (isMicActive)
            return 'listening';
        return 'idle';
    }, [agentStatus, isMicActive]);
    return (_jsxs("div", { className: "flex flex-col h-full bg-black/40 rounded-2xl overflow-hidden ring-1 ring-white/10 min-h-0", children: [_jsxs("div", { className: "flex-[0_1_auto] min-h-[160px] max-h-[240px] flex flex-col items-center justify-center border-b border-white/5 bg-radial-at-c from-primary-purple/10 to-transparent relative overflow-hidden py-4 shrink-0", children: [_jsx("div", { className: "absolute inset-0 pointer-events-none opacity-20 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]" }), _jsx("div", { className: "absolute inset-0 bg-primary-purple/5 animate-glow-pulse pointer-events-none" }), _jsx("div", { className: "scale-[1.3] mb-4 relative z-10 transition-transform duration-700", children: _jsx(SynapseOrb, { state: orbState }) }), _jsxs("div", { className: "flex flex-col items-center gap-1.5 relative z-10", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Sparkles, { size: 12, className: agentStatus === 'speaking' || agentStatus === 'thinking' ? 'text-primary-purple animate-pulse' : 'text-white/20' }), _jsx("span", { className: `text-[10px] uppercase tracking-[0.3em] font-black transition-colors ${agentStatus === 'speaking' ? 'text-emerald-400' :
                                            agentStatus === 'thinking' ? 'text-primary-purple' :
                                                isMicActive ? 'text-sky-400' : 'text-white/30'}`, children: agentStatus === 'speaking' ? 'Synapse Active' :
                                            agentStatus === 'thinking' ? 'Neural Processing' :
                                                isMicActive ? 'Voice Intercept' : 'System Standby' })] }), _jsx("div", { className: "h-[2px] w-8 bg-white/10 rounded-full" })] })] }), _jsxs("div", { className: "flex-1 overflow-y-auto p-4 flex flex-col gap-4 custom-scrollbar", children: [_jsxs("div", { className: "flex items-center justify-between mb-2", children: [_jsx("span", { className: "text-[10px] font-black uppercase tracking-widest text-white/30", children: "Intelligence Transcript" }), onViewArtifacts && (_jsxs("button", { onClick: onViewArtifacts, className: "flex items-center gap-1.5 px-2 py-1 rounded-md bg-white/5 border border-white/10 hover:bg-primary-purple/20 hover:border-primary-purple/30 text-white/40 hover:text-primary-purple transition-all group scale-90", children: [_jsx(FileText, { size: 10 }), _jsx("span", { className: "text-[9px] font-black uppercase tracking-widest", children: "Access Materials" })] })), _jsxs("span", { className: "text-[10px] font-mono text-white/15", children: ["SESS: ", sessionId.slice(-8).toUpperCase()] })] }), transcript.length === 0 && (_jsxs("div", { className: "flex flex-col items-center justify-center py-20 text-center border border-dashed border-white/5 rounded-2xl px-6", children: [_jsx(Activity, { size: 32, className: "text-white/10 mb-4 animate-pulse" }), _jsx("p", { className: "text-xs font-bold text-white/30 tracking-widest uppercase", children: "Initializing Context Matrix..." })] })), transcript.map((entry, i) => (_jsxs("div", { className: `group relative flex flex-col gap-2 p-4 rounded-xl transition-all duration-300 ${entry.role === 'agent'
                            ? 'bg-white/[0.03] border border-white/5 self-start mr-8'
                            : 'bg-primary-purple/5 border border-primary-purple/10 self-end ml-8'}`, style: { animation: 'fade-in-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards', animationDelay: `${Math.min(i * 60, 600)}ms` }, children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: `p-1.5 rounded-full ${entry.role === 'agent' ? 'bg-white/10 text-white' : 'bg-primary-purple/20 text-primary-purple'}`, children: entry.role === 'agent' ? _jsx(Bot, { size: 12 }) : _jsx(User, { size: 12 }) }), _jsx("span", { className: `text-[11px] font-black uppercase tracking-widest ${entry.role === 'agent' ? 'text-white/60' : 'text-primary-purple'}`, children: entry.role === 'agent' ? 'Synapse AI' : 'Operator' }), _jsx("span", { className: "text-[9px] font-mono text-white/20 ml-auto", children: new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) })] }), _jsx("p", { className: `text-sm leading-relaxed ${entry.role === 'agent' ? 'text-white/80 font-medium font-inter italic' : 'text-white font-bold'}`, children: entry.role === 'agent' ? `"${entry.text}"` : entry.text })] }, i))), _jsx("div", { ref: transcriptEndRef })] }), _jsx("div", { className: "shrink-0 px-4 pt-3 pb-1", children: _jsx("div", { className: "flex gap-2 overflow-x-auto scrollbar-hide pb-1", children: (ROLE_ACTIONS[role] || ROLE_ACTIONS['csm']).map((action) => (_jsxs("button", { className: "flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white/50 text-[11px] font-bold uppercase tracking-wider whitespace-nowrap hover:bg-primary-purple/20 hover:border-primary-purple/30 hover:text-primary-purple transition-all duration-300 group", onClick: () => onSendText(action.command), children: [_jsx("span", { className: "opacity-50 group-hover:opacity-100 transition-opacity", children: action.icon }), action.label] }, action.label))) }) }), _jsxs("div", { className: "shrink-0 p-4 bg-black/60 border-t border-white/5 space-y-4", children: [_jsxs("div", { className: "flex gap-3", children: [_jsx("input", { type: "text", placeholder: "Transmit intelligence protocol...", value: textInput, onChange: e => setTextInput(e.target.value), onKeyDown: handleKeyDown, className: "flex-1 bg-white/5 border border-white/10 rounded-xl px-5 py-3 text-sm font-medium text-white placeholder:text-white/20 focus:outline-none focus:border-primary-purple/50 transition-colors" }), _jsx("button", { className: "bg-primary-purple hover:bg-primary-purple/80 text-white p-3 rounded-xl transition-all disabled:opacity-20 disabled:grayscale", onClick: handleSend, disabled: !textInput.trim(), children: _jsx(Send, { size: 18 }) })] }), _jsxs("div", { className: "flex items-center justify-center gap-6 pt-1", children: [_jsx("button", { className: `w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 border ${isScreenShared
                                    ? 'bg-rose-500/20 border-rose-500/50 text-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.3)]'
                                    : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20 hover:text-white'}`, onClick: onToggleScreenShare, title: "Vision Sync", children: isScreenShared ? _jsx(MonitorSmartphone, { size: 20 }) : _jsx(MonitorOff, { size: 20 }) }), _jsx("button", { className: `w-16 h-16 rounded-full flex items-center justify-center transition-all duration-500 border-2 ${isMicActive
                                    ? 'bg-primary-purple border-primary-purple text-white shadow-[0_0_30px_rgba(123,57,252,0.5)] scale-110'
                                    : 'bg-white/5 border-white/10 text-white/20 hover:border-white/30 hover:text-white'}`, onClick: onToggleMic, title: "Voice Uplink (Space)", children: isMicActive ? _jsx(Mic, { size: 28 }) : _jsx(MicOff, { size: 28 }) }), _jsx("button", { className: "w-12 h-12 rounded-full flex items-center justify-center bg-white/5 border border-white/10 text-white/40 hover:bg-rose-500/10 hover:border-rose-500/50 hover:text-rose-500 transition-all group", onClick: onEndBriefing, title: "Terminate Session", children: _jsx(XCircle, { size: 20, className: "group-hover:rotate-90 transition-transform duration-300" }) })] })] })] }));
}
