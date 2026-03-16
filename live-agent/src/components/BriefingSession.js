import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useVoiceSession } from '../useVoiceSession';
import ConversationPanel from './ConversationPanel';
import GraphPanel from './GraphPanel';
import { Hash, MessageSquare, ShieldCheck, Activity, Users, Loader2, FileBox } from 'lucide-react';
import BackgroundVideo from './BackgroundVideo';
import ArtifactViewer from './ArtifactViewer';
export default function BriefingSession() {
    const { clientId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const location = useLocation();
    const tenantId = searchParams.get('tenant_id');
    const roleId = searchParams.get('role') || 'csm';
    // Get deal context from dashboard state if available
    const dealId = location.state?.dealId;
    // session_id is now managed by a local state after calling /api/sessions/start
    const [realSessionId, setRealSessionId] = useState(null);
    const [initializing, setInitializing] = useState(true);
    const [isArtifactsOpen, setIsArtifactsOpen] = useState(false);
    const { isConnected, isMicActive, isScreenShared, agentStatus, transcript, toolCalls, currentNode, connect, disconnect, toggleMic, toggleScreenShare, sendText, } = useVoiceSession();
    const [clientDetails, setClientDetails] = useState(null);
    const hasStartedRef = useRef(false);
    useEffect(() => {
        if (!clientId) {
            navigate('/dashboard');
            return;
        }
        const fetchClientDetails = async () => {
            try {
                const token = localStorage.getItem('synapse_tenant_token');
                const headers = { 'X-Tenant-Id': tenantId || '' };
                if (token)
                    headers['Authorization'] = `Bearer ${token}`;
                const url = import.meta.env.VITE_API_URL || "";
                const requestUrl = tenantId
                    ? `${url}/api/clients?tenant_id=${tenantId}`
                    : `${url}/api/clients`;
                const res = await fetch(requestUrl, { headers });
                const data = await res.json();
                const client = data.clients?.find((c) => c.client_id === clientId);
                if (client)
                    setClientDetails(client);
            }
            catch (err) {
                console.error("Failed to fetch client details:", err);
            }
        };
        const initSession = async () => {
            if (hasStartedRef.current)
                return;
            hasStartedRef.current = true;
            try {
                const token = localStorage.getItem('synapse_tenant_token');
                const headers = {
                    'Content-Type': 'application/json',
                    'X-Tenant-Id': tenantId || ''
                };
                if (token)
                    headers['Authorization'] = `Bearer ${token}`;
                const url = import.meta.env.VITE_API_URL || "";
                // Call /api/sessions/start to get a real session ID from the backend nexus
                const res = await fetch(`${url}/api/sessions/start`, {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({
                        client_id: clientId,
                        tenant_id: tenantId,
                        deal_id: dealId,
                        role: roleId
                    })
                });
                if (res.ok) {
                    const data = await res.json();
                    const newSid = data.session_id;
                    setRealSessionId(newSid);
                    // Connect to the WebSocket with the valid session ID
                    connect(newSid);
                }
                else {
                    console.error("Failed to start session nexus");
                }
            }
            catch (err) {
                console.error("Nexus initialization error:", err);
            }
            finally {
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
        const handler = (e) => {
            if (e.code === 'Space' && isConnected && e.target === document.body) {
                e.preventDefault();
                toggleMic();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [isConnected, toggleMic]);
    return (_jsxs("div", { className: "relative min-h-screen text-white font-manrope selection:bg-primary-purple/30 overflow-hidden", children: [_jsx(BackgroundVideo, { src: "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4" }), initializing ? (_jsxs("div", { className: "relative h-screen flex flex-col items-center justify-center gap-8 animate-fade-in z-20", children: [_jsxs("div", { className: "relative", children: [_jsx(Loader2, { className: "text-primary-purple animate-spin", size: 64, strokeWidth: 1 }), _jsx("div", { className: "absolute inset-0 bg-primary-purple/30 blur-3xl -z-10" })] }), _jsxs("div", { className: "text-center space-y-2", children: [_jsx("p", { className: "text-white/30 font-bold font-inter tracking-[0.4em] uppercase text-[10px] animate-pulse", children: "Initializing Synapse Nexus" }), _jsxs("p", { className: "text-white/60 text-sm font-medium", children: ["Grounding context for ", clientDetails?.company_name || clientId, "..."] })] })] })) : (_jsxs("div", { className: "relative h-screen p-6 flex flex-col gap-6 animate-fade-in overflow-hidden", children: [_jsxs("header", { className: "glass-card px-8 h-20 flex items-center justify-between shrink-0 border-white/10 ring-1 ring-white/5 backdrop-blur-2xl", children: [_jsxs("div", { className: "flex items-center gap-12", children: [_jsxs("div", { className: "flex flex-col gap-1", children: [_jsxs("div", { className: "flex items-center gap-2 animate-pulse", children: [_jsx(Activity, { size: 12, className: "text-primary-purple" }), _jsx("span", { className: "text-[10px] uppercase tracking-[0.3em] text-primary-purple font-black drop-shadow-[0_0_8px_rgba(123,57,252,0.4)]", children: "SYNAPSE NEXUS ACTIVE" })] }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsx(ShieldCheck, { size: 24, className: "text-white/80" }), _jsx("h1", { className: "text-2xl font-bold font-inter tracking-tight text-gradient", children: clientDetails?.company_name || clientId })] })] }), _jsx("div", { className: "w-[1px] h-12 bg-white/10" }), _jsxs("div", { className: "flex items-center gap-10", children: [_jsxs("div", { className: "flex flex-col gap-1", children: [_jsxs("span", { className: "text-[10px] uppercase tracking-widest text-white/30 font-black flex items-center gap-2", children: [_jsx(MessageSquare, { size: 10 }), " Context Signals"] }), _jsxs("span", { className: "text-lg font-bold font-inter tracking-tight", children: [transcript.length, " ", _jsx("span", { className: "text-[10px] text-white/40 uppercase", children: "Tokens" })] })] }), _jsxs("div", { className: "flex flex-col gap-1", children: [_jsxs("span", { className: "text-[10px] uppercase tracking-widest text-white/30 font-black flex items-center gap-2", children: [_jsx(Hash, { size: 10 }), " Traversed Nodes"] }), _jsxs("span", { className: "text-lg font-bold font-inter tracking-tight", children: [new Set([currentNode, ...toolCalls.filter(t => t.name === 'follow_link').map(t => t.args?.node_id)].filter(Boolean)).size, " ", _jsx("span", { className: "text-[10px] text-white/40 uppercase", children: "Layers" })] })] })] })] }), _jsxs("div", { className: "flex items-center gap-8", children: [_jsxs("button", { onClick: () => setIsArtifactsOpen(true), className: "flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all group", children: [_jsx(FileBox, { size: 16, className: "text-primary-purple group-hover:scale-110 transition-transform" }), _jsx("span", { className: "text-[11px] font-black uppercase tracking-widest text-white/70", children: "Materials" })] }), _jsxs("div", { className: "flex items-center gap-6 bg-black/40 px-6 py-3 rounded-2xl border border-white/5 shadow-inner", children: [_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: `w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500 shadow-[0_0_15px_#f43f5e]'} shadow-current` }), _jsx("span", { className: `text-[11px] font-black tracking-[0.2em] uppercase ${isConnected ? 'text-emerald-400' : 'text-rose-500'} `, children: isConnected ? 'Nexus Connected' : 'Nexus Severed' })] }), _jsx("div", { className: "w-[1px] h-4 bg-white/10" }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsx(Users, { size: 14, className: "text-white/40" }), _jsx("span", { className: "text-[11px] font-black tracking-[0.2em] uppercase text-white/40", children: "Grounded Briefing" })] })] })] })] }), _jsxs("div", { className: "flex-1 flex gap-6 min-h-0", children: [_jsx("div", { className: "w-[480px] shrink-0", children: _jsx(ConversationPanel, { transcript: transcript, isMicActive: isMicActive, isScreenShared: isScreenShared, agentStatus: agentStatus, sessionId: realSessionId || '', role: roleId, onToggleMic: toggleMic, onToggleScreenShare: toggleScreenShare, onSendText: sendText, onEndBriefing: handleEnd, onViewArtifacts: () => setIsArtifactsOpen(true) }) }), _jsx("div", { className: "flex-1 min-w-0", children: _jsx(GraphPanel, { clientId: clientId || '', tenantId: tenantId, toolCalls: toolCalls, currentNode: currentNode }) })] })] })), _jsx(ArtifactViewer, { clientId: clientId || '', tenantId: tenantId, isOpen: isArtifactsOpen, onClose: () => setIsArtifactsOpen(false) })] }));
}
