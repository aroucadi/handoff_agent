/**
 * Handoff — Briefing Session Component
 *
 * Split-screen layout: ConversationPanel (left) + GraphPanel (right).
 * Manages the active voice session and passes state to child panels.
 */

import { useEffect } from 'react';
import { useVoiceSession } from '../useVoiceSession';
import ConversationPanel from './ConversationPanel';
import GraphPanel from './GraphPanel';

interface BriefingSessionProps {
    clientId: string;
    sessionId: string;
    onEnd: () => void;
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

    // Connect to WebSocket when session starts
    useEffect(() => {
        connect(sessionId);
        return () => disconnect();
    }, [sessionId, connect, disconnect]);

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

    return (
        <div className="briefing">
            <div className="briefing__status-bar">
                <div className="briefing__client">
                    <span className="briefing__client-label">Client:</span>
                    <span className="briefing__client-id">{clientId}</span>
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
