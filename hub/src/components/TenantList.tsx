import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface Tenant {
    tenant_id: string;
    name: string;
    brand_name: string;
    status: 'configuring' | 'ready' | 'active';
    products: any[];
    agent: { roles: string[] };
    updated_at: string;
}

const TenantList: React.FC = () => {
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/tenants')
            .then(res => res.json())
            .then(data => {
                setTenants(data.tenants);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch tenants", err);
                setLoading(false);
            });
    }, []);

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[400px]">
            <div className="w-12 h-12 rounded-full border-2 border-primary-purple border-t-transparent animate-spin mb-4" />
            <div className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">Synchronizing Neural Instances...</div>
        </div>
    );

    return (
        <section className="tenant-dashboard">
            <div className="flex justify-between items-end mb-12 gap-8">
                <div className="flex-1">
                    <h1 className="text-4xl font-black mb-2 text-gradient">Nexus Dashboard</h1>
                    <p className="text-slate-400 max-w-md">Manage neural tenant instances and agent grounding configurations.</p>
                </div>
                <div className="flex gap-6">
                    <div className="glass-card p-6 px-10 text-center min-w-[180px] stagger-1 relative overflow-hidden group">
                        <div className="absolute top-0 left-0 w-full h-1 bg-primary-purple opacity-30" />
                        <span className="label block text-[10px] mb-2 opacity-50">Total Nodes</span>
                        <div className="text-4xl font-black italic tracking-tighter">{tenants.length}</div>
                    </div>
                    <div className="glass-card p-6 px-10 text-center min-w-[180px] stagger-2 relative overflow-hidden group">
                        <div className="absolute top-0 left-0 w-full h-1 bg-emerald-400 opacity-30" />
                        <span className="label block text-[10px] mb-2 text-emerald-400/70">Live Agents</span>
                        <div className="text-4xl font-black text-emerald-400 italic tracking-tighter">
                            {tenants.filter(t => t.status === 'active' || t.status === 'ready').length}
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {tenants.map((tenant, idx) => (
                    <Link key={tenant.tenant_id} to={`/tenants/${tenant.tenant_id}`} className="no-underline">
                        <div className={`glass-card p-8 h-full flex flex-col justify-between group stagger-${(idx % 5) + 1} relative overflow-hidden`}>
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <span className="text-4xl">🧬</span>
                            </div>

                            <div>
                                <div className="flex justify-between items-start mb-8">
                                    <h3 className="text-xl font-bold group-hover:text-primary-purple transition-all duration-300 transform group-hover:translate-x-1">{tenant.name}</h3>
                                    <span className={`status-badge status-badge--${tenant.status}`}>
                                        {tenant.status}
                                    </span>
                                </div>

                                <div className="space-y-4 mb-10 text-sm">
                                    <div className="flex justify-between border-b border-white/5 pb-3">
                                        <span className="text-slate-500 font-medium">Brand Entity</span>
                                        <span className="text-white font-bold">{tenant.brand_name}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-white/5 pb-3">
                                        <span className="text-slate-500 font-medium">Catalog Depth</span>
                                        <span className="text-cyan-400 font-bold uppercase tracking-wider">{tenant.products.length} Items</span>
                                    </div>
                                    <div className="flex flex-col gap-2">
                                        <span className="text-slate-500 font-medium text-[11px] uppercase tracking-widest opacity-50">Agent Specialization</span>
                                        <div className="flex flex-wrap gap-2">
                                            {tenant.agent.roles.map(role => (
                                                <span key={role} className="bg-white/5 px-2.5 py-1 rounded-md text-[9px] uppercase font-black tracking-widest border border-white/5">
                                                    {role}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-between items-center pt-8 border-t border-white/5">
                                <span className="text-[10px] text-slate-500 font-black uppercase tracking-widest opacity-40">
                                    REF_{tenant.tenant_id.slice(-6).toUpperCase()}
                                </span>
                                <div className="flex items-center gap-6">
                                    <a
                                        href={`${(import.meta as any).env?.VITE_VOICE_UI_URL || 'http://localhost:5173'}/tenants?auto=${tenant.tenant_id}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-emerald-400 font-black text-[10px] uppercase tracking-widest hover:text-emerald-300 transition-colors flex items-center gap-1.5"
                                        onClick={(e) => e.stopPropagation()}
                                    >
                                        <span>Launch Agent</span>
                                        <span className="text-xs">↗</span>
                                    </a>
                                    <span className="text-primary-purple font-black text-[10px] uppercase tracking-widest group-hover:translate-x-1 transition-transform">
                                        Configure →
                                    </span>
                                </div>
                            </div>
                        </div>
                    </Link>
                ))}

                {tenants.length === 0 && (
                    <div className="glass-card col-span-full text-center py-20 bg-primary-purple/5 border-dashed border-primary-purple/20">
                        <div className="text-5xl mb-6 opacity-20">📡</div>
                        <h3 className="text-2xl font-black mb-4">No Neural Tenants Found</h3>
                        <p className="text-slate-500 mb-10 max-w-md mx-auto italic font-medium leading-relaxed">Start by initializing your first tenant configuration to begin agent training sequences.</p>
                        <Link to="/tenants/new" className="btn btn-primary px-12 py-4">Initialize Nexus Protocol</Link>
                    </div>
                )}
            </div>
        </section>
    );
};

export default TenantList;
