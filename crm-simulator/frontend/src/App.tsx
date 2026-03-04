/**
 * ClawdForce CRM — Main App Component
 *
 * Salesforce-inspired CRM with:
 * - Home dashboard with pipeline metrics
 * - Opportunities Kanban board
 * - Accounts list view
 * - Contract PDF viewer
 */

import { useEffect, useState, useCallback } from 'react';
import type { Deal, DealStage } from './types';
import { PIPELINE_STAGES, STAGE_LABELS } from './types';
import { fetchDeals, changeDealStage, resetData } from './api';
import { PremiumDashboard } from './components/PremiumDashboard';
import { AdvancedAccountsTable } from './components/AdvancedAccountsTable';

type TabId = 'home' | 'opportunities' | 'accounts' | 'leads' | 'reports';

function formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}

/* ── PDF Modal ──────────────────────────────────────────────────── */

function PdfModal({ dealId, companyName, onClose }: { dealId: string; companyName: string; onClose: () => void }) {
    return (
        <div className="pdf-modal-overlay" onClick={onClose}>
            <div className="pdf-modal" onClick={e => e.stopPropagation()}>
                <div className="pdf-modal__header">
                    <div>
                        <h3 className="pdf-modal__title">📄 Contract — {companyName}</h3>
                        <span className="pdf-modal__subtitle">{dealId}</span>
                    </div>
                    <button className="pdf-modal__close" onClick={onClose}>✕</button>
                </div>
                <iframe
                    className="pdf-modal__frame"
                    src={`/api/deals/${dealId}/contract-pdf`}
                    title={`Contract for ${companyName}`}
                />
            </div>
        </div>
    );
}

/* ── Deal Card ──────────────────────────────────────────────────── */

function DealCard({ deal, onStageChange, onViewContract }: {
    deal: Deal;
    onStageChange: (dealId: string, stage: DealStage) => void;
    onViewContract: (dealId: string, companyName: string) => void;
}) {
    const [expanded, setExpanded] = useState(false);

    const nextStages: Partial<Record<DealStage, DealStage[]>> = {
        prospecting: ['qualification'],
        qualification: ['negotiation', 'closed_lost'],
        negotiation: ['closed_won', 'closed_lost'],
        closed_won: ['implemented'],
    };

    const available = nextStages[deal.stage] ?? [];

    const getDealModifier = () => {
        if (deal.stage === 'closed_won') return 'deal-card--won';
        if (deal.stage === 'implemented') return 'deal-card--implemented';
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
                <div className="deal-card__webhook-badge">
                    ✅ Synapse Integrated
                </div>
            )}

            {expanded && (
                <div className="record-details">
                    <div className="detail-row">
                        <div className="detail-row__label">Account</div>
                        <div className="detail-row__value">{deal.company_name}</div>
                    </div>
                    <div className="detail-row">
                        <div className="detail-row__label">Deal ID</div>
                        <div className="detail-row__value" style={{ fontFamily: 'monospace', fontSize: '0.7rem' }}>{deal.deal_id}</div>
                    </div>
                    {deal.close_date && (
                        <div className="detail-row">
                            <div className="detail-row__label">Close Date</div>
                            <div className="detail-row__value">{deal.close_date}</div>
                        </div>
                    )}
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

                    {/* Contract PDF Button */}
                    <div className="detail-row" style={{ marginTop: '0.5rem' }}>
                        <div className="detail-row__label">Contract</div>
                        <div className="detail-row__value">
                            <button
                                className="slds-button slds-button--outline"
                                onClick={(e) => { e.stopPropagation(); onViewContract(deal.deal_id, deal.company_name); }}
                            >
                                📄 View Contract PDF
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {available.length > 0 && (
                <div className="deal-card__actions">
                    {available.map(stage => (
                        <button
                            key={stage}
                            className={`slds-button ${stage === 'closed_won' ? 'slds-button--brand' : ''} ${stage === 'closed_lost' ? 'slds-button--destructive' : ''}`}
                            onClick={(e) => { e.stopPropagation(); onStageChange(deal.deal_id, stage as DealStage); }}
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

function PipelineColumn({ stage, deals, onStageChange, onViewContract }: {
    stage: DealStage;
    deals: Deal[];
    onStageChange: (dealId: string, stage: DealStage) => void;
    onViewContract: (dealId: string, companyName: string) => void;
}) {
    return (
        <div className="pipeline-column">
            <div className="pipeline-column__header">
                <h2 className="pipeline-column__title">{STAGE_LABELS[stage]} ({deals.length})</h2>
            </div>
            <div className="pipeline-column__cards">
                {deals.map(deal => (
                    <DealCard key={deal.deal_id} deal={deal} onStageChange={onStageChange} onViewContract={onViewContract} />
                ))}
                {deals.length === 0 && (
                    <div className="pipeline-column__empty">No deals</div>
                )}
            </div>
        </div>
    );
}

// DEPRECATED: Basic components replaced by Premium Stitch versions

/* ── Coming Soon Stub ───────────────────────────────────────────── */

function ComingSoon({ title, icon }: { title: string; icon: string }) {
    return (
        <div className="coming-soon">
            <div className="coming-soon__icon">{icon}</div>
            <h2 className="coming-soon__title">{title}</h2>
            <p className="coming-soon__text">This module is coming soon to ClawdForce CRM.</p>
            <span className="coming-soon__badge">Lightning Experience</span>
        </div>
    );
}

/* ── Main App ───────────────────────────────────────────────────── */

const TABS: { id: TabId; label: string; icon: string }[] = [
    { id: 'home', label: 'Home', icon: '🏠' },
    { id: 'opportunities', label: 'Opportunities', icon: '💰' },
    { id: 'accounts', label: 'Accounts', icon: '🏢' },
    { id: 'leads', label: 'Leads', icon: '🎯' },
    { id: 'reports', label: 'Reports', icon: '📊' },
];

export default function App() {
    const [deals, setDeals] = useState<Deal[]>([]);
    const [loading, setLoading] = useState(true);
    const [notification, setNotification] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<TabId>('home');
    const [pdfModal, setPdfModal] = useState<{ dealId: string; companyName: string } | null>(null);

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
                setNotification(`🛒 ClawdForce: Deal closed! Webhook fired to Synapse. Graph generation started.`);
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

    const handleViewContract = (dealId: string, companyName: string) => {
        setPdfModal({ dealId, companyName });
    };

    if (loading) {
        return (
            <div className="loading">
                <div className="loading__spinner" />
                <span>Loading ClawdForce CRM...</span>
            </div>
        );
    }

    return (
        <div className="app">
            {/* ── Global Header ─── */}
            <header className="app-header">
                <div className="app-header__brand">
                    <div className="brand-icon">☁️</div>
                    <div>
                        <h1 className="app-header__title">ClawdForce</h1>
                        <span className="app-header__subtitle">Lightning Experience • Global Sales</span>
                    </div>
                </div>
                <div className="app-header__nav">
                    <div className="header-search">
                        <span className="header-search__icon">🔍</span>
                        <input className="header-search__input" placeholder="Search ClawdForce..." readOnly />
                    </div>
                </div>
                <div className="app-header__actions">
                    <button className="slds-button slds-button--icon" title="Notifications">🔔</button>
                    <button className="slds-button" onClick={handleReset}>Reset Demo</button>
                    <div className="avatar">
                        <span>AE</span>
                    </div>
                </div>
            </header>

            {/* ── Tab Bar ─── */}
            <div className="tabs-container">
                {TABS.map(tab => (
                    <div
                        key={tab.id}
                        className={`tab-item ${activeTab === tab.id ? 'active' : ''} ${tab.id === 'leads' || tab.id === 'reports' ? 'tab-item--muted' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span className="tab-item__icon">{tab.icon}</span>
                        {tab.label}
                    </div>
                ))}
            </div>

            {/* ── Notification Toast ─── */}
            {notification && (
                <div className="slds-notify">{notification}</div>
            )}

            {/* ── Tab Content ─── */}
            <div className="tab-content">
                {activeTab === 'home' && <PremiumDashboard deals={deals} />}
                {activeTab === 'opportunities' && (
                    <div className="pipeline">
                        {PIPELINE_STAGES.map(stage => (
                            <PipelineColumn
                                key={stage}
                                stage={stage}
                                deals={deals.filter(d => d.stage === stage)}
                                onStageChange={handleStageChange}
                                onViewContract={handleViewContract}
                            />
                        ))}
                    </div>
                )}
                {activeTab === 'accounts' && <AdvancedAccountsTable deals={deals} onViewContract={handleViewContract} />}
                {activeTab === 'leads' && <ComingSoon title="Leads" icon="🎯" />}
                {activeTab === 'reports' && <ComingSoon title="Reports & Dashboards" icon="📊" />}
            </div>

            {/* ── PDF Modal ─── */}
            {pdfModal && (
                <PdfModal
                    dealId={pdfModal.dealId}
                    companyName={pdfModal.companyName}
                    onClose={() => setPdfModal(null)}
                />
            )}
        </div>
    );
}
