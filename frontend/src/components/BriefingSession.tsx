import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useVoiceSession } from '../useVoiceSession';
import ConversationPanel from './ConversationPanel';
import GraphPanel from './GraphPanel';
import { Hash, MessageSquare, ShieldCheck, Activity, Users, Loader2 } from 'lucide-react';
import BackgroundVideo from './BackgroundVideo';

interface ClientDetails {
    client_id: string;
    company_name?: string;
    deal_value?: number;
    kickoff_date?: string;
}

export default function BriefingSession() {
    const { clientId } = useParams<{ clientId: string }>();
    const navigate = useNavigate();
    const location = useLocation();

    // Get deal context from dashboard state if available
    const dealId = location.state?.dealId;

    // session_id is now managed by a local state after calling /api/sessions/start
    const [realSessionId, setRealSessionId] = useState<string | null>(null);
    const [initializing, setInitializing] = useState(true);

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
    const hasStartedRef = useRef(false);

    useEffect(() => {
        if (!clientId) {
            navigate('/dashboard');
            return;
        }

        const fetchClientDetails = async () => {
            try {
                const url = import.meta.env.VITE_API_URL || "";
                const res = await fetch(`${url}/api/clients`);
                const data = await res.json();
                const client = data.clients?.find((c: ClientDetails) => c.client_id === clientId);
                if (client) setClientDetails(client);
            } catch (err) {
                console.error("Failed to fetch client details:", err);
            }
        };

        const initSession = async () => {
            if (hasStartedRef.current) return;
            hasStartedRef.current = true;

            try {
                const url = import.meta.env.VITE_API_URL || "";
                // Call /api/sessions/start to get a real session ID from the backend nexus
                const res = await fetch(`${url}/api/sessions/start`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        client_id: clientId,
                        deal_id: dealId,
                        role: 'csm' // Default to CSM for briefing
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    const newSid = data.session_id;
                    setRealSessionId(newSid);
                    // Connect to the WebSocket with the valid session ID
                    connect(newSid);
                } else {
                    console.error("Failed to start session nexus");
                }
            } catch (err) {
                console.error("Nexus initialization error:", err);
            } finally {
                setInitializing(false);
            }
        };

        fetchClientDetails();
        initSession();

        return () => {
            disconnect();
        };
    }, [clientId, connect, disconnect, navigate]);

    const handleEnd = () => {
        disconnect();
        navigate('/dashboard');
    };

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
        <div className="relative min-h-screen text-white font-manrope selection:bg-primary-purple/30 overflow-hidden">
            <BackgroundVideo
                src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4"
            />


            {initializing ? (
                <div className="relative h-screen flex flex-col items-center justify-center gap-8 animate-fade-in z-20">
                    <div className="relative">
                        <Loader2 className="text-primary-purple animate-spin" size={64} strokeWidth={1} />
                        <div className="absolute inset-0 bg-primary-purple/30 blur-3xl -z-10" />
                    </div>
                    <div className="text-center space-y-2">
                        <p className="text-white/30 font-bold font-inter tracking-[0.4em] uppercase text-[10px] animate-pulse">Initializing Synapse Nexus</p>
                        <p className="text-white/60 text-sm font-medium">Grounding context for {clientDetails?.company_name || clientId}...</p>
                    </div>
                </div>
            ) : (
                <div className="relative h-screen p-6 flex flex-col gap-6 animate-fade-in overflow-hidden">

                    {/* Session Top Bar: High-Fidelity Specs */}
                    <header className="glass-card px-8 h-20 flex items-center justify-between shrink-0 border-white/10 ring-1 ring-white/5 backdrop-blur-2xl">
                        <div className="flex items-center gap-12">
                            <div className="flex flex-col gap-1">
                                <div className="flex items-center gap-2 animate-pulse">
                                    <Activity size={12} className="text-primary-purple" />
                                    <span className="text-[10px] uppercase tracking-[0.3em] text-primary-purple font-black drop-shadow-[0_0_8px_rgba(123,57,252,0.4)]">SYNAPSE NEXUS ACTIVE</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <ShieldCheck size={24} className="text-white/80" />
                                    <h1 className="text-2xl font-bold font-inter tracking-tight text-gradient">
                                        {clientDetails?.company_name || clientId}
                                    </h1>
                                </div>
                            </div>

                            <div className="w-[1px] h-12 bg-white/10" />

                            <div className="flex items-center gap-10">
                                <div className="flex flex-col gap-1">
                                    <span className="text-[10px] uppercase tracking-widest text-white/30 font-black flex items-center gap-2">
                                        <MessageSquare size={10} /> Context Signals
                                    </span>
                                    <span className="text-lg font-bold font-inter tracking-tight">{transcript.length} <span className="text-[10px] text-white/40 uppercase">Tokens</span></span>
                                </div>
                                <div className="flex flex-col gap-1">
                                    <span className="text-[10px] uppercase tracking-widest text-white/30 font-black flex items-center gap-2">
                                        <Hash size={10} /> Traversed Nodes
                                    </span>
                                    <span className="text-lg font-bold font-inter tracking-tight">
                                        {new Set([currentNode, ...toolCalls.filter(t => t.name === 'follow_link').map(t => t.args?.node_id)].filter(Boolean)).size} <span className="text-[10px] text-white/40 uppercase">Layers</span>
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-8">
                            {/* Live Status Indicator */}
                            <div className="flex items-center gap-6 bg-black/40 px-6 py-3 rounded-2xl border border-white/5 shadow-inner">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500 shadow-[0_0_15px_#f43f5e]'} shadow-current`} />
                                    <span className={`text-[11px] font-black tracking-[0.2em] uppercase ${isConnected ? 'text-emerald-400' : 'text-rose-500'}`}>
                                        {isConnected ? 'Nexus Connected' : 'Nexus Severed'}
                                    </span>
                                </div>
                                <div className="w-[1px] h-4 bg-white/10" />
                                <div className="flex items-center gap-3">
                                    <Users size={14} className="text-white/40" />
                                    <span className="text-[11px] font-black tracking-[0.2em] uppercase text-white/40">Grounded Briefing</span>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Main Split Layout */}
                    <div className="flex-1 flex gap-6 min-h-0">
                        <div className="w-[480px] shrink-0">
                            <ConversationPanel
                                transcript={transcript}
                                isMicActive={isMicActive}
                                isScreenShared={isScreenShared}
                                agentStatus={agentStatus}
                                sessionId={realSessionId || ''}
                                onToggleMic={toggleMic}
                                onToggleScreenShare={toggleScreenShare}
                                onSendText={sendText}
                                onEndBriefing={handleEnd}
                            />
                        </div>
                        <div className="flex-1 min-w-0">
                            <GraphPanel
                                clientId={clientId || ''}
                                toolCalls={toolCalls}
                                currentNode={currentNode}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
