import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Search,
    Filter,
    Clock,
    ArrowRight,
    Loader2,
    Database,
    Zap,
    Briefcase,
    Circle,
    Activity,
    FileText,
    Settings,
    Shield,
    Users
} from 'lucide-react';
import BackgroundVideo from './BackgroundVideo';
import ArtifactViewer from './ArtifactViewer';

interface Deal {
    id: string; // The deal_id (e.g. WON-2025-CS01)
    client_id: string; // The slug for graph lookup (e.g. precisionmetal-ltd)
    account_name: string;
    stage: string;
    amount: number;
    close_date: string;
    graph_status?: 'ready' | 'generating' | 'not_found' | 'error';
    account_details?: Record<string, unknown>;
}

const ICON_MAP: Record<string, React.ElementType> = {
    'LayoutDashboard': LayoutDashboard,
    'Zap': Zap,
    'Database': Database,
    'Briefcase': Briefcase,
    'Settings': Settings,
    'Shield': Shield,
    'Users': Users
};

const DEFAULT_ROLE_CONFIG = { title: 'Nexus Overview', subtitle: 'High-fidelity workflow monitoring', stages: ['closed_won'], icon: LayoutDashboard };

export default function Dashboard() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const roleId = searchParams.get('role') || 'csm';
    const tenantId = searchParams.get('tenant_id');
    const [deals, setDeals] = useState<Deal[]>([]);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [tenantConfig, setTenantConfig] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [artifactCounts, setArtifactCounts] = useState<Record<string, Record<string, number>>>({});
    const [viewerOpen, setViewerOpen] = useState(false);
    const [viewerClientId, setViewerClientId] = useState('');

    const roleConfig = tenantConfig?.agent?.role_views?.[roleId] || null;
    const activeRole = roleConfig ? {
        title: roleConfig.display_name,
        subtitle: `Workflow: ${roleConfig.display_name}`,
        stages: roleConfig.stage_filter || [],
        icon: ICON_MAP[roleConfig.icon] || LayoutDashboard
    } : {
        ...DEFAULT_ROLE_CONFIG,
        title: `${roleId.toUpperCase()} Overview`,
        subtitle: `Operational monitoring for ${roleId.toUpperCase()}`
    };

    const terms = {
        account: tenantConfig?.terminology_overrides?.account || 'Account',
        case: tenantConfig?.terminology_overrides?.case || 'Case'
    };

    const activeStageLabels = tenantConfig?.agent?.stage_display_config || {
        'closed_won': 'Won',
        'prospecting': 'Prospecting',
        'qualification': 'Qualifying',
        'negotiation': 'Negotiating',
        'implemented': 'Deployed',
        'closed_lost': 'Lost'
    };

    useEffect(() => {
        const fetchTenantConfig = async () => {
            if (!tenantId) return;
            try {
                const token = localStorage.getItem('synapse_tenant_token');
                const headers: Record<string, string> = {};
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const baseUrl = import.meta.env.VITE_API_URL || '';
                const res = await fetch(`${baseUrl}/api/tenants/${tenantId}`, { headers });
                if (res.ok) {
                    const data = await res.json();
                    setTenantConfig(data);
                }
            } catch (err) {
                console.error('Fetch tenant config error:', err);
            }
        };

        const fetchDeals = async () => {
            try {
                const token = localStorage.getItem('synapse_tenant_token');
                const headers: Record<string, string> = { 'X-Tenant-Id': tenantId || '' };
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const baseUrl = import.meta.env.VITE_API_URL || '';
                const url = tenantId
                    ? `${baseUrl}/api/crm/deals?tenant_id=${tenantId}`
                    : `${baseUrl}/api/crm/deals`;
                const res = await fetch(url, { headers });
                const data = await res.json();

                const filtered = (data.deals || []).filter((d: { stage: string }) =>
                    activeRole.stages.includes(d.stage)
                );

                const mapped = filtered.map((d: { deal_id?: string; id: string; client_id: string; account_name?: string; company_name: string; stage: string; amount?: number; deal_value: number; graph_ready?: boolean; close_date?: string }) => ({
                    id: d.deal_id || d.id,
                    client_id: d.client_id,
                    account_name: d.account_name || d.company_name,
                    stage: d.stage,
                    amount: d.amount || d.deal_value,
                    close_date: d.close_date || '',
                    graph_status: d.graph_ready ? 'ready' : 'generating'
                }));

                setDeals(mapped);
            } catch (err) {
                console.error('Fetch deals error:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchTenantConfig().then(fetchDeals);
    }, [roleId, activeRole.stages, tenantId]);

    // Fetch artifact counts per client
    const fetchArtifactCounts = useCallback(async (clientIds: string[]) => {
        const apiUrl = import.meta.env.VITE_API_URL || '';
        const counts: Record<string, Record<string, number>> = {};
        await Promise.all(clientIds.map(async (cid) => {
            try {
                const token = localStorage.getItem('synapse_tenant_token');
                const headers: Record<string, string> = { 'X-Tenant-Id': tenantId || '' };
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const url = tenantId
                    ? `${apiUrl}/api/clients/${cid}/outputs?tenant_id=${tenantId}`
                    : `${apiUrl}/api/clients/${cid}/outputs`;
                const res = await fetch(url, { headers });
                if (res.ok) {
                    const data = await res.json();
                    const typeCounts: Record<string, number> = {};
                    for (const o of (data.outputs || [])) {
                        if (o.is_latest !== false) {
                            typeCounts[o.type] = (typeCounts[o.type] || 0) + 1;
                        }
                    }
                    counts[cid] = typeCounts;
                }
            } catch { /* skip */ }
        }));
        setArtifactCounts(counts);
    }, []);

    useEffect(() => {
        if (deals.length > 0) {
            const clientIds = [...new Set(deals.map(d => d.client_id))];
            fetchArtifactCounts(clientIds);
        }
    }, [deals, fetchArtifactCounts]);

    const filteredDeals = deals.filter(d =>
        d.account_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="relative min-h-screen text-white font-manrope selection:bg-primary-purple/30">
            <BackgroundVideo
                src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4"
            />


            <main className="relative pt-8 pb-20 px-6 max-w-[1440px] mx-auto">

                {/* Dashboard Header Bar */}
                <div className="flex flex-col md:flex-row justify-between items-end gap-10 mb-20 animate-fade-in">
                    <div className="space-y-4">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-purple/10 border border-primary-purple/20">
                            <Activity size={12} className="text-primary-purple animate-pulse" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-primary-purple">Synapse Engine Live</span>
                        </div>
                        <div>
                            <h1 className="text-4xl md:text-5xl font-medium font-inter tracking-tight mb-2 text-gradient">{activeRole.title}</h1>
                            <p className="text-[#f6f7f9] opacity-50 font-medium">{activeRole.subtitle}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 w-full md:w-auto">
                        <div className="relative flex-1 md:w-[320px]">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30" size={18} />
                            <input
                                type="text"
                                placeholder={`Search by ${terms.account.toLowerCase()} or ID...`}
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-6 text-sm focus:outline-none focus:border-primary-purple/50 focus:ring-4 focus:ring-primary-purple/5 transition-all placeholder:text-white/20"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <button className="h-[52px] w-[52px] flex items-center justify-center glass-card hover:border-white/30 hover:bg-white/5 transition-all group">
                            <Filter size={20} className="text-white/40 group-hover:text-white" />
                        </button>
                    </div>
                </div>

                {/* Content Area */}
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-40 gap-8">
                        <div className="relative">
                            <Loader2 className="text-primary-purple animate-spin" size={64} strokeWidth={1} />
                            <div className="absolute inset-0 bg-primary-purple/20 blur-3xl -z-10" />
                        </div>
                        <p className="text-white/30 font-bold font-inter tracking-[0.3em] uppercase text-[10px] animate-pulse">Scanning Synapse nodes</p>
                    </div>
                ) : filteredDeals.length === 0 ? (
                    <div className="glass-card py-40 text-center border-dashed border-white/10">
                        <div className="w-20 h-20 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-8 border border-white/5">
                            <Search className="text-white/10" size={32} />
                        </div>
                        <h3 className="text-white/30 font-inter text-xl mb-6 font-bold">No {terms.account.toLowerCase()}s found in this nexus.</h3>
                        <button
                            className="px-8 py-3 bg-white text-black text-sm font-bold rounded-xl transition-all hover:scale-105 active:scale-95"
                            onClick={() => setSearchTerm('')}
                        >
                            Reset Search
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {filteredDeals.map((deal) => (
                            <div
                                key={deal.id}
                                className="group relative glass-card p-8 hover:border-white/30 transition-all duration-500 flex flex-col gap-8 hover:-translate-y-2"
                            >
                                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-purple/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                                <div className="relative z-10 flex justify-between items-start">
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-3">
                                            <span className="text-[10px] font-black font-cabin uppercase tracking-[0.2em] text-white/30">{deal.id}</span>
                                            <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${deal.graph_status === 'ready' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                                }`}>
                                                <div className={`w-1 h-1 rounded-full ${deal.graph_status === 'ready' ? 'bg-emerald-400' : 'bg-amber-400 animate-pulse'}`} />
                                                {deal.graph_status || 'Pending'}
                                            </div>
                                        </div>
                                        <h3 className="text-2xl font-bold font-inter group-hover:text-primary-purple transition-colors tracking-tight">{deal.account_name}</h3>
                                    </div>
                                    <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center font-bold text-2xl text-white/20 border border-white/10 group-hover:border-primary-purple/30 group-hover:text-primary-purple transition-all duration-500">
                                        {deal.account_name[0]}
                                    </div>
                                </div>

                                <div className="relative z-10 grid grid-cols-2 gap-6 py-8 border-y border-white/5">
                                    <div className="space-y-2">
                                        <p className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-white/20 font-black">
                                            <Circle size={8} className="fill-primary-purple text-primary-purple" /> {terms.case} Stage
                                        </p>
                                        <p className="text-md font-bold text-white/80">{activeStageLabels[deal.stage] || deal.stage}</p>
                                    </div>
                                    <div className="space-y-2">
                                        <p className="flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] text-white/20 font-black">
                                            <Clock size={10} className="text-white/40" /> Last Won
                                        </p>
                                        <p className="text-md font-bold text-white/80">{deal.close_date ? new Date(deal.close_date).toLocaleDateString() : 'TBD'}</p>
                                    </div>
                                </div>

                                {/* Artifact Badges */}
                                {artifactCounts[deal.client_id] && Object.keys(artifactCounts[deal.client_id]).length > 0 && (
                                    <div
                                        className="relative z-10 flex items-center gap-2 px-1 py-2 cursor-pointer group/artifacts"
                                        onClick={(e) => { e.stopPropagation(); setViewerClientId(deal.client_id); setViewerOpen(true); }}
                                    >
                                        <FileText size={12} className="text-white/20" />
                                        {Object.entries(artifactCounts[deal.client_id]).map(([type, count]) => (
                                            <span
                                                key={type}
                                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[10px] font-bold text-white/40 group-hover/artifacts:border-primary-purple/30 group-hover/artifacts:text-primary-purple/60 transition-all"
                                            >
                                                {type === 'briefing' ? '📋' : type === 'risk_report' ? '⚠️' : type === 'transcript' ? '💼' : type === 'action_plan' ? '✅' : '📄'}
                                                ×{count}
                                            </span>
                                        ))}
                                        <span className="text-[9px] text-white/20 uppercase tracking-wider group-hover/artifacts:text-primary-purple/40 transition-colors">View</span>
                                    </div>
                                )}

                                <button
                                    className="relative z-10 w-full py-4 bg-primary-purple text-white font-bold font-cabin text-sm uppercase tracking-widest rounded-xl hover:bg-primary-purple-hover shadow-lg shadow-primary-purple/20 transition-all flex items-center justify-center gap-3 group/btn hover:scale-[1.02] active:scale-95"
                                    onClick={() => {
                                        const params = new URLSearchParams();
                                        if (tenantId) params.set('tenant_id', tenantId);
                                        params.set('role', roleId);
                                        navigate(`/briefing/${deal.client_id}?${params.toString()}`, {
                                            state: {
                                                dealId: deal.id,
                                                companyName: deal.account_name
                                            }
                                        });
                                    }}
                                >
                                    Ground Context <ArrowRight size={18} className="group-hover/btn:translate-x-1 transition-transform" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </main>

            {/* Artifact Viewer Modal */}
            <ArtifactViewer
                clientId={viewerClientId}
                tenantId={tenantId}
                isOpen={viewerOpen}
                onClose={() => setViewerOpen(false)}
            />
        </div>
    );
}
