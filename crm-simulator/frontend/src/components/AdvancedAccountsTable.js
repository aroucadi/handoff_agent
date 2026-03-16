import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState, useMemo } from 'react';
import { STAGE_LABELS } from '../types';
import { Filter, Plus, MoreVertical, Activity, History, User, MessageSquare, FileText, PlusCircle, ChevronLeft, ChevronRight, MapPin, Building2 } from 'lucide-react';
/* ── Helpers ───────────────────────────────────────────────── */
function formatCurrency(value) {
    if (value >= 1_000_000)
        return `$${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000)
        return `$${(value / 1_000).toFixed(0)}k`;
    return `$${value.toFixed(0)}`;
}
function getSentiment(account) {
    const hasWon = account.deals.some(d => d.stage === 'closed_won' || d.stage === 'implemented');
    const hasLost = account.deals.some(d => d.stage === 'closed_lost');
    const hasRisks = account.deals.some(d => d.risks.length > 0);
    const hasOpen = account.deals.some(d => !['closed_won', 'closed_lost', 'implemented'].includes(d.stage));
    if (hasLost && !hasWon && !hasOpen)
        return 'CHURNED';
    if (hasRisks || (hasLost && hasOpen))
        return 'AT RISK';
    if (hasOpen || hasWon)
        return 'ACTIVE';
    return 'DORMANT';
}
/* ── Main Component ────────────────────────────────────────── */
export const AdvancedAccountsTable = ({ deals, onViewContract }) => {
    const [expandedRow, setExpandedRow] = useState(null);
    const [filterIndustry, setFilterIndustry] = useState('');
    const [filterName, setFilterName] = useState('');
    // Derive accounts from live deals
    const accounts = useMemo(() => {
        const map = new Map();
        for (const deal of deals) {
            const key = deal.company_name;
            if (!map.has(key)) {
                map.set(key, {
                    name: key,
                    industry: deal.industry,
                    totalValue: 0,
                    dealCount: 0,
                    contactCount: 0,
                    deals: [],
                    synapsed: false,
                    topStage: deal.stage,
                });
            }
            const acc = map.get(key);
            acc.totalValue += deal.deal_value;
            acc.dealCount += 1;
            acc.contactCount += deal.contacts.length;
            acc.deals.push(deal);
            if (deal.webhook_fired)
                acc.synapsed = true;
        }
        let list = Array.from(map.values());
        // Apply filters
        if (filterName) {
            list = list.filter(a => a.name.toLowerCase().includes(filterName.toLowerCase()));
        }
        if (filterIndustry) {
            list = list.filter(a => a.industry === filterIndustry);
        }
        list.sort((a, b) => b.totalValue - a.totalValue);
        return list;
    }, [deals, filterName, filterIndustry]);
    const industries = useMemo(() => {
        return [...new Set(deals.map(d => d.industry))].sort();
    }, [deals]);
    return (_jsxs("div", { className: "flex flex-col flex-1 overflow-hidden bg-background-light dark:bg-background-dark", children: [_jsxs("div", { className: "bg-white dark:bg-slate-900 px-8 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-4", children: [_jsx("h1", { className: "text-xl font-bold text-slate-900 dark:text-white", children: "Accounts Inventory" }), _jsxs("span", { className: "text-sm text-slate-500", children: [accounts.length, " accounts \u2022 ", deals.length, " opportunities"] })] }), _jsxs("div", { className: "flex items-center gap-3", children: [_jsxs("button", { className: "flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-semibold transition-all", children: [_jsx(Filter, { size: 18 }), _jsx("span", { children: "Filters" })] }), _jsxs("button", { className: "flex items-center gap-2 px-4 py-2 bg-primary text-white hover:bg-primary/90 rounded-lg text-sm font-semibold shadow-lg shadow-primary/20 transition-all", children: [_jsx(Plus, { size: 18 }), _jsx("span", { children: "New Account" })] })] })] }), _jsxs("div", { className: "flex flex-1 overflow-hidden", children: [_jsxs("aside", { className: "w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 p-6 flex flex-col gap-8 overflow-y-auto hidden md:flex", children: [_jsxs("div", { className: "space-y-4", children: [_jsx("h3", { className: "text-xs font-bold uppercase tracking-widest text-slate-400", children: "Search Filters" }), _jsxs("div", { className: "space-y-5", children: [_jsxs("label", { className: "block", children: [_jsx("span", { className: "text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block", children: "Account Name" }), _jsx("input", { className: "w-full rounded-lg border border-slate-200 dark:border-slate-700 dark:bg-slate-800 text-sm focus:border-primary focus:ring-primary py-2 px-3", placeholder: "e.g. Acme Corp", type: "text", value: filterName, onChange: (e) => setFilterName(e.target.value) })] }), _jsxs("label", { className: "block", children: [_jsx("span", { className: "text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block", children: "Industry" }), _jsxs("select", { className: "w-full rounded-lg border border-slate-200 dark:border-slate-700 dark:bg-slate-800 text-sm focus:border-primary focus:ring-primary py-2 px-3 appearance-none", value: filterIndustry, onChange: (e) => setFilterIndustry(e.target.value), children: [_jsx("option", { value: "", children: "All Industries" }), industries.map(ind => (_jsx("option", { value: ind, children: ind }, ind)))] })] })] })] }), _jsx("div", { className: "mt-auto pt-6 border-t border-slate-200 dark:border-slate-800", children: _jsx("button", { className: "w-full py-2.5 text-sm font-semibold text-primary hover:bg-primary/5 rounded-lg transition-colors", onClick: () => { setFilterName(''); setFilterIndustry(''); }, children: "Clear All Filters" }) })] }), _jsxs("main", { className: "flex-1 p-6 overflow-y-auto", children: [_jsx("div", { className: "bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl rounded-xl shadow-xl overflow-hidden border border-slate-200 dark:border-slate-800", children: _jsxs("table", { className: "w-full text-left border-collapse min-w-[900px]", children: [_jsx("thead", { children: _jsxs("tr", { className: "bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700", children: [_jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider", children: "Account Name" }), _jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider", children: "Industry" }), _jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center", children: "Opps" }), _jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right", children: "Pipeline" }), _jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center", children: "Contacts" }), _jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center", children: "Sentiment" }), _jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center", children: "Synapse" }), _jsx("th", { className: "px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider" })] }) }), _jsxs("tbody", { className: "divide-y divide-slate-200 dark:divide-slate-700", children: [accounts.map((account) => {
                                                    const sentiment = getSentiment(account);
                                                    return (_jsxs(React.Fragment, { children: [_jsxs("tr", { className: `hover:bg-primary/[0.02] transition-colors cursor-pointer group ${expandedRow === account.name ? 'bg-primary/[0.04]' : ''}`, onClick: () => setExpandedRow(expandedRow === account.name ? null : account.name), children: [_jsx("td", { className: "px-6 py-4", children: _jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "size-10 rounded bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm text-primary", children: _jsx(Building2, { size: 20 }) }), _jsxs("div", { children: [_jsx("p", { className: "text-sm font-bold text-slate-900 dark:text-white", children: account.name }), _jsxs("p", { className: "text-[10px] text-slate-500 flex items-center gap-1", children: [_jsx(MapPin, { size: 8 }), " ", account.industry] })] })] }) }), _jsx("td", { className: "px-6 py-4 text-sm text-slate-600 dark:text-slate-400", children: account.industry }), _jsx("td", { className: "px-6 py-4 text-sm text-center font-bold text-slate-900 dark:text-white", children: account.dealCount }), _jsx("td", { className: "px-6 py-4 text-sm font-bold text-right text-primary", children: formatCurrency(account.totalValue) }), _jsx("td", { className: "px-6 py-4 text-sm text-center text-slate-700 dark:text-slate-300", children: account.contactCount }), _jsx("td", { className: "px-6 py-4 text-center", children: _jsxs("span", { className: `inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold ${sentiment === 'ACTIVE' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
                                                                                sentiment === 'AT RISK' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' :
                                                                                    sentiment === 'CHURNED' ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400' :
                                                                                        'bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-400'}`, children: [_jsx("span", { className: `size-1.5 rounded-full mr-1.5 ${sentiment === 'ACTIVE' ? 'bg-emerald-500' :
                                                                                        sentiment === 'AT RISK' ? 'bg-amber-500' :
                                                                                            sentiment === 'CHURNED' ? 'bg-rose-500' : 'bg-slate-400'}` }), sentiment] }) }), _jsx("td", { className: "px-6 py-4 text-center", children: account.synapsed
                                                                            ? _jsx("span", { className: "text-emerald-500 text-xs font-bold", children: "\u2705 Connected" })
                                                                            : _jsx("span", { className: "text-slate-400 text-xs", children: "\u2014" }) }), _jsx("td", { className: "px-6 py-4 relative", children: _jsx("div", { className: "flex justify-end opacity-0 group-hover:opacity-100 transition-opacity", children: _jsx("button", { className: "p-1.5 hover:bg-white dark:hover:bg-slate-700 text-slate-500 rounded-lg shadow-sm border border-transparent hover:border-slate-200 dark:hover:border-slate-600", children: _jsx(MoreVertical, { size: 16 }) }) }) })] }), expandedRow === account.name && (_jsx("tr", { className: "bg-slate-50/50 dark:bg-slate-800/30 border-l-2 border-primary", children: _jsx("td", { className: "px-8 py-6", colSpan: 8, children: _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-8", children: [_jsxs("div", { className: "space-y-4", children: [_jsxs("h4", { className: "text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2", children: [_jsx(Activity, { size: 14 }), " Opportunities (", account.dealCount, ")"] }), _jsx("div", { className: "space-y-2", children: account.deals.map(deal => (_jsxs("div", { className: "flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700", children: [_jsxs("div", { children: [_jsx("span", { className: `text-[10px] font-bold px-2 py-0.5 rounded-full ${deal.stage === 'closed_won' || deal.stage === 'implemented' ? 'bg-emerald-100 text-emerald-700' :
                                                                                                                deal.stage === 'closed_lost' ? 'bg-rose-100 text-rose-700' :
                                                                                                                    'bg-blue-100 text-blue-700'}`, children: STAGE_LABELS[deal.stage] }), _jsxs("p", { className: "text-xs text-slate-500 mt-1 font-mono", children: [deal.deal_id.slice(0, 12), "..."] })] }), _jsx("span", { className: "text-sm font-bold text-primary", children: formatCurrency(deal.deal_value) })] }, deal.deal_id))) })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("h4", { className: "text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2", children: [_jsx(History, { size: 14 }), " Deal Products"] }), _jsx("ul", { className: "text-xs space-y-3", children: account.deals.flatMap(d => d.products).slice(0, 5).map((p, i) => (_jsxs("li", { className: "flex gap-2", children: [_jsx("span", { className: "text-primary font-bold", children: "\u2022" }), " ", p.name, p.annual_value && _jsxs("span", { className: "text-slate-400 ml-auto", children: [formatCurrency(p.annual_value), "/yr"] })] }, i))) })] }), _jsxs("div", { className: "space-y-4", children: [_jsxs("h4", { className: "text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2", children: [_jsx(User, { size: 14 }), " Quick Actions"] }), _jsxs("div", { className: "flex flex-wrap gap-2", children: [_jsxs("button", { className: "flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white text-[10px] font-bold rounded-lg hover:bg-primary/90 shadow-md shadow-primary/20", onClick: (e) => {
                                                                                                    e.stopPropagation();
                                                                                                    const firstDeal = account.deals[0];
                                                                                                    if (firstDeal)
                                                                                                        onViewContract(firstDeal.deal_id, account.name);
                                                                                                }, children: [_jsx(FileText, { size: 12 }), " View Contract"] }), _jsxs("button", { className: "flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-bold rounded-lg shadow-sm border border-slate-200 dark:border-slate-600", children: [_jsx(MessageSquare, { size: 12 }), " Chat with AE"] }), _jsxs("button", { className: "flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-bold rounded-lg shadow-sm border border-slate-200 dark:border-slate-600", children: [_jsx(PlusCircle, { size: 12 }), " Add Opp"] })] })] })] }) }) }))] }, account.name));
                                                }), accounts.length === 0 && (_jsx("tr", { children: _jsx("td", { colSpan: 8, className: "px-6 py-12 text-center text-slate-400 text-sm", children: "No accounts found matching your filters." }) }))] })] }) }), _jsxs("div", { className: "mt-6 flex items-center justify-between", children: [_jsxs("p", { className: "text-sm text-slate-500", children: ["Showing ", _jsx("span", { className: "font-bold text-slate-900 dark:text-slate-200", children: accounts.length }), " accounts"] }), _jsxs("div", { className: "flex items-center gap-1", children: [_jsx("button", { className: "p-2 border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50", disabled: true, children: _jsx(ChevronLeft, { size: 16 }) }), _jsx("button", { className: "px-4 py-2 bg-primary text-white font-bold rounded-lg text-sm transition-all focus:ring-2 focus:ring-primary/50", children: "1" }), _jsx("button", { className: "p-2 border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800", disabled: true, children: _jsx(ChevronRight, { size: 16 }) })] })] })] })] })] }));
};
