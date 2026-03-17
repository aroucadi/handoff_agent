import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, Building2, ArrowRight, Loader2 } from 'lucide-react';

interface Tenant {
    tenant_id: string;
    name: string;
    brand_name: string;
    crm?: {
        crm_type: string;
    };
    signed_token?: string;
}

const TenantSelector: React.FC = () => {
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('synapse_tenant_token');
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        fetch('/api/tenants', { headers })
            .then(res => res.json())
            .then(data => {
                setTenants(data.tenants || []);
                setLoading(false);
            })
            .catch(err => {
                console.error('Failed to fetch tenants:', err);
                setLoading(false);
            });
    }, []);

    const filteredTenants = tenants.filter(t =>
        t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.brand_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.tenant_id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="tenant-selector animate-fade-in">
            <div className="hero-section text-center mb-12">
                <h1 className="text-4xl md:text-6xl font-medium font-inter tracking-tight mb-4 text-gradient">
                    Select Tenant Context
                </h1>
                <p className="text-white/50 text-lg font-medium">
                    Choose a tenant to manage its Synapse configuration
                </p>
            </div>

            <div className="max-w-2xl mx-auto space-y-8">
                <div className="flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30" size={20} />
                        <input
                            type="text"
                            placeholder="Search by name or ID..."
                            className="w-full bg-white/5 border border-white/10 rounded-2xl py-5 pl-12 pr-6 text-lg focus:outline-none focus:border-primary-purple/50 focus:ring-4 focus:ring-primary-purple/5 transition-all placeholder:text-white/20"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button
                        onClick={() => navigate('/tenants/new')}
                        className="px-6 rounded-2xl bg-white text-black font-bold hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
                    >
                        <Plus size={20} />
                        <span className="hidden md:inline">Build New</span>
                    </button>
                </div>

                {loading ? (
                    <div className="flex justify-center py-20">
                        <Loader2 className="text-primary-purple animate-spin" size={48} />
                    </div>
                ) : (
                    <div className="grid gap-4">
                        {filteredTenants.map(tenant => (
                            <div
                                key={tenant.tenant_id}
                                onClick={() => {
                                    if (tenant.signed_token) {
                                        localStorage.setItem('synapse_tenant_token', tenant.signed_token);
                                    }
                                    navigate(`/tenants/${tenant.tenant_id}`);
                                }}
                                className="group glass-card p-6 flex items-center justify-between hover:border-primary-purple/50 cursor-pointer transition-all hover:-translate-y-1"
                            >
                                <div className="flex items-center gap-6">
                                    <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:border-primary-purple/30 group-hover:text-primary-purple transition-all">
                                        <Building2 size={24} className="text-white/30 group-hover:text-primary-purple transition-all" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold font-inter group-hover:text-primary-purple transition-colors">
                                            {tenant.name}
                                        </h3>
                                        <p className="text-white/40 text-sm font-medium">
                                            ID: {tenant.tenant_id} • CRM: {(tenant.crm?.crm_type || 'custom').toUpperCase()}
                                        </p>
                                    </div>
                                </div>
                                <div className="p-3 rounded-full bg-white/5 opacity-0 group-hover:opacity-100 transition-all group-hover:bg-primary-purple/10">
                                    <ArrowRight size={20} className="text-primary-purple" />
                                </div>
                            </div>
                        ))}

                        {filteredTenants.length === 0 && (
                            <div className="text-center py-20 border-2 border-dashed border-white/5 rounded-3xl">
                                <p className="text-white/30 font-medium text-lg">No tenants found</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default TenantSelector;
