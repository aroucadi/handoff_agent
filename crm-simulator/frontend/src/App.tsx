/**
 * CRM Simulator — Main App Component
 *
 * Kanban-style pipeline board with deal cards.
 * Drag deals to "Closed Won" to trigger the Handoff webhook.
 */

import { useEffect, useState, useCallback } from 'react';
import type { Deal, DealStage } from './types';
import { PIPELINE_STAGES, STAGE_LABELS } from './types';
import { fetchDeals, changeDealStage, resetData } from './api';

function formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}

/* ── Deal Card ──────────────────────────────────────────────────── */

function DealCard({ deal, onStageChange }: { deal: Deal; onStageChange: (dealId: string, stage: DealStage) => void }) {
    const [expanded, setExpanded] = useState(false);

    const nextStages: Partial<Record<DealStage, DealStage[]>> = {
        prospecting: ['qualification'],
        qualification: ['negotiation', 'closed_lost'],
        negotiation: ['closed_won', 'closed_lost'],
    };

    const available = nextStages[deal.stage] ?? [];

    return (
        <div className={`deal-card ${deal.webhook_fired ? 'deal-card--webhook-fired' : ''}`}>
            <div className="deal-card__header" onClick={() => setExpanded(!expanded)}>
                <h3 className="deal-card__company">{deal.company_name}</h3>
                <span className="deal-card__value">{formatCurrency(deal.deal_value)}</span>
            </div>

            <div className="deal-card__meta">
                <span className="deal-card__industry">{deal.industry}</span>
                {deal.contacts.length > 0 && (
                    <span className="deal-card__contacts">{deal.contacts.length} contacts</span>
                )}
            </div>

            {deal.products.length > 0 && (
                <div className="deal-card__products">
                    {deal.products.map((p, i) => (
                        <span key={i} className="deal-card__product-tag">{p.name}</span>
                    ))}
                </div>
            )}

            {deal.webhook_fired && (
                <div className="deal-card__webhook-badge">
                    ✅ Webhook sent to Handoff
                </div>
            )}

            {expanded && (
                <div className="deal-card__details">
                    {deal.contacts.length > 0 && (
                        <div className="deal-card__section">
                            <h4>Contacts</h4>
                            {deal.contacts.map((c, i) => (
                                <div key={i} className="deal-card__contact">
                                    <strong>{c.name}</strong> — {c.title}
                                    <span className={`role-tag role-tag--${c.role}`}>{c.role}</span>
                                    {c.pain_point && <div className="deal-card__pain">{c.pain_point}</div>}
                                </div>
                            ))}
                        </div>
                    )}

                    {deal.risks.length > 0 && (
                        <div className="deal-card__section">
                            <h4>Risks ({deal.risks.length})</h4>
                            {deal.risks.map((r, i) => (
                                <div key={i} className={`deal-card__risk risk--${r.severity}`}>
                                    {r.description}
                                </div>
                            ))}
                        </div>
                    )}

                    {deal.success_metrics.length > 0 && (
                        <div className="deal-card__section">
                            <h4>Success Metrics</h4>
                            {deal.success_metrics.map((m, i) => (
                                <div key={i} className="deal-card__metric">
                                    <strong>{m.metric}</strong>: {m.current_value} → {m.target_value}
                                    {m.timeframe && <span className="deal-card__timeframe">({m.timeframe})</span>}
                                </div>
                            ))}
                        </div>
                    )}

                    {deal.sales_transcript && (
                        <div className="deal-card__section">
                            <h4>Sales Transcript</h4>
                            <pre className="deal-card__transcript">{deal.sales_transcript.slice(0, 300)}...</pre>
                        </div>
                    )}
                </div>
            )}

            {available.length > 0 && (
                <div className="deal-card__actions">
                    {available.map(stage => (
                        <button
                            key={stage}
                            className={`stage-btn stage-btn--${stage}`}
                            onClick={(e) => { e.stopPropagation(); onStageChange(deal.deal_id, stage); }}
                        >
                            Move to {STAGE_LABELS[stage]}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}

/* ── Pipeline Column ────────────────────────────────────────────── */

function PipelineColumn({ stage, deals, onStageChange }: {
    stage: DealStage;
    deals: Deal[];
    onStageChange: (dealId: string, stage: DealStage) => void;
}) {
    const stageColors: Record<DealStage, string> = {
        prospecting: '#6366f1',
        qualification: '#8b5cf6',
        negotiation: '#f59e0b',
        closed_won: '#10b981',
        closed_lost: '#ef4444',
    };

    return (
        <div className="pipeline-column">
            <div className="pipeline-column__header" style={{ borderTopColor: stageColors[stage] }}>
                <h2 className="pipeline-column__title">{STAGE_LABELS[stage]}</h2>
                <span className="pipeline-column__count">{deals.length}</span>
            </div>
            <div className="pipeline-column__cards">
                {deals.map(deal => (
                    <DealCard key={deal.deal_id} deal={deal} onStageChange={onStageChange} />
                ))}
                {deals.length === 0 && (
                    <div className="pipeline-column__empty">No deals</div>
                )}
            </div>
        </div>
    );
}

/* ── Main App ───────────────────────────────────────────────────── */

export default function App() {
    const [deals, setDeals] = useState<Deal[]>([]);
    const [loading, setLoading] = useState(true);
    const [notification, setNotification] = useState<string | null>(null);

    const loadDeals = useCallback(async () => {
        try {
            const data = await fetchDeals();
            setDeals(data);
        } catch (err) {
            console.error('Failed to load deals:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadDeals();
    }, [loadDeals]);

    const handleStageChange = async (dealId: string, newStage: DealStage) => {
        try {
            const result = await changeDealStage(dealId, newStage);
            await loadDeals();

            if (result.webhook_fired) {
                setNotification(`🚀 Deal closed! Webhook fired to Handoff. Graph generation started.`);
                setTimeout(() => setNotification(null), 5000);
            }
        } catch (err) {
            console.error('Failed to change stage:', err);
            setNotification(`❌ Failed to update deal stage`);
            setTimeout(() => setNotification(null), 3000);
        }
    };

    const handleReset = async () => {
        await resetData();
        await loadDeals();
        setNotification('🔄 Demo data reset successfully');
        setTimeout(() => setNotification(null), 3000);
    };

    if (loading) {
        return <div className="loading">Loading CRM data...</div>;
    }

    return (
        <div className="app">
            <header className="app-header">
                <div className="app-header__brand">
                    <h1 className="app-header__title">VeloSaaS CRM</h1>
                    <span className="app-header__subtitle">Handoff Simulator</span>
                </div>
                <div className="app-header__actions">
                    <span className="app-header__deal-count">{deals.length} deals</span>
                    <button className="reset-btn" onClick={handleReset}>Reset Demo Data</button>
                </div>
            </header>

            {notification && (
                <div className="notification">{notification}</div>
            )}

            <div className="pipeline">
                {PIPELINE_STAGES.map(stage => (
                    <PipelineColumn
                        key={stage}
                        stage={stage}
                        deals={deals.filter(d => d.stage === stage)}
                        onStageChange={handleStageChange}
                    />
                ))}
            </div>
        </div>
    );
}
