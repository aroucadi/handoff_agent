import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Database, Zap, BookOpen, Globe } from 'lucide-react';

const TenantHub: React.FC = () => {
    const { slug } = useParams<{ slug: string }>();
    const [tenantName, setTenantName] = useState<string>('');

    useEffect(() => {
        // We assume the context was set by TenantLayout.tsx
        const name = localStorage.getItem('tenant_name') || 'Your Workspace';
        setTenantName(name);
    }, [slug]);

    const cards = [
        { title: 'CRM Connectivity', icon: Globe, desc: 'Sync your deals & accounts', path: `/t/${slug}/hub/crm`, color: 'text-blue-400' },
        { title: 'Product Catalog', icon: Database, desc: 'Manage product knowledge', path: `/t/${slug}/hub/products`, color: 'text-emerald-400' },
        { title: 'Agent Persona', icon: Zap, desc: 'Refine response style', path: `/t/${slug}/hub/agent`, color: 'text-purple-400' },
        { title: 'Knowledge Sources', icon: BookOpen, desc: 'Ground with docs & URLs', path: `/t/${slug}/hub/knowledge`, color: 'text-amber-400' },
    ];

    return (
        <div className="tenant-hub animate-fade-in">
            <header className="mb-12">
                <div className="flex items-center gap-4 mb-2">
                    <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-black tracking-widest uppercase text-white/40">Tenant Hub</span>
                </div>
                <h1 className="text-5xl font-black text-white leading-tight">
                    Welcome to <span className="text-secondary-cyan italic">{tenantName}</span>
                </h1>
                <p className="text-white/50 text-xl font-medium mt-4 max-w-2xl">
                    Configure your cognitive layer, unify your CRM workflows, and empower your teams with grounded AI.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {cards.map((card, i) => (
                    <Link to={card.path} key={i} className="group glass-card p-8 hover:border-white/20 transition-all hover:-translate-y-2">
                        <card.icon className={`${card.color} mb-6 pointer-events-none group-hover:scale-110 transition-transform`} size={32} />
                        <h3 className="text-xl font-bold mb-2">{card.title}</h3>
                        <p className="text-white/40 text-sm leading-relaxed">{card.desc}</p>
                    </Link>
                ))}
            </div>

            <div className="mt-12 p-8 glass-card border-emerald-500/20 bg-emerald-500/5">
                <div className="flex items-center justify-between">
                    <div>
                        <h4 className="text-xl font-bold text-emerald-400 mb-2 whitespace-nowrap">Live Agent Preview</h4>
                        <p className="text-white/50 text-sm max-w-xl">Test your current configuration against the Gemini Live engine. Verification ensures grounding is accurate across all entity types.</p>
                    </div>
                    <div className="flex gap-4">
                        <Link to={`/t/${slug}/hub/test`} className="px-8 py-4 bg-white/5 border border-white/10 text-white font-bold rounded-2xl hover:bg-white/10 transition-all">Internal Test</Link>
                        <button
                            onClick={() => window.open(`${import.meta.env.VITE_VOICE_UI_URL || ''}/t/${slug}/voice`, '_blank')}
                            className="px-8 py-4 bg-emerald-500 text-black font-black rounded-2xl hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/10"
                        >
                            Launch Live Agent
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TenantHub;
