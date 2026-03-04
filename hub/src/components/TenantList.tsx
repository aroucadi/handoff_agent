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

    if (loading) return <div className="text-center">Loading tenants...</div>;

    return (
        <section className="tenant-dashboard">
            <div className="flex justify-between items-center mb-12">
                <div>
                    <h1 className="text-4xl font-black mb-2 text-gradient">Nexus Dashboard</h1>
                    <p className="text-slate-400">Manage neural tenant instances and agent grounding configurations.</p>
                </div>
                <div className="flex gap-8">
                    <div className="glass-card p-4 px-6 text-center min-w-[120px] stagger-1">
                        <span className="label block text-[10px] mb-1">Total Nodes</span>
                        <div className="text-3xl font-black italic">{tenants.length}</div>
                    </div>
                    <div className="glass-card p-4 px-6 text-center min-w-[120px] stagger-2">
                        <span className="label block text-[10px] mb-1 text-emerald-400">Live Agents</span>
                        <div className="text-3xl font-black text-emerald-400 italic">
                            {tenants.filter(t => t.status === 'active' || t.status === 'ready').length}
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tenants.map((tenant, idx) => (
                    <Link key={tenant.tenant_id} to={`/tenants/${tenant.tenant_id}`} className="no-underline">
                        <div className={`glass-card p-6 h-full flex flex-col justify-between group stagger-${(idx % 5) + 1}`}>
                            <div>
                                <div className="flex justify-between items-start mb-6">
                                    <h3 className="text-xl font-bold group-hover:text-primary-purple transition-all duration-300 transform group-hover:translate-x-1">{tenant.name}</h3>
                                    <span className={`status-badge status-badge--${tenant.status}`}>
                                        {tenant.status}
                                    </span>
                                </div>

                                <div className="space-y-3 mb-8 text-sm">
                                    <div className="flex justify-between border-b border-white/5 pb-2">
                                        <span className="text-slate-500 font-medium">Brand Entity</span>
                                        <span className="text-white font-semibold">{tenant.brand_name}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-white/5 pb-2">
                                        <span className="text-slate-500 font-medium">Catalog Depth</span>
                                        <span className="text-cyan-400 font-semibold">{tenant.products.length} Items</span>
                                    </div>
                                    <div className="flex flex-col gap-1.5">
                                        <span className="text-slate-500 font-medium">Agent Specialization</span>
                                        <div className="flex flex-wrap gap-1.5">
                                            {tenant.agent.roles.map(role => (
                                                <span key={role} className="bg-white/5 px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider">
                                                    {role}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-between items-center pt-6 border-t border-white/5">
                                <span className="text-[11px] text-slate-500 font-medium uppercase tracking-widest">
                                    REF_{tenant.tenant_id.slice(-6).toUpperCase()}
                                </span>
                                <span className="text-primary-purple font-bold text-xs uppercase tracking-widest group-hover:translate-x-1 transition-transform">
                                    Configure Nexus →
                                </span>
                            </div>
                        </div>
                    </Link>
                ))}

                {tenants.length === 0 && (
                    <div className="glass-card col-span-full text-center py-20 bg-primary-purple/5">
                        <h3 className="text-2xl font-black mb-4">No Neural Tenants Found</h3>
                        <p className="text-slate-400 mb-8 max-w-md mx-auto italic">Start by initializing your first tenant configuration to begin agent training.</p>
                        <Link to="/tenants/new" className="btn btn-primary">Initialize Nexus</Link>
                    </div>
                )}
            </div>
        </section>
    );
};

export default TenantList;
