/**
 * CRM Simulator — Main App Component
 *
 * Kanban-style pipeline board with deal cards.
 * Drag deals to "Closed Won" to trigger the Synapse webhook.
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

    const getDealModifier = () => {
        if (deal.stage === 'closed_won') return 'deal-card--won';
        if (deal.stage === 'closed_lost') return 'deal-card--lost';
        return '';
    };

    return (
        <div className={`deal-card ${getDealModifier()}`}>
            <div className="deal-card__header" onClick={() => setExpanded(!expanded)}>
                <div>
                    <div className="deal-card__company">💼 {deal.company_name}</div>
                    <div className="deal-card__meta">
                        {deal.industry} • {deal.contacts.length} Contacts
                    </div>
                </div>
                <span className="deal-card__value">{formatCurrency(deal.deal_value)}</span>
            </div>

            <div className="deal-card__products">
                {deal.products.map((p, i) => (
                    <span key={i} className="product-pill">{p.name}</span>
                ))}
            </div>

            {deal.webhook_fired && (
                <div className="deal-card__webhook-badge" style={{ marginTop: '8px', fontSize: '0.7rem', color: '#2e844a' }}>
                    ✅ Synapse Integrated
                </div>
            )}

            {expanded && (
                <div className="record-details">
                    <div className="detail-row">
                        <div className="detail-row__label">Account</div>
                        <div className="detail-row__value">{deal.company_name}</div>
                    </div>
                    {deal.contacts.map((c, i) => (
                        <div key={i} className="detail-row">
                            <div className="detail-row__label">Contact</div>
                            <div className="detail-row__value">
                                {c.name} <span className={`role-badge role-badge--${c.role}`}>{c.role}</span>
                                <div style={{ fontSize: '0.65rem', color: '#706e6b' }}>{c.title}</div>
                            </div>
                        </div>
                    ))}
                    {deal.risks.length > 0 && (
                        <div className="detail-row">
                            <div className="detail-row__label">Risks</div>
                            <div className="detail-row__value">
                                {deal.risks.map((r, i) => (
                                    <div key={i} style={{ color: r.severity === 'high' ? '#ea001b' : '#3e3e3c' }}>• {r.description}</div>
                                ))}
                            </div>
                        </div>
                    )}
                    {deal.sales_transcript && (
                        <div className="detail-row">
                            <div className="detail-row__label">Transcript</div>
                            <div className="detail-row__value">
                                <div style={{ fontStyle: 'italic', background: '#f3f3f3', padding: '4px', borderRadius: '4px' }}>
                                    "{deal.sales_transcript.slice(0, 100)}..."
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {available.length > 0 && (
                <div className="deal-card__actions">
                    {available.map(stage => (
                        <button
                            key={stage}
                            className={`slds-button ${stage === 'closed_won' ? 'slds-button--brand' : ''} ${stage === 'closed_lost' ? 'slds-button--destructive' : ''}`}
                            onClick={(e) => { e.stopPropagation(); onStageChange(deal.deal_id, stage); }}
                        >
                            {stage === 'closed_won' ? 'Won' : stage === 'closed_lost' ? 'Lost' : `To ${STAGE_LABELS[stage]}`}
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
    return (
        <div className="pipeline-column">
            <div className="pipeline-column__header">
                <h2 className="pipeline-column__title">{STAGE_LABELS[stage]} ({deals.length})</h2>
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
                setNotification(`🛒 SalesClaw: Deal closed! Webhook fired to Synapse. Graph generation started.`);
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
                    <div className="brand-icon">☁️</div>
                    <div>
                        <h1 className="app-header__title">SalesClaw CRM</h1>
                        <span className="app-header__subtitle">Lightning Experience • Global Sales</span>
                    </div>
                </div>
                <div className="app-header__actions">
                    <button className="slds-button" onClick={handleReset}>Refresh Records</button>
                    <div className="brand-icon" style={{ background: '#706e6b', fontSize: '0.9rem' }}>👤</div>
                </div>
            </header>

            <div className="tabs-container">
                <div className="tab-item">Home</div>
                <div className="tab-item active">Opportunities</div>
                <div className="tab-item">Accounts</div>
                <div className="tab-item">Leads</div>
                <div className="tab-item">Reports</div>
            </div>

            {notification && (
                <div className="slds-notify">{notification}</div>
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
