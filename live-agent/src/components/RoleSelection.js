import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Handshake, TrendingUp, Headset, Target, ArrowRight } from 'lucide-react';
import BackgroundVideo from './BackgroundVideo';
const ROLE_DEFS = {
    csm: {
        id: 'csm',
        title: 'Customer Success',
        icon: _jsx(Handshake, { size: 32, strokeWidth: 1.5 }),
        desc: 'Ground every kickoff in the living memory of the deal journey.',
        color: '#7b39fc',
        stages: ['closed_won'],
    },
    sales: {
        id: 'sales',
        title: 'Sales Intelligence',
        icon: _jsx(TrendingUp, { size: 32, strokeWidth: 1.5 }),
        desc: 'Extract deep account insights from active CRM opportunities.',
        color: '#f87b52',
        stages: ['prospecting', 'qualification', 'negotiation'],
    },
    support: {
        id: 'support',
        title: 'Customer Support',
        icon: _jsx(Headset, { size: 32, strokeWidth: 1.5 }),
        desc: 'Understand implementation history to resolve tickets faster.',
        color: '#10b981',
        stages: ['implemented'],
    },
    strategy: {
        id: 'strategy',
        title: 'Win-Back Analysis',
        icon: _jsx(Target, { size: 32, strokeWidth: 1.5 }),
        desc: 'Analyze competitive losses to improve product-market fit.',
        color: '#f43f5e',
        stages: ['closed_lost'],
    },
};
export default function RoleSelection() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const tenantId = searchParams.get('tenant_id') || localStorage.getItem('tenant_id');
    const [tenantInfo, setTenantInfo] = useState(null);
    const [dealCounts, setDealCounts] = useState({});
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        const baseUrl = import.meta.env.VITE_API_URL || '';
        const fetchData = async () => {
            try {
                // Fetch tenant info if tenant_id is provided
                if (tenantId) {
                    const token = localStorage.getItem('synapse_tenant_token');
                    const headers = {};
                    if (token)
                        headers['Authorization'] = `Bearer ${token}`;
                    const tenantRes = await fetch(`${baseUrl}/api/tenants/${tenantId}`, { headers });
                    if (tenantRes.ok) {
                        const data = await tenantRes.json();
                        setTenantInfo(data);
                    }
                }
                // Fetch deal counts (tenant-scoped if available)
                const token = localStorage.getItem('synapse_tenant_token');
                const headers = {};
                if (token)
                    headers['Authorization'] = `Bearer ${token}`;
                const dealsUrl = tenantId
                    ? `${baseUrl}/api/crm/deals?tenant_id=${tenantId}`
                    : `${baseUrl}/api/crm/deals`;
                const dealsRes = await fetch(dealsUrl, { headers });
                const dealsData = await dealsRes.json();
                const counts = {};
                for (const deal of dealsData.deals || []) {
                    const stage = deal.stage;
                    counts[stage] = (counts[stage] || 0) + 1;
                }
                setDealCounts(counts);
            }
            catch {
                console.error('Failed to load role data');
            }
            finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [tenantId]);
    // Determine which roles to show based on tenant config
    const enabledRoleIds = tenantInfo?.roles || ['csm', 'sales', 'support', 'strategy'];
    const rolesToShow = Object.values(ROLE_DEFS);
    const getCount = (stages) => stages.reduce((sum, s) => sum + (dealCounts[s] || 0), 0);
    const handleRoleSelect = (roleId) => {
        const params = new URLSearchParams();
        params.set('role', roleId);
        if (tenantId)
            params.set('tenant_id', tenantId);
        navigate(`/dashboard?${params.toString()}`);
    };
    return (_jsxs("div", { className: "relative min-h-screen text-white font-manrope selection:bg-primary-purple/30", children: [_jsx(BackgroundVideo, { src: "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4" }), _jsxs("main", { className: "relative pt-8 pb-20 px-6 max-w-7xl mx-auto flex flex-col items-center", children: [_jsxs("div", { className: "text-center mb-20 animate-fade-in", children: [_jsxs("div", { className: "inline-flex items-center gap-2 px-4 py-1.5 glass-card mb-8 border-white/10", children: [_jsx("div", { className: "w-1.5 h-1.5 bg-primary-purple rounded-full shadow-[0_0_8px_#7b39fc] animate-pulse" }), _jsx("span", { className: "text-[11px] font-bold font-cabin uppercase tracking-[0.2em] text-white/60", children: tenantInfo ? tenantInfo.brand_name || tenantInfo.name : 'SYNAPSE INTELLIGENCE HUB' })] }), _jsx("h2", { className: "text-4xl md:text-[64px] font-medium font-inter tracking-tight leading-tight mb-6 text-gradient", children: "Select Your Mission" }), _jsx("p", { className: "text-lg text-[#f6f7f9] opacity-70 max-w-2xl mx-auto leading-relaxed font-regular", children: "Choose your role to ground the AI agent's context. Our knowledge graph dynamically transforms your CRM data into actionable intelligence." })] }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-[1280px]", children: rolesToShow.map((role) => {
                            const count = getCount(role.stages);
                            const isEnabled = enabledRoleIds.includes(role.id);
                            return (_jsxs("div", { className: `group relative glass-card p-8 flex flex-col gap-8 transition-all duration-500 hover:-translate-y-2 hover:border-white/30 cursor-pointer ${!isEnabled ? 'opacity-50 grayscale cursor-not-allowed' : ''}`, onClick: () => isEnabled && handleRoleSelect(role.id), children: [_jsx("div", { className: "absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-20 transition-all duration-700 pointer-events-none", style: { background: `radial-gradient(circle at 50% 0%, ${role.color}, transparent 80%)` } }), _jsx("div", { className: "w-14 h-14 rounded-2xl flex items-center justify-center border transition-all duration-500 group-hover:scale-110", style: {
                                            backgroundColor: `${role.color}15`,
                                            borderColor: `${role.color}30`,
                                            color: role.color
                                        }, children: role.icon }), _jsxs("div", { className: "flex-1 space-y-4", children: [_jsx("h3", { className: "text-xl font-bold font-inter text-white tracking-tight", children: role.title }), _jsx("p", { className: "text-sm text-[#f6f7f9] opacity-50 leading-relaxed font-medium", children: role.desc })] }), _jsxs("div", { className: "pt-6 border-t border-white/5 flex items-center justify-between", children: [_jsxs("div", { className: "flex items-baseline gap-2", children: [_jsx("span", { className: "text-2xl font-bold font-cabin", style: { color: role.color }, children: loading ? '...' : count }), _jsx("span", { className: "text-[10px] font-black font-cabin uppercase tracking-widest text-white/30", children: "Engagements" })] }), _jsx("div", { className: "p-2 rounded-full bg-white/5 text-white/20 group-hover:bg-primary-purple group-hover:text-white transition-all", children: _jsx(ArrowRight, { size: 18, className: "group-hover:translate-x-0.5 transition-transform" }) })] }), !isEnabled && (_jsx("div", { className: "absolute top-4 right-4 bg-white/5 border border-white/10 px-3 py-1 rounded-full", children: _jsx("span", { className: "text-[9px] font-bold font-cabin uppercase tracking-widest text-white/40", children: "Not Enabled" }) }))] }, role.id));
                        }) })] })] }));
}
