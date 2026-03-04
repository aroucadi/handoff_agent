import { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useVoiceSession } from '../useVoiceSession';
import ConversationPanel from './ConversationPanel';
import GraphPanel from './GraphPanel';
import { Hash, MessageSquare, ShieldCheck, Activity, Users } from 'lucide-react';
import Navbar from './Navbar';
import BackgroundVideo from './BackgroundVideo';

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
    const sessionId = location.state?.sessionId || clientId;

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

    useEffect(() => {
        if (!clientId || !sessionId) {
            navigate('/dashboard');
            return;
        }

        connect(sessionId);

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
        fetchClientDetails();

        return () => disconnect();
    }, [sessionId, connect, disconnect, clientId, navigate]);

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

            <Navbar />

            <div className="relative pt-[120px] h-screen p-6 flex flex-col gap-6 animate-fade-in">

                {/* Session Top Bar: High-Fidelity Specs */}
                <header className="glass-card px-10 h-24 flex items-center justify-between shrink-0 border-white/10 ring-1 ring-white/5 backdrop-blur-2xl">
                    <div className="flex items-center gap-12">
                        <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                                <Activity size={12} className="text-primary-purple animate-pulse" />
                                <span className="text-[10px] uppercase tracking-[0.3em] text-primary-purple font-black">SYNAPSE NEXUS ACTIVE</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <ShieldCheck size={24} className="text-white/80" />
                                <h1 className="text-2xl font-bold font-inter tracking-tight">
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
                            sessionId={sessionId}
                            onToggleMic={toggleMic}
                            onToggleScreenShare={toggleScreenShare}
                            onSendText={sendText}
                            onEndBriefing={handleEnd}
                        />
                    </div>
                    <div className="flex-1">
                        <GraphPanel
                            clientId={clientId || ''}
                            toolCalls={toolCalls}
                            currentNode={currentNode}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
