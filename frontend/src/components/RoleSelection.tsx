import { useEffect, useState, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { Handshake, TrendingUp, Headset, Target, ArrowRight } from 'lucide-react';
import Navbar from './Navbar';
import BackgroundVideo from './BackgroundVideo';

interface RoleDef {
    id: string;
    title: string;
    icon: ReactNode;
    desc: string;
    color: string;
    stages: string[];
    enabled: boolean;
}

const ROLES: RoleDef[] = [
    {
        id: 'csm',
        title: 'Customer Success',
        icon: <Handshake size={32} strokeWidth={1.5} />,
        desc: 'Ground every kickoff in the living memory of the deal journey.',
        color: '#7b39fc',
        stages: ['closed_won'],
        enabled: true,
    },
    {
        id: 'sales',
        title: 'Sales Intelligence',
        icon: <TrendingUp size={32} strokeWidth={1.5} />,
        desc: 'Extract deep account insights from active CRM opportunities.',
        color: '#f87b52',
        stages: ['prospecting', 'qualification', 'negotiation'],
        enabled: true,
    },
    {
        id: 'support',
        title: 'Customer Support',
        icon: <Headset size={32} strokeWidth={1.5} />,
        desc: 'Understand implementation history to resolve tickets faster.',
        color: '#10b981',
        stages: ['implemented'],
        enabled: true,
    },
    {
        id: 'strategy',
        title: 'Win-Back Analysis',
        icon: <Target size={32} strokeWidth={1.5} />,
        desc: 'Analyze competitive losses to improve product-market fit.',
        color: '#f43f5e',
        stages: ['closed_lost'],
        enabled: true,
    },
];

export default function RoleSelection() {
    const navigate = useNavigate();
    const [dealCounts, setDealCounts] = useState<Record<string, number>>({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            try {
                const baseUrl = import.meta.env.VITE_API_URL || '';
                const res = await fetch(`${baseUrl}/api/crm/deals`);
                const data = await res.json();
                const counts: Record<string, number> = {};
                for (const deal of data.deals || []) {
                    const stage = deal.stage;
                    counts[stage] = (counts[stage] || 0) + 1;
                }
                setDealCounts(counts);
            } catch {
                console.error('Failed to load deal counts');
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    const getCount = (stages: string[]) =>
        stages.reduce((sum, s) => sum + (dealCounts[s] || 0), 0);

    return (
        <div className="relative min-h-screen text-white font-manrope selection:bg-primary-purple/30">
            <BackgroundVideo
                src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4"
            />

            <Navbar />

            <main className="relative pt-[160px] pb-20 px-6 max-w-7xl mx-auto flex flex-col items-center">

                {/* Header Section */}
                <div className="text-center mb-20 animate-fade-in">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 glass-card mb-8 border-white/10">
                        <div className="w-1.5 h-1.5 bg-primary-purple rounded-full shadow-[0_0_8px_#7b39fc] animate-pulse" />
                        <span className="text-[11px] font-bold font-cabin uppercase tracking-[0.2em] text-white/60">SYNAPSE INTELLIGENCE HUB</span>
                    </div>

                    <h2 className="text-4xl md:text-[64px] font-medium font-inter tracking-tight leading-tight mb-6 text-white">
                        Select Your Mission
                    </h2>
                    <p className="text-lg text-[#f6f7f9] opacity-70 max-w-2xl mx-auto leading-relaxed font-regular">
                        Choose your role to ground the AI agent's context. Our knowledge graph dynamically transforms your CRM data into actionable intelligence.
                    </p>
                </div>

                {/* Role Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-[1280px]">
                    {ROLES.map((role) => {
                        const count = getCount(role.stages);
                        return (
                            <div
                                key={role.id}
                                className={`group relative glass-card p-8 flex flex-col gap-8 transition-all duration-500 hover:-translate-y-2 hover:border-white/30 cursor-pointer ${!role.enabled ? 'opacity-50 grayscale cursor-not-allowed' : ''}`}
                                onClick={() => role.enabled && navigate(`/dashboard?role=${role.id}`)}
                            >
                                {/* Accent Glow Overlay */}
                                <div
                                    className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-10 transition-opacity duration-500 pointer-events-none"
                                    style={{ background: `radial-gradient(circle at 50% 0%, ${role.color}, transparent 70%)` }}
                                />

                                <div
                                    className="w-14 h-14 rounded-2xl flex items-center justify-center border transition-all duration-500 group-hover:scale-110"
                                    style={{
                                        backgroundColor: `${role.color}15`,
                                        borderColor: `${role.color}30`,
                                        color: role.color
                                    }}
                                >
                                    {role.icon}
                                </div>

                                <div className="flex-1 space-y-4">
                                    <h3 className="text-xl font-bold font-inter text-white tracking-tight">{role.title}</h3>
                                    <p className="text-sm text-[#f6f7f9] opacity-50 leading-relaxed font-medium">
                                        {role.desc}
                                    </p>
                                </div>

                                <div className="pt-6 border-t border-white/5 flex items-center justify-between">
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-2xl font-bold font-cabin" style={{ color: role.color }}>
                                            {loading ? '...' : count}
                                        </span>
                                        <span className="text-[10px] font-black font-cabin uppercase tracking-widest text-white/30">
                                            Engagements
                                        </span>
                                    </div>
                                    <div className="p-2 rounded-full bg-white/5 text-white/20 group-hover:bg-primary-purple group-hover:text-white transition-all">
                                        <ArrowRight size={18} className="group-hover:translate-x-0.5 transition-transform" />
                                    </div>
                                </div>

                                {!role.enabled && (
                                    <div className="absolute top-4 right-4 bg-white/5 border border-white/10 px-3 py-1 rounded-full">
                                        <span className="text-[9px] font-bold font-cabin uppercase tracking-widest text-white/40">In Beta</span>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </main>
        </div>
    );
}
