import React, { useState, useMemo } from 'react';
import type { Deal } from '../types';
import { STAGE_LABELS } from '../types';
import {
    Filter,
    Plus,
    MoreVertical,
    Activity,
    History,
    User,
    MessageSquare,
    FileText,
    PlusCircle,
    ChevronLeft,
    ChevronRight,
    MapPin,
    Building2
} from 'lucide-react';

/* ── Types ─────────────────────────────────────────────────── */

interface AdvancedAccountsTableProps {
    deals: Deal[];
    onViewContract: (dealId: string, companyName: string) => void;
}

interface DerivedAccount {
    name: string;
    industry: string;
    totalValue: number;
    dealCount: number;
    contactCount: number;
    deals: Deal[];
    synapsed: boolean;
    topStage: string;
}

/* ── Helpers ───────────────────────────────────────────────── */

function formatCurrency(value: number): string {
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}k`;
    return `$${value.toFixed(0)}`;
}

function getSentiment(account: DerivedAccount): 'ACTIVE' | 'AT RISK' | 'DORMANT' | 'CHURNED' {
    const hasWon = account.deals.some(d => d.stage === 'closed_won' || d.stage === 'implemented');
    const hasLost = account.deals.some(d => d.stage === 'closed_lost');
    const hasRisks = account.deals.some(d => d.risks.length > 0);
    const hasOpen = account.deals.some(d => !['closed_won', 'closed_lost', 'implemented'].includes(d.stage));

    if (hasLost && !hasWon && !hasOpen) return 'CHURNED';
    if (hasRisks || (hasLost && hasOpen)) return 'AT RISK';
    if (hasOpen || hasWon) return 'ACTIVE';
    return 'DORMANT';
}

/* ── Main Component ────────────────────────────────────────── */

export const AdvancedAccountsTable: React.FC<AdvancedAccountsTableProps> = ({ deals, onViewContract }) => {
    const [expandedRow, setExpandedRow] = useState<string | null>(null);
    const [filterIndustry, setFilterIndustry] = useState<string>('');
    const [filterName, setFilterName] = useState<string>('');

    // Derive accounts from live deals
    const accounts = useMemo(() => {
        const map = new Map<string, DerivedAccount>();
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
            const acc = map.get(key)!;
            acc.totalValue += deal.deal_value;
            acc.dealCount += 1;
            acc.contactCount += deal.contacts.length;
            acc.deals.push(deal);
            if (deal.webhook_fired) acc.synapsed = true;
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

    return (
        <div className="flex flex-col flex-1 overflow-hidden bg-background-light dark:bg-background-dark">
            {/* Sub-Header */}
            <div className="bg-white dark:bg-slate-900 px-8 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <h1 className="text-xl font-bold text-slate-900 dark:text-white">Accounts Inventory</h1>
                    <span className="text-sm text-slate-500">{accounts.length} accounts • {deals.length} opportunities</span>
                </div>
                <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-semibold transition-all">
                        <Filter size={18} />
                        <span>Filters</span>
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-primary text-white hover:bg-primary/90 rounded-lg text-sm font-semibold shadow-lg shadow-primary/20 transition-all">
                        <Plus size={18} />
                        <span>New Account</span>
                    </button>
                </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar Filters */}
                <aside className="w-72 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 p-6 flex flex-col gap-8 overflow-y-auto hidden md:flex">
                    <div className="space-y-4">
                        <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Search Filters</h3>
                        <div className="space-y-5">
                            <label className="block">
                                <span className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block">Account Name</span>
                                <input
                                    className="w-full rounded-lg border border-slate-200 dark:border-slate-700 dark:bg-slate-800 text-sm focus:border-primary focus:ring-primary py-2 px-3"
                                    placeholder="e.g. Acme Corp"
                                    type="text"
                                    value={filterName}
                                    onChange={(e) => setFilterName(e.target.value)}
                                />
                            </label>
                            <label className="block">
                                <span className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block">Industry</span>
                                <select
                                    className="w-full rounded-lg border border-slate-200 dark:border-slate-700 dark:bg-slate-800 text-sm focus:border-primary focus:ring-primary py-2 px-3 appearance-none"
                                    value={filterIndustry}
                                    onChange={(e) => setFilterIndustry(e.target.value)}
                                >
                                    <option value="">All Industries</option>
                                    {industries.map(ind => (
                                        <option key={ind} value={ind}>{ind}</option>
                                    ))}
                                </select>
                            </label>
                        </div>
                    </div>
                    <div className="mt-auto pt-6 border-t border-slate-200 dark:border-slate-800">
                        <button
                            className="w-full py-2.5 text-sm font-semibold text-primary hover:bg-primary/5 rounded-lg transition-colors"
                            onClick={() => { setFilterName(''); setFilterIndustry(''); }}
                        >
                            Clear All Filters
                        </button>
                    </div>
                </aside>

                {/* Table Content */}
                <main className="flex-1 p-6 overflow-y-auto">
                    <div className="bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl rounded-xl shadow-xl overflow-hidden border border-slate-200 dark:border-slate-800">
                        <table className="w-full text-left border-collapse min-w-[900px]">
                            <thead>
                                <tr className="bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Account Name</th>
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Industry</th>
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center">Opps</th>
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Pipeline</th>
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center">Contacts</th>
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center">Sentiment</th>
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-center">Synapse</th>
                                    <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                                {accounts.map((account) => {
                                    const sentiment = getSentiment(account);
                                    return (
                                        <React.Fragment key={account.name}>
                                            <tr
                                                className={`hover:bg-primary/[0.02] transition-colors cursor-pointer group ${expandedRow === account.name ? 'bg-primary/[0.04]' : ''}`}
                                                onClick={() => setExpandedRow(expandedRow === account.name ? null : account.name)}
                                            >
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center gap-3">
                                                        <div className="size-10 rounded bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm text-primary">
                                                            <Building2 size={20} />
                                                        </div>
                                                        <div>
                                                            <p className="text-sm font-bold text-slate-900 dark:text-white">{account.name}</p>
                                                            <p className="text-[10px] text-slate-500 flex items-center gap-1"><MapPin size={8} /> {account.industry}</p>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{account.industry}</td>
                                                <td className="px-6 py-4 text-sm text-center font-bold text-slate-900 dark:text-white">{account.dealCount}</td>
                                                <td className="px-6 py-4 text-sm font-bold text-right text-primary">{formatCurrency(account.totalValue)}</td>
                                                <td className="px-6 py-4 text-sm text-center text-slate-700 dark:text-slate-300">{account.contactCount}</td>
                                                <td className="px-6 py-4 text-center">
                                                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold ${sentiment === 'ACTIVE' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
                                                            sentiment === 'AT RISK' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' :
                                                                sentiment === 'CHURNED' ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400' :
                                                                    'bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-400'
                                                        }`}>
                                                        <span className={`size-1.5 rounded-full mr-1.5 ${sentiment === 'ACTIVE' ? 'bg-emerald-500' :
                                                                sentiment === 'AT RISK' ? 'bg-amber-500' :
                                                                    sentiment === 'CHURNED' ? 'bg-rose-500' : 'bg-slate-400'
                                                            }`}></span>
                                                        {sentiment}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-center">
                                                    {account.synapsed
                                                        ? <span className="text-emerald-500 text-xs font-bold">✅ Connected</span>
                                                        : <span className="text-slate-400 text-xs">—</span>
                                                    }
                                                </td>
                                                <td className="px-6 py-4 relative">
                                                    <div className="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <button className="p-1.5 hover:bg-white dark:hover:bg-slate-700 text-slate-500 rounded-lg shadow-sm border border-transparent hover:border-slate-200 dark:hover:border-slate-600">
                                                            <MoreVertical size={16} />
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                            {expandedRow === account.name && (
                                                <tr className="bg-slate-50/50 dark:bg-slate-800/30 border-l-2 border-primary">
                                                    <td className="px-8 py-6" colSpan={8}>
                                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                                                            {/* Opportunities */}
                                                            <div className="space-y-4">
                                                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                                                    <Activity size={14} /> Opportunities ({account.dealCount})
                                                                </h4>
                                                                <div className="space-y-2">
                                                                    {account.deals.map(deal => (
                                                                        <div key={deal.deal_id} className="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                                                                            <div>
                                                                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${deal.stage === 'closed_won' || deal.stage === 'implemented' ? 'bg-emerald-100 text-emerald-700' :
                                                                                        deal.stage === 'closed_lost' ? 'bg-rose-100 text-rose-700' :
                                                                                            'bg-blue-100 text-blue-700'
                                                                                    }`}>{STAGE_LABELS[deal.stage]}</span>
                                                                                <p className="text-xs text-slate-500 mt-1 font-mono">{deal.deal_id.slice(0, 12)}...</p>
                                                                            </div>
                                                                            <span className="text-sm font-bold text-primary">{formatCurrency(deal.deal_value)}</span>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                            {/* Recent Activity */}
                                                            <div className="space-y-4">
                                                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                                                    <History size={14} /> Deal Products
                                                                </h4>
                                                                <ul className="text-xs space-y-3">
                                                                    {account.deals.flatMap(d => d.products).slice(0, 5).map((p, i) => (
                                                                        <li key={i} className="flex gap-2">
                                                                            <span className="text-primary font-bold">•</span> {p.name}
                                                                            {p.annual_value && <span className="text-slate-400 ml-auto">{formatCurrency(p.annual_value)}/yr</span>}
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                            {/* Quick Actions */}
                                                            <div className="space-y-4">
                                                                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                                                    <User size={14} /> Quick Actions
                                                                </h4>
                                                                <div className="flex flex-wrap gap-2">
                                                                    <button
                                                                        className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white text-[10px] font-bold rounded-lg hover:bg-primary/90 shadow-md shadow-primary/20"
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            const firstDeal = account.deals[0];
                                                                            if (firstDeal) onViewContract(firstDeal.deal_id, account.name);
                                                                        }}
                                                                    >
                                                                        <FileText size={12} /> View Contract
                                                                    </button>
                                                                    <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-bold rounded-lg shadow-sm border border-slate-200 dark:border-slate-600">
                                                                        <MessageSquare size={12} /> Chat with AE
                                                                    </button>
                                                                    <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-bold rounded-lg shadow-sm border border-slate-200 dark:border-slate-600">
                                                                        <PlusCircle size={12} /> Add Opp
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                </tr>
                                            )}
                                        </React.Fragment>
                                    );
                                })}
                                {accounts.length === 0 && (
                                    <tr>
                                        <td colSpan={8} className="px-6 py-12 text-center text-slate-400 text-sm">
                                            No accounts found matching your filters.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                    {/* Pagination */}
                    <div className="mt-6 flex items-center justify-between">
                        <p className="text-sm text-slate-500">Showing <span className="font-bold text-slate-900 dark:text-slate-200">{accounts.length}</span> accounts</p>
                        <div className="flex items-center gap-1">
                            <button className="p-2 border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-50" disabled>
                                <ChevronLeft size={16} />
                            </button>
                            <button className="px-4 py-2 bg-primary text-white font-bold rounded-lg text-sm transition-all focus:ring-2 focus:ring-primary/50">1</button>
                            <button className="p-2 border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800" disabled>
                                <ChevronRight size={16} />
                            </button>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};
