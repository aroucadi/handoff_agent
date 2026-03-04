/**
 * Synapse — Dashboard Component (Role-Filtered)
 *
 * Shows deals filtered by the user's selected role.
 * Premium glassmorphism cards with animated status indicators.
 */

import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { audioStreamer } from '../infrastructure/audio/AudioStreamer';
import { CheckCircle2, Clock, ClipboardList, Mic, ArrowLeft, Network } from 'lucide-react';

interface CrmDeal {
    deal_id: string;
    company_name: string;
    deal_value: number;
    stage: string;
    products: { name: string; annual_value?: number }[];
    industry: string;
    client_id: string;
    graph_ready: boolean;
    node_count: number;
}

const ROLE_CONFIG: Record<string, { title: string; subtitle: string; stages: string[]; color: string }> = {
    csm: {
        title: 'CSM Briefing Center',
        subtitle: 'Won deals ready for implementation kickoff',
        stages: ['closed_won'],
        color: '#10b981',
    },
    sales: {
        title: 'Sales Intelligence Hub',
        subtitle: 'Active pipeline opportunities with AI insights',
        stages: ['prospecting', 'qualification', 'negotiation'],
        color: '#38bdf8',
    },
    support: {
        title: 'Support Knowledge Base',
        subtitle: 'Deployed products and implementation context',
        stages: ['implemented'],
        color: '#f59e0b',
    },
    strategy: {
        title: 'Win-Back Analysis',
        subtitle: 'Lost deals — learn from competitive failures',
        stages: ['closed_lost'],
        color: '#f43f5e',
    },
};

const STAGE_LABELS: Record<string, string> = {
    prospecting: 'Prospecting',
    qualification: 'Qualification',
    negotiation: 'Negotiation',
    closed_won: 'Won',
    closed_lost: 'Lost',
    implemented: 'Implemented',
};

export default function Dashboard() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const role = searchParams.get('role') || 'csm';
    const roleConfig = ROLE_CONFIG[role] || ROLE_CONFIG.csm;

    const [deals, setDeals] = useState<CrmDeal[]>([]);
    const [loading, setLoading] = useState(true);

    const loadDeals = useCallback(async () => {
        try {
            const baseUrl = import.meta.env.VITE_API_URL || '';
            const res = await fetch(`${baseUrl}/api/crm/deals`);
            const data = await res.json();
            const allDeals: CrmDeal[] = data.deals || [];
            // Filter by the stages for the current role
            setDeals(allDeals.filter(d => roleConfig.stages.includes(d.stage)));
        } catch {
            console.error('Failed to load deals');
        } finally {
            setLoading(false);
        }
    }, [roleConfig.stages]);

    const handleStartBriefing = async (deal: CrmDeal) => {
        try {
            audioStreamer.unlock();

            const baseUrl = import.meta.env.VITE_API_URL || '';
            const res = await fetch(`${baseUrl}/api/sessions/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    client_id: deal.client_id,
                    csm_name: 'CSM',
                    deal_id: deal.deal_id,
                    role: role,
                }),
            });
            const data = await res.json();
            navigate(`/session/${deal.client_id}`, { state: { sessionId: data.session_id, dealId: deal.deal_id } });
        } catch (err) {
            console.error('Failed to start session:', err);
        }
    };

    useEffect(() => {
        setLoading(true);
        loadDeals();
        const interval = setInterval(loadDeals, 8000);
        return () => clearInterval(interval);
    }, [loadDeals]);

    return (
        <div className="dashboard" style={{ minHeight: '100vh', background: '#000000', padding: '4rem 2rem', display: 'flex', flexDirection: 'column' }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                <div className="dashboard__header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '2rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <div className="dashboard__role-badge" style={{ color: roleConfig.color, borderColor: roleConfig.color, display: 'inline-flex', padding: '0.25rem 0.75rem', borderRadius: '99px', fontSize: '0.75rem', fontWeight: 'bold', letterSpacing: '0.05em', background: `color-mix(in srgb, ${roleConfig.color} 10%, transparent)` }}>
                            {role.toUpperCase()}
                        </div>
                        <h2 className="dashboard__title" style={{ fontSize: '2.5rem', fontWeight: '800', letterSpacing: '-0.02em', margin: 0, background: 'linear-gradient(144.5deg, rgba(255, 255, 255, 1) 28%, rgba(255, 255, 255, 0.2) 115%)', color: '#fff', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                            {roleConfig.title}
                        </h2>
                        <p className="dashboard__subtitle text-premium-muted" style={{ fontSize: '1.2rem', margin: 0, color: 'rgba(255,255,255,0.6)' }}>{roleConfig.subtitle}</p>
                    </div>
                    <div className="dashboard__stats" style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                        <div className="stat" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                            <span className="stat__value" style={{ fontSize: '2.5rem', fontWeight: '800', lineHeight: 1 }}>{deals.length}</span>
                            <span className="stat__label" style={{ color: 'var(--text-muted-sm)', fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '500', marginTop: '0.25rem' }}>Deals</span>
                        </div>
                        <div className="stat" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', paddingRight: '2rem', borderRight: '1px solid rgba(255,255,255,0.1)' }}>
                            <span className="stat__value" style={{ fontSize: '2.5rem', fontWeight: '800', lineHeight: 1, color: 'var(--neon-cyan)' }}>{deals.filter(d => d.graph_ready).length}</span>
                            <span className="stat__label" style={{ color: 'var(--text-muted-sm)', fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '500', marginTop: '0.25rem' }}>Graph Ready</span>
                        </div>
                        <button
                            className="btn btn--nav hover-glow"
                            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', borderRadius: '99px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', fontSize: '0.875rem', fontWeight: '600', transition: 'all 0.2s' }}
                            onClick={() => navigate('/roles')}
                        >
                            <ArrowLeft size={16} /> Persona Select
                        </button>
                    </div>
                </div>

                <div className="dashboard__grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '2rem' }}>
                    {loading && (
                        <div className="dashboard__loading">
                            <div className="spinner" />
                            <span>Loading...</span>
                        </div>
                    )}

                    {!loading && deals.length === 0 && (
                        <div className="dashboard__empty" style={{ gridColumn: '1 / -1', padding: '6rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', borderRadius: '24px', border: '1px dashed rgba(255,255,255,0.1)', background: 'transparent' }}>
                            <div className="dashboard__empty-icon" style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', padding: '1.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '50%' }}>
                                <ClipboardList size={48} strokeWidth={1.5} />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '0.5rem' }}>No Intelligence Available</h3>
                            <p style={{ color: 'rgba(255,255,255,0.5)' }}>Try selecting a different persona to populate the graph context.</p>
                        </div>
                    )}

                    {deals.map((deal, i) => (
                        <div
                            key={deal.deal_id}
                            className={`account-card hover-glow ${deal.graph_ready ? 'account-card--ready' : ''}`}
                            style={{
                                animationDelay: `${i * 80}ms`,
                                padding: '2rem',
                                display: 'flex',
                                flexDirection: 'column',
                                borderRadius: '20px',
                                position: 'relative',
                                overflow: 'hidden',
                                background: 'rgba(255,255,255,0.02)',
                                border: '1px solid rgba(255,255,255,0.08)',
                                transition: 'all 0.3s ease'
                            }}
                        >
                            {deal.graph_ready && <div className="account-card__glow" style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '100%', background: 'radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.05), transparent 60%)', pointerEvents: 'none' }} />}

                            <div className="account-card__header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', zIndex: 1 }}>
                                <div className={`account-card__status ${deal.graph_ready ? 'status--ready' : 'status--not_found'}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '0.375rem 0.875rem', borderRadius: '99px', background: deal.graph_ready ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)', color: deal.graph_ready ? '#10b981' : '#f59e0b', border: `1px solid ${deal.graph_ready ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)'}` }}>
                                    {deal.graph_ready ? <CheckCircle2 size={14} /> : <Clock size={14} />}
                                    <span>{deal.graph_ready ? 'Graph Ready' : 'Pending'}</span>
                                </div>
                                <span className="account-card__nodes" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.8125rem', color: 'rgba(255,255,255,0.5)', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', padding: '0.25rem 0.75rem', borderRadius: '99px' }}>
                                    <Network size={14} /> {deal.node_count} nodes
                                </span>
                            </div>

                            <h3 className="account-card__id" style={{ fontSize: '1.25rem', fontWeight: '700', color: '#fff', marginBottom: '0.25rem', letterSpacing: '-0.01em', zIndex: 1 }}>{deal.company_name}</h3>
                            <p className="account-card__subtitle" style={{ fontSize: '0.875rem', fontFamily: 'monospace', color: 'rgba(255,255,255,0.4)', zIndex: 1, margin: 0 }}>
                                {deal.deal_id}
                            </p>

                            <div className="account-card__deal-info" style={{ marginTop: '1.5rem', marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', zIndex: 1 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                    <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Stage</span>
                                    <span style={{ color: roleConfig.color, fontWeight: '600', fontSize: '0.875rem' }}>
                                        {STAGE_LABELS[deal.stage] || deal.stage}
                                    </span>
                                </div>
                                {deal.deal_value > 0 && (
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                        <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Value</span>
                                        <span style={{ color: '#fff', fontWeight: '600', fontSize: '0.875rem' }}>${deal.deal_value.toLocaleString()}</span>
                                    </div>
                                )}
                                {deal.products?.length > 0 && (
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                                        {deal.products.map((p, j) => (
                                            <span key={j} style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.8)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>{p.name}</span>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <button
                                className={`btn ${deal.graph_ready ? 'glow-cyan' : ''}`}
                                disabled={!deal.graph_ready}
                                onClick={() => handleStartBriefing(deal)}
                                style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', width: '100%', padding: '1rem', marginTop: 'auto', borderRadius: '12px', fontSize: '1rem', fontWeight: '600', background: deal.graph_ready ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255,255,255,0.03)', color: deal.graph_ready ? '#38bdf8' : 'rgba(255,255,255,0.3)', border: deal.graph_ready ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid rgba(255,255,255,0.05)', zIndex: 1, cursor: deal.graph_ready ? 'pointer' : 'not-allowed', transition: 'all 0.2s' }}
                            >
                                {deal.graph_ready ? <><Mic size={18} /> Synapse Voice</> : <><Clock size={18} /> Processing Context</>}
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
