import React, { useEffect, useState } from 'react';
import { useParams, Routes, Route } from 'react-router-dom';
import TenantWizard from './TenantWizard';

const TenantLayout: React.FC = () => {
    const { slug } = useParams<{ slug: string }>();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const resolve = async () => {
            try {
                const resp = await fetch(`/api/resolve-tenant?slug=${slug}`);
                if (!resp.ok) throw new Error('Tenant not found');
                const tenant = await resp.json();

                // Store context
                localStorage.setItem('tenant_id', tenant.tenant_id);
                if (tenant.synapse_tenant_token) {
                    localStorage.setItem('synapse_tenant_token', tenant.synapse_tenant_token);
                }
                setLoading(false);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Resolution failed');
                setLoading(false);
            }
        };
        if (slug) resolve();
    }, [slug]);

    if (loading) return <div className="p-12 text-center text-white">Resolving Workspace...</div>;
    if (error) return <div className="p-12 text-center text-red-500">Error: {error}</div>;

    return (
        <Routes>
            <Route path="/" element={<TenantWizard />} />
            <Route path="/config" element={<TenantWizard />} />
        </Routes>
    );
};

export default TenantLayout;
