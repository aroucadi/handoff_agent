import React, { useMemo } from 'react';
import type { Deal, DealStage } from '../types';
import { STAGE_LABELS } from '../types';
import {
    TrendingUp,
    TrendingDown,
    Filter,
    History,
    Mail,
    CheckCircle,
    Phone,
    Sparkles,
    Clock,
    RefreshCw,
    Rocket,
    ChevronRight
} from 'lucide-react';

/* ── Types ─────────────────────────────────────────────────── */

interface PremiumDashboardProps {
    deals: Deal[];
}

interface KPICardProps {
    label: string;
    value: string;
    change: string;
    isPositive: boolean;
    colorClass: string;
    sparkline: string;
}

/* ── Sub-Components ────────────────────────────────────────── */

const KPICard: React.FC<KPICardProps> = ({ label, value, change, isPositive, colorClass, sparkline }) => (
    <div className="relative overflow-hidden bg-white dark:bg-slate-800/40 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg animate-[fadeIn_0.5s_ease-out]">
        <div className="flex justify-between items-start mb-4">
            <p className="text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">{label}</p>
            <span className={`flex items-center text-xs font-bold px-2 py-1 rounded-full ${isPositive ? 'text-emerald-500 bg-emerald-500/10' : 'text-rose-500 bg-rose-500/10'}`}>
                {isPositive ? <TrendingUp size={12} className="mr-1" /> : <TrendingDown size={12} className="mr-1" />}
                {change}
            </span>
        </div>
        <p className="text-3xl font-bold text-slate-900 dark:text-white">{value}</p>
        <div className="mt-4 h-12 w-full opacity-30">
            <div
                className={`w-full h-full bg-gradient-to-r ${colorClass} rounded-lg`}
                style={{ clipPath: `polygon(${sparkline})` }}
            />
        </div>
    </div>
);

const EinsteinInsight: React.FC<{
    title: string;
    description: string;
    icon: React.ReactNode;
    buttonText: string;
    variant?: 'primary' | 'secondary'
}> = ({ title, description, icon, buttonText, variant = 'primary' }) => (
    <div className="p-4 bg-white/5 dark:bg-slate-900/40 backdrop-blur-sm rounded-lg border border-primary/20 group cursor-pointer hover:border-primary transition-colors">
        <div className="flex items-start gap-3">
            <div className={`p-2 rounded-md ${variant === 'primary' ? 'bg-primary/20 text-primary' : 'bg-emerald-500/20 text-emerald-500'}`}>
                {icon}
            </div>
            <div className="flex-1">
                <h4 className="text-sm font-bold group-hover:text-primary transition-colors">{title}</h4>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">{description}</p>
            </div>
        </div>
        <button className={`mt-4 w-full py-2 text-xs font-bold rounded-lg shadow-lg transition-all ${variant === 'primary'
            ? 'bg-primary text-white shadow-primary/20 hover:bg-primary/90'
            : 'bg-slate-800 dark:bg-slate-700 text-white hover:bg-slate-700'
            }`}>
            {buttonText}
        </button>
    </div>
);

/* ── Helpers ───────────────────────────────────────────────── */

function formatCurrency(value: number): string {
    if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}k`;
    return `$${value.toFixed(0)}`;
}

/* ── Main Component ────────────────────────────────────────── */

export const PremiumDashboard: React.FC<PremiumDashboardProps> = ({ deals }) => {
    const metrics = useMemo(() => {
        const totalValue = deals.reduce((sum, d) => sum + d.deal_value, 0);
        const openDeals = deals.filter(d => !['closed_lost', 'implemented'].includes(d.stage));
        const wonDeals = deals.filter(d => d.stage === 'closed_won' || d.stage === 'implemented');
        const lostDeals = deals.filter(d => d.stage === 'closed_lost');
        const winRate = wonDeals.length + lostDeals.length > 0
            ? Math.round((wonDeals.length / (wonDeals.length + lostDeals.length)) * 100)
            : 0;

        // Stage funnel data
        const funnelStages: DealStage[] = ['prospecting', 'qualification', 'negotiation', 'closed_won'];
        const funnelData = funnelStages.map(stage => {
            const stageDeals = deals.filter(d => d.stage === stage);
            const stageValue = stageDeals.reduce((s, d) => s + d.deal_value, 0);
            return { stage, label: STAGE_LABELS[stage], value: stageValue, count: stageDeals.length };
        });
        const maxFunnelValue = Math.max(...funnelData.map(f => f.value), 1);

        // Recent activity (webhook-fired deals)
        const recentActivity = deals
            .filter(d => d.webhook_fired)
            .slice(0, 3)
            .map(d => ({
                user: d.company_name,
                action: d.stage === 'closed_won' ? 'Deal Closed' : `moved to ${STAGE_LABELS[d.stage]}`,
                target: formatCurrency(d.deal_value),
                time: d.close_date || 'Recently',
                meta: d.products.map(p => p.name).join(', ') || d.industry,
            }));

        return { totalValue, openDeals, wonDeals, lostDeals, winRate, funnelData, maxFunnelValue, recentActivity };
    }, [deals]);

    const activityIcons = [
        { icon: <CheckCircle size={16} />, iconColor: 'text-emerald-500 bg-emerald-500/10' },
        { icon: <Mail size={16} />, iconColor: 'text-blue-500 bg-blue-500/10' },
        { icon: <Phone size={16} />, iconColor: 'text-amber-500 bg-amber-500/10' },
    ];

    // Einstein insights based on actual data
    const atRiskDeals = deals.filter(d => d.risks.length > 0 && !['closed_lost', 'closed_won', 'implemented'].includes(d.stage));
    const topRiskDeal = atRiskDeals[0];
    const prospectingDeals = deals.filter(d => d.stage === 'prospecting');
    const negotiationDeals = deals.filter(d => d.stage === 'negotiation');

    return (
        <div className="p-8 max-w-[1600px] mx-auto w-full space-y-8">
            {/* KPI Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KPICard
                    label="Total Pipeline"
                    value={formatCurrency(metrics.totalValue)}
                    change={`${deals.length} deals`}
                    isPositive={true}
                    colorClass="from-primary/5 via-primary/40 to-primary/10"
                    sparkline="0% 80%, 10% 60%, 20% 70%, 30% 40%, 40% 55%, 50% 30%, 60% 45%, 70% 20%, 80% 35%, 90% 10%, 100% 25%, 100% 100%, 0% 100%"
                />
                <KPICard
                    label="Open Deals"
                    value={String(metrics.openDeals.length)}
                    change={formatCurrency(metrics.openDeals.reduce((s, d) => s + d.deal_value, 0))}
                    isPositive={metrics.openDeals.length > 0}
                    colorClass="from-rose-500/5 via-rose-500/40 to-rose-500/10"
                    sparkline="0% 20%, 20% 40%, 40% 30%, 60% 70%, 80% 60%, 100% 90%, 100% 100%, 0% 100%"
                />
                <KPICard
                    label="Win Rate"
                    value={`${metrics.winRate}%`}
                    change={`${metrics.wonDeals.length}W / ${metrics.lostDeals.length}L`}
                    isPositive={metrics.winRate >= 50}
                    colorClass="from-success/5 via-success/40 to-success/10"
                    sparkline="0% 70%, 15% 65%, 30% 80%, 45% 40%, 60% 50%, 75% 20%, 90% 30%, 100% 10%, 100% 100%, 0% 100%"
                />
                <KPICard
                    label="Closed Won"
                    value={formatCurrency(metrics.wonDeals.reduce((s, d) => s + d.deal_value, 0))}
                    change={`${metrics.wonDeals.length} deals`}
                    isPositive={true}
                    colorClass="from-primary/5 via-primary/40 to-primary/10"
                    sparkline="0% 90%, 25% 85%, 50% 80%, 75% 75%, 100% 70%, 100% 100%, 0% 100%"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Section */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Sales Funnel */}
                    <div className="bg-white dark:bg-slate-800/40 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
                        <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                            <Filter className="text-primary" size={20} /> Sales Stage Funnel
                        </h3>
                        <div className="flex flex-col gap-3">
                            {metrics.funnelData.map((item, idx) => {
                                const widthPct = metrics.maxFunnelValue > 0
                                    ? Math.max(5, (item.value / metrics.maxFunnelValue) * 100)
                                    : 5;
                                return (
                                    <div key={idx} className="group relative flex items-center h-14 bg-primary/5 rounded-lg px-6 overflow-hidden transition-all hover:bg-primary/10 border border-transparent hover:border-primary/20">
                                        <div className="absolute inset-0 bg-primary opacity-5" style={{ width: `${widthPct}%` }}></div>
                                        <span className="relative z-10 text-sm font-bold w-32">{item.label}</span>
                                        <div className="relative z-10 flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden ml-4">
                                            <div className="h-full bg-primary transition-all duration-1000" style={{ width: `${widthPct}%` }}></div>
                                        </div>
                                        <span className="relative z-10 text-sm font-bold ml-6">{formatCurrency(item.value)}</span>
                                        <span className="relative z-10 text-xs text-slate-400 ml-2">({item.count})</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Activity Feed */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <History className="text-primary" size={20} /> Recent Activity
                        </h3>
                        <div className="space-y-3">
                            {metrics.recentActivity.length > 0 ? metrics.recentActivity.map((activity, idx) => {
                                const iconSet = activityIcons[idx % activityIcons.length];
                                return (
                                    <div key={idx} className="flex items-center p-4 bg-white/50 dark:bg-slate-800/20 backdrop-blur-md rounded-xl border border-white/20 dark:border-slate-700 shadow-sm group hover:border-primary/50 transition-all">
                                        <div className={`size-10 rounded-full flex items-center justify-center mr-4 ${iconSet.iconColor}`}>
                                            {iconSet.icon}
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium"><span className="text-primary font-bold">{activity.user}</span> {activity.action}</p>
                                            <p className="text-xs text-slate-500 mt-0.5">{activity.time} • {activity.target} • {activity.meta}</p>
                                        </div>
                                        <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-slate-400 hover:text-primary">
                                            <ChevronRight size={18} />
                                        </button>
                                    </div>
                                );
                            }) : (
                                <div className="p-6 text-center text-slate-400 text-sm bg-white/50 dark:bg-slate-800/20 rounded-xl border border-slate-200 dark:border-slate-700">
                                    No recent webhook activity. Move a deal through the pipeline to see updates here.
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Sidebar — Einstein AI Insights */}
                <div className="space-y-6">
                    <div className="relative p-6 rounded-xl border border-primary/30 bg-primary/5 overflow-hidden shadow-inner">
                        <div className="absolute -top-12 -right-12 size-40 bg-primary/20 blur-[60px]"></div>
                        <div className="absolute -bottom-12 -left-12 size-40 bg-primary/10 blur-[60px]"></div>
                        <div className="relative z-10">
                            <h3 className="text-lg font-bold mb-6 flex items-center gap-2 text-slate-900 dark:text-white">
                                <Sparkles className="text-primary fill-primary/20" size={20} /> Einstein AI Insights
                            </h3>
                            <p className="text-xs font-bold text-primary uppercase tracking-widest mb-4">Next Best Actions</p>
                            <div className="space-y-4">
                                {topRiskDeal && (
                                    <EinsteinInsight
                                        title={`Risk Alert: ${topRiskDeal.company_name}`}
                                        description={topRiskDeal.risks[0]?.description || 'Flagged risks detected on this opportunity. Review recommended.'}
                                        icon={<Clock size={16} />}
                                        buttonText="Review Risks"
                                    />
                                )}
                                {negotiationDeals.length > 0 && (
                                    <EinsteinInsight
                                        title={`${negotiationDeals.length} Deals in Negotiation`}
                                        description={`Total value: ${formatCurrency(negotiationDeals.reduce((s, d) => s + d.deal_value, 0))}. Push for close this quarter.`}
                                        icon={<RefreshCw size={16} />}
                                        buttonText="View Negotiations"
                                        variant="secondary"
                                    />
                                )}
                                {prospectingDeals.length > 0 && (
                                    <EinsteinInsight
                                        title={`${prospectingDeals.length} New Prospects`}
                                        description={`${prospectingDeals.map(d => d.company_name).slice(0, 2).join(', ')} and more are in early pipeline.`}
                                        icon={<Rocket size={16} />}
                                        buttonText="Qualify Leads"
                                        variant="secondary"
                                    />
                                )}
                                {!topRiskDeal && negotiationDeals.length === 0 && prospectingDeals.length === 0 && (
                                    <EinsteinInsight
                                        title="Pipeline is Clean"
                                        description="No immediate actions needed. All deals are on track."
                                        icon={<CheckCircle size={16} />}
                                        buttonText="View Pipeline"
                                    />
                                )}
                            </div>

                            <div className="mt-8 p-4 bg-slate-900 rounded-lg text-center shadow-2xl ring-1 ring-white/10">
                                <p className="text-[10px] text-slate-400 uppercase font-bold tracking-tighter">AI Accuracy Score</p>
                                <div className="mt-2 flex items-center justify-center gap-1">
                                    <span className="text-2xl font-black text-white">{metrics.winRate > 0 ? Math.min(98, metrics.winRate + 30) : 94}</span>
                                    <span className="text-primary text-lg font-bold">%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
