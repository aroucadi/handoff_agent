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
        <div className="briefing">
            <div className="briefing__status-bar flex justify-between items-center">
                <div className="flex items-center gap-6">
                    <div className="briefing__client">
                        <span className="briefing__client-label text-xs text-slate-500 uppercase tracking-wider block mb-1">Client</span>
                        <span className="briefing__client-id font-mono text-lg">{clientDetails?.company_name || clientId}</span>
                    </div>

                    {clientDetails?.deal_value !== undefined && clientDetails.deal_value > 0 && (
                        <div>
                            <span className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Deal Value</span>
                            <span className="font-mono text-lg text-emerald-400">${clientDetails.deal_value.toLocaleString()}</span>
                        </div>
                    )}

                    {clientDetails?.kickoff_date && (
                        <div>
                            <span className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Kickoff</span>
                            <span className="font-mono text-lg text-amber-400">
                                {Math.max(0, Math.floor((new Date(clientDetails.kickoff_date).getTime() - new Date().getTime()) / (1000 * 3600 * 24)))} Days
                            </span>
                        </div>
                    )}
                </div>
                <div className="briefing__metrics">
                    <div className="metric">
                        <span className="metric__value">{toolCalls.length}</span>
                        <span className="metric__label">Agent Actions</span>
                    </div>
                    <div className="metric">
                        <span className="metric__value">
                            {new Set([
                                currentNode,
                                ...toolCalls.filter(t => t.name === 'follow_link').map(t => t.args?.node_id)
                            ].filter(Boolean)).size}
                        </span>
                        <span className="metric__label">Nodes Visited</span>
                    </div>
                    <div className="metric">
                        <span className="metric__value">{transcript.length}</span>
                        <span className="metric__label">Messages</span>
                    </div>
                </div>
                <div className={`briefing__connection ${isConnected ? 'briefing__connection--on' : ''}`}>
                    {isConnected ? '● Connected' : '○ Disconnected'}
                </div>
            </div>

            <div className="briefing__agent-status flex justify-center gap-2 m-2">
                {agentStatus === 'listening' ? <span className="status-badge text-xs font-mono bg-cyan-900/40 text-cyan-400 px-3 py-1 rounded-full border border-cyan-500/30">⬤ Listening</span> : null}
                {agentStatus === 'thinking' ? <span className="status-badge text-xs font-mono bg-purple-900/40 text-purple-400 px-3 py-1 rounded-full border border-purple-500/30 animate-pulse">⬤ Thinking...</span> : null}
                {agentStatus === 'speaking' ? <span className="status-badge text-xs font-mono bg-emerald-900/40 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/30">🔊 Speaking</span> : null}
            </div>

            <div className="briefing__split">
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
    );
}
