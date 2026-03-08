import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Wifi, WifiOff, ArrowRight, Loader2, Shield } from 'lucide-react';
import BackgroundVideo from './BackgroundVideo';

interface TenantSummary {
    tenant_id: string;
    name: string;
    brand_name: string;
    crm_type: string;
    integration_status: string;
    roles: string[];
    product_count: number;
    signed_token?: string; // New: context-isolated demo token
}

const CRM_ICONS: Record<string, string> = {
    salesforce: '☁️',
    hubspot: '🟠',
    dynamics: '💎',
    custom: '⚙️',
};

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: typeof Wifi }> = {
    verified: { label: 'Connected', color: 'emerald', icon: Wifi },
    pending: { label: 'Pending', color: 'amber', icon: Wifi },
    error: { label: 'Error', color: 'red', icon: WifiOff },
    not_configured: { label: 'Not Configured', color: 'white/30', icon: WifiOff },
};

export default function TenantPicker() {
    const navigate = useNavigate();
    const [tenants, setTenants] = useState<TenantSummary[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            try {
                const baseUrl = import.meta.env.VITE_API_URL || '';
                const res = await fetch(`${baseUrl}/api/tenants`);
                const data = await res.json();
                setTenants(data.tenants || []);
            } catch (err) {
                console.error('Failed to load tenants:', err);
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    return (
        <div className="relative min-h-screen text-white font-manrope selection:bg-primary-purple/30">
            <BackgroundVideo
                src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260215_121759_424f8e9c-d8bd-4974-9567-52709dfb6842.mp4"
            />

            <main className="relative pt-8 pb-20 px-6 max-w-5xl mx-auto flex flex-col items-center z-[2]">

                {/* Header */}
                <div className="text-center mb-16 animate-fade-in">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 glass-card mb-8 border-white/10">
                        <Shield size={14} className="text-primary-purple" />
                        <span className="text-[11px] font-bold font-cabin uppercase tracking-[0.2em] text-white/60">SECURE TENANT ACCESS</span>
                    </div>

                    <h2 className="text-4xl md:text-[56px] font-medium font-inter tracking-tight leading-tight mb-6 text-gradient">
                        Select Your Organization
                    </h2>
                    <p className="text-lg text-[#f6f7f9] opacity-70 max-w-2xl mx-auto leading-relaxed">
                        Choose the tenant workspace to access. Each organization has its own CRM integration, knowledge graphs, and AI agent configuration.
                    </p>
                </div>

                {/* Tenant Grid */}
                {loading ? (
                    <div className="flex flex-col items-center gap-6 py-32">
                        <Loader2 size={48} className="text-primary-purple animate-spin" />
                        <p className="text-white/30 font-bold font-inter tracking-[0.3em] uppercase text-[10px]">Loading organizations</p>
                    </div>
                ) : tenants.length === 0 ? (
                    <div className="glass-card py-24 px-12 text-center border-dashed border-white/10 max-w-lg">
                        <Building2 size={48} className="text-white/10 mx-auto mb-6" />
                        <h3 className="text-white/40 font-inter text-xl mb-4 font-bold">No Tenants Configured</h3>
                        <p className="text-white/20 text-sm mb-8">Create a tenant in the Synapse Hub to get started.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
                        {tenants.map((tenant) => {
                            const status = STATUS_CONFIG[tenant.integration_status] || STATUS_CONFIG.not_configured;
                            const StatusIcon = status.icon;
                            return (
                                <div
                                    key={tenant.tenant_id}
                                    onClick={() => {
                                        // Store signed token for authoritative context
                                        if (tenant.signed_token) {
                                            localStorage.setItem('synapse_tenant_token', tenant.signed_token);
                                        }
                                        localStorage.setItem('synapse_tenant_id', tenant.tenant_id);
                                        navigate(`/roles?tenant_id=${tenant.tenant_id}`);
                                    }}
                                >
                                    {/* Hover glow */}
                                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-purple/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                                    {/* Header row */}
                                    <div className="relative z-10 flex justify-between items-start">
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl">{CRM_ICONS[tenant.crm_type] || '⚙️'}</span>
                                                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/30">
                                                    {tenant.crm_type}
                                                </span>
                                            </div>
                                            <h3 className="text-2xl font-bold font-inter group-hover:text-primary-purple transition-colors tracking-tight">
                                                {tenant.brand_name || tenant.name}
                                            </h3>
                                        </div>

                                        {/* Integration Status */}
                                        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest bg-${status.color}-500/10 text-${status.color}-400 border border-${status.color}-500/20`}>
                                            <StatusIcon size={10} />
                                            {status.label}
                                        </div>
                                    </div>

                                    {/* Stats row */}
                                    <div className="relative z-10 flex gap-8 text-sm">
                                        <div>
                                            <p className="text-[10px] uppercase tracking-[0.2em] text-white/20 font-black mb-1">Roles</p>
                                            <p className="text-white/70 font-bold">{tenant.roles.length} active</p>
                                        </div>
                                        <div>
                                            <p className="text-[10px] uppercase tracking-[0.2em] text-white/20 font-black mb-1">Products</p>
                                            <p className="text-white/70 font-bold">{tenant.product_count}</p>
                                        </div>
                                        <div>
                                            <p className="text-[10px] uppercase tracking-[0.2em] text-white/20 font-black mb-1">ID</p>
                                            <p className="text-white/40 font-mono text-xs">{tenant.tenant_id.slice(0, 8)}…</p>
                                        </div>
                                    </div>

                                    {/* Enter button */}
                                    <button className="relative z-10 w-full py-3.5 bg-white/5 border border-white/10 text-white/70 font-bold font-cabin text-sm uppercase tracking-widest rounded-xl hover:bg-primary-purple hover:text-white hover:border-primary-purple transition-all flex items-center justify-center gap-3 group-hover:bg-primary-purple group-hover:text-white group-hover:border-primary-purple">
                                        Enter Workspace <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* Info */}
                <p className="mt-12 text-white/20 text-xs text-center max-w-md">
                    In production, this page is replaced by SSO authentication. Your identity determines which tenant workspace loads automatically.
                </p>
            </main>
        </div>
    );
}
