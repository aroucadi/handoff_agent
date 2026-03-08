import React, { useEffect, useState } from 'react';
import { useParams, Routes, Route } from 'react-router-dom';
import RoleSelection from './RoleSelection';
import Dashboard from './Dashboard';
import BriefingSession from './BriefingSession';

const VoiceTenantLayout: React.FC = () => {
    const { slug } = useParams<{ slug: string }>();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const resolve = async () => {
            try {
                // In production, the API URL might need to be absolute or proxied
                // For this demo, we assume the backend is reachable at /api
                const resp = await fetch(`/api/resolve-tenant?slug=${slug}`);
                if (!resp.ok) throw new Error('Workspace not found');
                const tenant = await resp.json();

                // Store context for the Voice UI components
                localStorage.setItem('tenant_id', tenant.tenant_id);
                if (tenant.synapse_tenant_token) {
                    localStorage.setItem('synapse_tenant_token', tenant.synapse_tenant_token);
                }

                // Also store agent config for initial branding if needed
                localStorage.setItem('tenant_name', tenant.name);
                localStorage.setItem('brand_name', tenant.brand_name);

                setLoading(false);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Resolution failed');
                setLoading(false);
            }
        };
        if (slug) resolve();
    }, [slug]);

    if (loading) return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900">
            <div className="text-xl text-blue-400 animate-pulse">Initializing Synapse Workspace...</div>
        </div>
    );

    if (error) return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900">
            <div className="text-xl text-red-500">Error: {error}</div>
        </div>
    );

    return (
        <Routes>
            <Route path="/" element={<RoleSelection />} />
            <Route path="/roles" element={<RoleSelection />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/briefing/:clientId" element={<BriefingSession />} />
        </Routes>
    );
};

export default VoiceTenantLayout;
