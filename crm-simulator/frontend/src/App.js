import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
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
import { PIPELINE_STAGES, STAGE_LABELS } from './types';
import { fetchDeals, changeDealStage, resetData, importTemplate } from './api';
import { PremiumDashboard } from './components/PremiumDashboard';
import { AdvancedAccountsTable } from './components/AdvancedAccountsTable';
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}
/* ── PDF Modal ──────────────────────────────────────────────────── */
function PdfModal({ dealId, companyName, onClose }) {
    return (_jsx("div", { className: "pdf-modal-overlay", onClick: onClose, children: _jsxs("div", { className: "pdf-modal", onClick: e => e.stopPropagation(), children: [_jsxs("div", { className: "pdf-modal__header", children: [_jsxs("div", { children: [_jsxs("h3", { className: "pdf-modal__title", children: ["\uD83D\uDCC4 Contract \u2014 ", companyName] }), _jsx("span", { className: "pdf-modal__subtitle", children: dealId })] }), _jsx("button", { className: "pdf-modal__close", onClick: onClose, children: "\u2715" })] }), _jsx("iframe", { className: "pdf-modal__frame", src: `/api/deals/${dealId}/contract-pdf`, title: `Contract for ${companyName}` })] }) }));
}
/* ── Deal Card ──────────────────────────────────────────────────── */
function DealCard({ deal, onStageChange, onViewContract }) {
    const [expanded, setExpanded] = useState(false);
    const nextStages = {
        prospecting: ['qualification'],
        qualification: ['negotiation', 'closed_lost'],
        negotiation: ['closed_won', 'closed_lost'],
        closed_won: ['implemented'],
    };
    const available = nextStages[deal.stage] ?? [];
    const getDealModifier = () => {
        if (deal.stage === 'closed_won')
            return 'deal-card--won';
        if (deal.stage === 'implemented')
            return 'deal-card--implemented';
        if (deal.stage === 'closed_lost')
            return 'deal-card--lost';
        return '';
    };
    return (_jsxs("div", { className: `deal-card ${getDealModifier()}`, children: [_jsxs("div", { className: "deal-card__header", onClick: () => setExpanded(!expanded), children: [_jsxs("div", { children: [_jsxs("div", { className: "deal-card__company", children: ["\uD83D\uDCBC ", deal.company_name] }), _jsxs("div", { className: "deal-card__meta", children: [deal.industry, " \u2022 ", deal.contacts.length, " Contacts"] })] }), _jsx("span", { className: "deal-card__value", children: formatCurrency(deal.deal_value) })] }), _jsx("div", { className: "deal-card__products", children: deal.products.map((p, i) => (_jsx("span", { className: "product-pill", children: p.name }, i))) }), deal.webhook_fired && (_jsx("div", { className: "deal-card__webhook-badge", children: "\u2705 Synapse Integrated" })), expanded && (_jsxs("div", { className: "record-details", children: [_jsxs("div", { className: "detail-row", children: [_jsx("div", { className: "detail-row__label", children: "Account" }), _jsx("div", { className: "detail-row__value", children: deal.company_name })] }), _jsxs("div", { className: "detail-row", children: [_jsx("div", { className: "detail-row__label", children: "Deal ID" }), _jsx("div", { className: "detail-row__value", style: { fontFamily: 'monospace', fontSize: '0.7rem' }, children: deal.deal_id })] }), deal.close_date && (_jsxs("div", { className: "detail-row", children: [_jsx("div", { className: "detail-row__label", children: "Close Date" }), _jsx("div", { className: "detail-row__value", children: deal.close_date })] })), deal.contacts.map((c, i) => (_jsxs("div", { className: "detail-row", children: [_jsx("div", { className: "detail-row__label", children: "Contact" }), _jsxs("div", { className: "detail-row__value", children: [c.name, " ", _jsx("span", { className: `role-badge role-badge--${c.role}`, children: c.role }), _jsx("div", { style: { fontSize: '0.65rem', color: '#706e6b' }, children: c.title })] })] }, i))), deal.risks.length > 0 && (_jsxs("div", { className: "detail-row", children: [_jsx("div", { className: "detail-row__label", children: "Risks" }), _jsx("div", { className: "detail-row__value", children: deal.risks.map((r, i) => (_jsxs("div", { style: { color: r.severity === 'high' ? '#ea001b' : '#3e3e3c' }, children: ["\u2022 ", r.description] }, i))) })] })), deal.sales_transcript && (_jsxs("div", { className: "detail-row", children: [_jsx("div", { className: "detail-row__label", children: "Transcript" }), _jsx("div", { className: "detail-row__value", children: _jsxs("div", { style: { fontStyle: 'italic', background: '#f3f3f3', padding: '4px', borderRadius: '4px' }, children: ["\"", deal.sales_transcript.slice(0, 100), "...\""] }) })] })), _jsxs("div", { className: "detail-row", style: { marginTop: '0.5rem' }, children: [_jsx("div", { className: "detail-row__label", children: "Contract" }), _jsx("div", { className: "detail-row__value", children: _jsx("button", { className: "slds-button slds-button--outline", onClick: (e) => { e.stopPropagation(); onViewContract(deal.deal_id, deal.company_name); }, children: "\uD83D\uDCC4 View Contract PDF" }) })] })] })), available.length > 0 && (_jsx("div", { className: "deal-card__actions", children: available.map(stage => (_jsx("button", { className: `slds-button ${stage === 'closed_won' ? 'slds-button--brand' : ''} ${stage === 'closed_lost' ? 'slds-button--destructive' : ''}`, onClick: (e) => { e.stopPropagation(); onStageChange(deal.deal_id, stage); }, children: stage === 'closed_won' ? 'Won' : stage === 'closed_lost' ? 'Lost' : `To ${STAGE_LABELS[stage]}` }, stage))) }))] }));
}
/* ── Pipeline Column ────────────────────────────────────────────── */
function PipelineColumn({ stage, deals, onStageChange, onViewContract }) {
    return (_jsxs("div", { className: "pipeline-column", children: [_jsx("div", { className: "pipeline-column__header", children: _jsxs("h2", { className: "pipeline-column__title", children: [STAGE_LABELS[stage], " (", deals.length, ")"] }) }), _jsxs("div", { className: "pipeline-column__cards", children: [deals.map(deal => (_jsx(DealCard, { deal: deal, onStageChange: onStageChange, onViewContract: onViewContract }, deal.deal_id))), deals.length === 0 && (_jsx("div", { className: "pipeline-column__empty", children: "No deals" }))] })] }));
}
// DEPRECATED: Basic components replaced by Premium Stitch versions
/* ── Coming Soon Stub ───────────────────────────────────────────── */
function ComingSoon({ title, icon }) {
    return (_jsxs("div", { className: "coming-soon", children: [_jsx("div", { className: "coming-soon__icon", children: icon }), _jsx("h2", { className: "coming-soon__title", children: title }), _jsx("p", { className: "coming-soon__text", children: "This module is coming soon to ClawdForce CRM." }), _jsx("span", { className: "coming-soon__badge", children: "Lightning Experience" })] }));
}
/* ── Main App ───────────────────────────────────────────────────── */
const TABS = [
    { id: 'home', label: 'Home', icon: '🏠' },
    { id: 'opportunities', label: 'Opportunities', icon: '💰' },
    { id: 'accounts', label: 'Accounts', icon: '🏢' },
    { id: 'leads', label: 'Leads', icon: '🎯' },
    { id: 'reports', label: 'Reports', icon: '📊' },
];
export default function App() {
    const [deals, setDeals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [notification, setNotification] = useState(null);
    const [activeTab, setActiveTab] = useState('home');
    const [pdfModal, setPdfModal] = useState(null);
    const loadDeals = useCallback(async () => {
        try {
            const data = await fetchDeals();
            setDeals(data);
        }
        catch (err) {
            console.error('Failed to load deals:', err);
        }
        finally {
            setLoading(false);
        }
    }, []);
    useEffect(() => {
        loadDeals();
    }, [loadDeals]);
    const handleStageChange = async (dealId, newStage) => {
        try {
            const result = await changeDealStage(dealId, newStage);
            await loadDeals();
            if (result.webhook_fired) {
                setNotification(`🛒 ClawdForce: Deal closed! Webhook fired to Synapse. Graph generation started.`);
                setTimeout(() => setNotification(null), 5000);
            }
        }
        catch (err) {
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
    const handleImportDeal = async (templateId) => {
        try {
            const menu = document.getElementById('import-menu');
            if (menu)
                menu.style.display = 'none';
            setNotification(`⏳ Importing ${templateId.replace('_', ' ')}...`);
            await importTemplate(templateId);
            await loadDeals();
            setActiveTab('opportunities');
            setNotification('✅ Demo deal imported to Prospecting!');
            setTimeout(() => setNotification(null), 3000);
        }
        catch (err) {
            console.error('Failed to import deal:', err);
            setNotification('❌ Failed to import demo deal');
            setTimeout(() => setNotification(null), 3000);
        }
    };
    // Global toggle for the menu (simple approach for demo app)
    useEffect(() => {
        window.toggleImportMenu = () => {
            const menu = document.getElementById('import-menu');
            if (menu) {
                menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
            }
        };
    }, []);
    const handleViewContract = (dealId, companyName) => {
        setPdfModal({ dealId, companyName });
    };
    if (loading) {
        return (_jsxs("div", { className: "loading", children: [_jsx("div", { className: "loading__spinner" }), _jsx("span", { children: "Loading ClawdForce CRM..." })] }));
    }
    return (_jsxs("div", { className: "app", children: [_jsxs("header", { className: "app-header", children: [_jsxs("div", { className: "app-header__brand", children: [_jsx("div", { className: "brand-icon", children: "\u2601\uFE0F" }), _jsxs("div", { children: [_jsx("h1", { className: "app-header__title", children: "ClawdForce" }), _jsx("span", { className: "app-header__subtitle", children: "Lightning Experience \u2022 Global Sales" })] })] }), _jsx("div", { className: "app-header__nav", children: _jsxs("div", { className: "header-search", children: [_jsx("span", { className: "header-search__icon", children: "\uD83D\uDD0D" }), _jsx("input", { className: "header-search__input", placeholder: "Search ClawdForce...", readOnly: true })] }) }), _jsxs("div", { className: "app-header__actions", children: [_jsx("button", { className: "slds-button slds-button--icon", title: "Notifications", children: "\uD83D\uDD14" }), _jsxs("div", { className: "import-menu-container", style: { position: 'relative', display: 'inline-block' }, children: [_jsx("button", { className: "slds-button slds-button--brand", onClick: () => window.toggleImportMenu(), children: "\uD83D\uDCE5 Import Demo Deal" }), _jsxs("div", { id: "import-menu", className: "import-menu", style: { display: 'none', position: 'absolute', top: '100%', right: 0, background: 'white', border: '1px solid #dddbda', borderRadius: '4px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)', zIndex: 1000, width: '220px', marginTop: '4px' }, children: [_jsxs("div", { className: "import-menu__item", onClick: () => handleImportDeal('aerospace_expansion'), style: { padding: '8px 12px', cursor: 'pointer', borderBottom: '1px solid #f3f3f3' }, children: [_jsx("div", { style: { fontWeight: 'bold', fontSize: '0.85rem' }, children: "Aerospace Expansion" }), _jsx("div", { style: { fontSize: '0.7rem', color: '#706e6b' }, children: "$2.4M \u2022 PrecisionMetal Ltd" })] }), _jsxs("div", { className: "import-menu__item", onClick: () => handleImportDeal('biotech_onboarding'), style: { padding: '8px 12px', cursor: 'pointer' }, children: [_jsx("div", { style: { fontWeight: 'bold', fontSize: '0.85rem' }, children: "Biotech Onboarding" }), _jsx("div", { style: { fontSize: '0.7rem', color: '#706e6b' }, children: "$1.2M \u2022 BioSynth Labs" })] })] })] }), _jsx("button", { className: "slds-button", onClick: handleReset, children: "Reset Demo" }), _jsx("div", { className: "avatar", children: _jsx("span", { children: "AE" }) })] })] }), _jsx("div", { className: "tabs-container", children: TABS.map(tab => (_jsxs("div", { className: `tab-item ${activeTab === tab.id ? 'active' : ''} ${tab.id === 'leads' || tab.id === 'reports' ? 'tab-item--muted' : ''}`, onClick: () => setActiveTab(tab.id), children: [_jsx("span", { className: "tab-item__icon", children: tab.icon }), tab.label] }, tab.id))) }), notification && (_jsx("div", { className: "slds-notify", children: notification })), _jsxs("div", { className: "tab-content", children: [activeTab === 'home' && _jsx(PremiumDashboard, { deals: deals }), activeTab === 'opportunities' && (_jsx("div", { className: "pipeline", children: PIPELINE_STAGES.map(stage => (_jsx(PipelineColumn, { stage: stage, deals: deals.filter(d => d.stage === stage), onStageChange: handleStageChange, onViewContract: handleViewContract }, stage))) })), activeTab === 'accounts' && _jsx(AdvancedAccountsTable, { deals: deals, onViewContract: handleViewContract }), activeTab === 'leads' && _jsx(ComingSoon, { title: "Leads", icon: "\uD83C\uDFAF" }), activeTab === 'reports' && _jsx(ComingSoon, { title: "Reports & Dashboards", icon: "\uD83D\uDCCA" })] }), pdfModal && (_jsx(PdfModal, { dealId: pdfModal.dealId, companyName: pdfModal.companyName, onClose: () => setPdfModal(null) }))] }));
}
