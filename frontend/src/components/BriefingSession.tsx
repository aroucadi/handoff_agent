/**
 * Handoff — Briefing Session Component
 *
 * Split-screen layout: ConversationPanel (left) + GraphPanel (right).
 * Manages the active voice session and passes state to child panels.
 */

import { useEffect, useState } from 'react';
import { useVoiceSession } from '../useVoiceSession';
import ConversationPanel from './ConversationPanel';
import GraphPanel from './GraphPanel';

interface BriefingSessionProps {
    clientId: string;
    sessionId: string;
    onEnd: () => void;
}

interface ClientDetails {
    client_id: string;
    company_name?: string;
    deal_value?: number;
    kickoff_date?: string;
}

export default function BriefingSession({ clientId, sessionId, onEnd }: BriefingSessionProps) {
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

    const [clientDetails, setClientDetails] = useState<ClientDetails | null>(null);

    // Connect to WebSocket when session starts
    useEffect(() => {
        connect(sessionId);

        // Fetch client details for header
        const fetchClientDetails = async () => {
            try {
                const url = import.meta.env.VITE_API_URL || "http://localhost:8000";
                const res = await fetch(`${url}/api/clients`);
                const data = await res.json();
                const client = data.clients?.find((c: any) => c.client_id === clientId);
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
        onEnd();
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
                        <span className="metric__label">Tool calls</span>
                    </div>
                    <div className="metric">
                        <span className="metric__value">{new Set(toolCalls.filter(t => t.name === 'follow_link').map(t => t.args?.node_id)).size}</span>
                        <span className="metric__label">Nodes</span>
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

            <div className="briefing__split">
                <ConversationPanel
                    transcript={transcript}
                    isMicActive={isMicActive}
                    isAgentSpeaking={isAgentSpeaking}
                    sessionId={sessionId}
                    onToggleMic={toggleMic}
                    onSendText={sendText}
                    onEndBriefing={handleEnd}
                />
                <GraphPanel
                    clientId={clientId}
                    toolCalls={toolCalls}
                    currentNode={currentNode}
                />
            </div>
        </div>
    );
}
