/**
 * Synapse — Briefing Session Component
 *
 * Split-screen layout: ConversationPanel (left) + GraphPanel (right).
 * Manages the active voice session and passes state to child panels.
 */

import { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useVoiceSession } from '../useVoiceSession';
import ConversationPanel from './ConversationPanel';
import GraphPanel from './GraphPanel';
import { Activity, Hash, MessageSquare } from 'lucide-react';

interface ClientDetails {
    client_id: string;
    company_name?: string;
    deal_value?: number;
    kickoff_date?: string;
}

export default function BriefingSession() {
    const { clientId } = useParams<{ clientId: string }>();
    const location = useLocation();
    const navigate = useNavigate();
    const sessionId = location.state?.sessionId;

    const {
        isConnected,
        isMicActive,
        isScreenShared,
        agentStatus,
        transcript,
        toolCalls,
        currentNode,
        connect,
        disconnect,
        toggleMic,
        toggleScreenShare,
        sendText,
    } = useVoiceSession();

    const [clientDetails, setClientDetails] = useState<ClientDetails | null>(null);

    // Connect to WebSocket when session starts
    useEffect(() => {
        if (!clientId || !sessionId) {
            navigate('/dashboard');
            return;
        }

        connect(sessionId);

        // Fetch client details for header
        const fetchClientDetails = async () => {
            try {
                const url = import.meta.env.VITE_API_URL || "http://localhost:8000";
                const res = await fetch(`${url}/api/clients`);
                const data = await res.json();
                const client = data.clients?.find((c: ClientDetails) => c.client_id === clientId);
                if (client) {
                    setClientDetails(client);
                }
            } catch (err) {
                console.error("Failed to fetch client details:", err);
            }
        };
        fetchClientDetails();

        return () => disconnect();
    }, [sessionId, connect, disconnect, clientId]);

    const handleEnd = () => {
        disconnect();
        navigate('/dashboard');
    };

    // Keyboard: Space to toggle mic
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

    // Keyboard: Escape to end briefing
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            if (e.code === 'Escape' && isConnected) {
                handleEnd();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [isConnected, handleEnd]);

    return (
        <div className="briefing-wrapper" style={{ minHeight: '100vh', background: '#000000', padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column' }}>
            <div className="briefing glass-card-premium" style={{ flex: 1, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 3rem)', borderRadius: '24px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)', background: 'linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)', boxShadow: '0 0 40px rgba(0,0,0,0.5)' }}>
                <div className="briefing__top-bar flex items-center justify-between" style={{ padding: '0 2rem', background: 'rgba(0,0,0,0.4)', borderBottom: '1px solid rgba(255,255,255,0.05)', height: '4.5rem', flexShrink: 0 }}>
                    <div className="flex items-center gap-6">
                        {/* Logo Area */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <div style={{ width: '28px', height: '28px', background: 'radial-gradient(circle at 30% 30%, #a855f7, #3b82f6)', borderRadius: '50%', position: 'relative', boxShadow: '0 0 15px rgba(168, 85, 247, 0.4)' }}>
                                <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '10px', height: '10px', background: '#fff', borderRadius: '50%', boxShadow: '0 0 10px #fff' }} />
                            </div>
                            <span className="font-bold text-lg tracking-tight" style={{ letterSpacing: '-0.02em' }}>Synapse Briefing</span>
                        </div>

                        <div style={{ width: '1px', height: '20px', background: 'rgba(255,255,255,0.1)' }} />

                        {/* Meta Info */}
                        <div className="flex items-center gap-6" style={{ fontSize: '0.875rem' }}>
                            <div className="flex items-center gap-2">
                                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted-sm)', textTransform: 'uppercase', letterSpacing: '0.05em' }}><Activity size={12} style={{ display: 'inline', marginRight: '4px' }} /> Client:</span>
                                <span className="font-mono text-sm">{clientDetails?.company_name || clientId}</span>
                            </div>
                            {clientDetails?.deal_value !== undefined && clientDetails.deal_value > 0 && (
                                <div className="flex items-center gap-2">
                                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted-sm)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Deal Value:</span>
                                    <span className="font-mono text-sm text-emerald-400">${((clientDetails?.deal_value || 0) / 1000).toFixed(0)}k</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-8">
                        {/* Inline Metrics */}
                        <div className="flex items-center gap-6" style={{ color: 'var(--text-muted-sm)', fontSize: '0.875rem' }}>
                            <div className="flex items-center gap-2">
                                <MessageSquare size={14} /> Messages: <span className="text-white font-mono">{transcript.length}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Hash size={14} /> Nodes Visited: <span className="text-white font-mono">
                                    {new Set([currentNode, ...toolCalls.filter(t => t.name === 'follow_link').map(t => t.args?.node_id)].filter(Boolean)).size}
                                </span>
                            </div>
                        </div>

                        {/* Connection Pill */}
                        <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold tracking-wider ${isConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                            {isConnected ? <><div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse" /> CONNECTED</> : <><div className="w-2 h-2 rounded-full bg-rose-400 shadow-[0_0_8px_#fb7185]" /> OFFLINE</>}
                        </div>
                    </div>
                </div>

                <div className="briefing__split" style={{ height: 'calc(100vh - 7.5rem)' }}>
                    <ConversationPanel
                        transcript={transcript}
                        isMicActive={isMicActive}
                        isScreenShared={isScreenShared}
                        agentStatus={agentStatus}
                        sessionId={sessionId}
                        onToggleMic={toggleMic}
                        onToggleScreenShare={toggleScreenShare}
                        onSendText={sendText}
                        onEndBriefing={handleEnd}
                    />
                    <GraphPanel
                        clientId={clientId || ''}
                        toolCalls={toolCalls}
                        currentNode={currentNode}
                    />
                </div>
            </div>
        </div>
    );
}
