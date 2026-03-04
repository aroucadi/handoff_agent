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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Dashboard</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Manage your client instances and agent configurations.</p>
                </div>
                <div style={{ display: 'flex', gap: '24px' }}>
                    <div className="stat-item">
                        <span className="label">Total</span>
                        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{tenants.length}</div>
                    </div>
                    <div className="stat-item">
                        <span className="label">Active</span>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--green)' }}>
                            {tenants.filter(t => t.status === 'active' || t.status === 'ready').length}
                        </div>
                    </div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '24px' }}>
                {tenants.map(tenant => (
                    <Link key={tenant.tenant_id} to={`/tenants/${tenant.tenant_id}`} style={{ textDecoration: 'none' }}>
                        <div className="card tenant-card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                                <h3 style={{ fontSize: '20px' }}>{tenant.name}</h3>
                                <span className={`status-badge status-badge--${tenant.status}`}>
                                    {tenant.status}
                                </span>
                            </div>

                            <div style={{ marginBottom: '16px', color: 'var(--text-secondary)', fontSize: '14px' }}>
                                <div style={{ marginBottom: '8px' }}>Brand: <span style={{ color: 'var(--text-primary)' }}>{tenant.brand_name}</span></div>
                                <div style={{ marginBottom: '8px' }}>Products: <span style={{ color: 'var(--text-primary)' }}>{tenant.products.length} catalog items</span></div>
                                <div>Roles: <span style={{ color: 'var(--text-primary)' }}>{tenant.agent.roles.join(', ')}</span></div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
                                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                    Updated {new Date(tenant.updated_at).toLocaleDateString()}
                                </span>
                                <span style={{ color: 'var(--accent)', fontWeight: 600 }}>Edit Config →</span>
                            </div>
                        </div>
                    </Link>
                ))}

                {tenants.length === 0 && (
                    <div className="card" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '60px' }}>
                        <h3 style={{ marginBottom: '16px' }}>No tenants found</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Get started by creating your first tenant configuration.</p>
                        <Link to="/tenants/new" className="btn btn-primary">Create First Tenant</Link>
                    </div>
                )}
            </div>
        </section>
    );
};

export default TenantList;
