/**
 * Synapse — Role Selection Component
 *
 * Premium persona selector with glassmorphism cards.
 * Routes users to a filtered deal dashboard based on their role.
 */

import { useEffect, useState, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { Handshake, TrendingUp, Headset, Target } from 'lucide-react';

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
        desc: 'Prepare implementation kickoff briefings for won deals.',
        color: '#10b981',
        stages: ['closed_won'],
        enabled: true,
    },
    {
        id: 'sales',
        title: 'Sales',
        icon: <TrendingUp size={32} strokeWidth={1.5} />,
        desc: 'AI-assisted pipeline intelligence for active opportunities.',
        color: '#38bdf8',
        stages: ['prospecting', 'qualification', 'negotiation'],
        enabled: true,
    },
    {
        id: 'support',
        title: 'Customer Support',
        icon: <Headset size={32} strokeWidth={1.5} />,
        desc: 'Understand deployed products for ongoing client support.',
        color: '#f59e0b',
        stages: ['implemented'],
        enabled: true,
    },
    {
        id: 'strategy',
        title: 'Strategy & Win-Back',
        icon: <Target size={32} strokeWidth={1.5} />,
        desc: 'Analyze lost deals to learn from competitive failures.',
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
        <div className="role-selection" style={{ minHeight: '100vh', background: '#000000', display: 'flex', flexDirection: 'column', padding: '6rem 2rem' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', gap: '4rem' }}>
                <div className="role-selection__header" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

                    {/* Badge */}
                    <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '6px 14px',
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '20px',
                        fontSize: '13px',
                        fontWeight: 500,
                        color: '#fff',
                        marginBottom: '1.5rem'
                    }}>
                        <div style={{ width: '6px', height: '6px', background: 'var(--neon-cyan)', borderRadius: '50%', boxShadow: '0 0 10px var(--neon-cyan)' }} />
                        <span style={{ opacity: 0.8, letterSpacing: '0.05em', textTransform: 'uppercase' }}>Intelligence Hub</span>
                    </div>

                    <h2 className="role-selection__title" style={{
                        margin: 0,
                        maxWidth: '800px',
                        fontSize: 'clamp(32px, 4vw, 56px)',
                        fontWeight: 800,
                        lineHeight: 1.1,
                        letterSpacing: '-0.02em',
                        paddingBottom: '8px',
                        background: 'linear-gradient(144.5deg, rgba(255, 255, 255, 1) 28%, rgba(255, 255, 255, 0.2) 115%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        color: 'transparent'
                    }}>
                        Select Your Persona
                    </h2>
                    <p className="role-selection__subtitle" style={{ fontSize: '1.125rem', maxWidth: '540px', margin: '1rem auto 0', lineHeight: '1.6', color: 'rgba(255,255,255,0.6)' }}>
                        Choose a role to ground the Synapse agent's multimodal context. The agent dynamically adjusts its knowledge graph depending on your objective.
                    </p>
                </div>

                <div className="role-selection__grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
                    {ROLES.map((role, i) => {
                        const count = getCount(role.stages);
                        return (
                            <div
                                key={role.id}
                                className={`role-card hover-glow ${!role.enabled ? 'role-card--disabled' : ''}`}
                                style={{
                                    animationDelay: `${i * 100}ms`,
                                    '--accent-color': role.color,
                                    padding: '2.5rem 2rem',
                                    borderRadius: '24px',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: '1.5rem',
                                    position: 'relative',
                                    overflow: 'hidden',
                                    cursor: role.enabled ? 'pointer' : 'default',
                                    border: `1px solid rgba(255,255,255,0.08)`,
                                    background: `rgba(255,255,255,0.02)`,
                                    transition: 'all 0.3s ease'
                                } as React.CSSProperties}
                                onClick={() => role.enabled && navigate(`/dashboard?role=${role.id}`)}
                                onMouseEnter={(e) => {
                                    if (role.enabled) {
                                        e.currentTarget.style.borderColor = `color-mix(in srgb, ${role.color} 50%, transparent)`;
                                        e.currentTarget.style.transform = 'translateY(-2px)';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (role.enabled) {
                                        e.currentTarget.style.borderColor = `rgba(255,255,255,0.08)`;
                                        e.currentTarget.style.transform = 'translateY(0)';
                                    }
                                }}
                            >
                                <div className="role-card__glow" style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '100%', background: `radial-gradient(circle at 50% 0%, color-mix(in srgb, ${role.color} 10%, transparent), transparent 70%)`, pointerEvents: 'none' }} />

                                <div className="role-card__icon-wrap" style={{
                                    background: `color-mix(in srgb, ${role.color} 15%, transparent)`,
                                    width: '56px', height: '56px',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    borderRadius: '16px',
                                    color: role.color,
                                    border: `1px solid color-mix(in srgb, ${role.color} 30%, transparent)`
                                }}>
                                    {role.icon}
                                </div>

                                <div style={{ flex: 1, zIndex: 1 }}>
                                    <h3 className="role-card__title" style={{ color: '#fff', fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.75rem', letterSpacing: '-0.01em' }}>{role.title}</h3>
                                    <p className="role-card__desc" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.9375rem', lineHeight: '1.6', margin: 0 }}>{role.desc}</p>
                                </div>

                                <div className="role-card__footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.05)', marginTop: 'auto', zIndex: 1 }}>
                                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.375rem' }}>
                                        <span className="role-card__count font-mono" style={{ color: role.color, fontSize: '1.5rem', fontWeight: 'bold', lineHeight: 1 }}>
                                            {loading ? '...' : count}
                                        </span>
                                        <span className="role-card__count-label" style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>
                                            {count === 1 ? 'Available' : 'Available'}
                                        </span>
                                    </div>
                                    {role.enabled ? (
                                        <div style={{ color: '#fff', fontSize: '0.875rem', fontWeight: 600, opacity: 0.5 }}>Select →</div>
                                    ) : null}
                                </div>
                                {!role.enabled && (
                                    <div className="role-card__badge" style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.5)', padding: '0.375rem 0.75rem', borderRadius: '99px', fontSize: '0.7rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Coming Soon</div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
