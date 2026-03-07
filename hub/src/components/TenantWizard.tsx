import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CrmConfig from './CrmConfig.tsx';
import MappingConfig from './MappingConfig.tsx';
import KnowledgeSourcesConfig from './KnowledgeSourcesConfig.tsx';
import ProductCatalog from './ProductCatalog.tsx';
import AgentConfig from './AgentConfig.tsx';
import TestPanel from './TestPanel.tsx';

interface Product {
    product_id: string;
    name: string;
    description: string;
    knowledge_generated: boolean;
    node_count: number;
}

interface KnowledgeSource {
    source_id: string;
    type: string;
    uri: string;
    name: string;
    config: Record<string, any>;
    status: string;
}

interface TenantConfig {
    name: string;
    brand_name: string;
    crm: {
        crm_type: string;
        crm_url: string;
        auth_method: string;
        field_mapping: Record<string, string>;
        stage_mapping: Record<string, string>;
    };
    product_alias_map: Record<string, string>;
    knowledge_sources: KnowledgeSource[];
    products: Product[];
    agent: {
        roles: string[];
        persona: string;
        brand_name: string;
        stage_display_config: Record<string, string>;
    };
    webhook_url: string;
    status: string;
}

const TenantWizard: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(id ? true : false);

    const [config, setConfig] = useState<TenantConfig>({
        name: '',
        brand_name: '',
        crm: {
            crm_type: 'salesforce',
            crm_url: '',
            auth_method: 'api_key',
            field_mapping: {},
            stage_mapping: {}
        },
        product_alias_map: {},
        knowledge_sources: [],
        products: [],
        agent: {
            roles: ['csm', 'sales', 'support'],
            persona: '',
            brand_name: '',
            stage_display_config: {
                "closed_won": "Won",
                "prospecting": "Prospecting",
                "qualification": "Qualifying",
                "negotiation": "Negotiating",
                "implemented": "Deployed",
                "closed_lost": "Lost"
            }
        },
        webhook_url: '',
        status: 'configuring'
    });

    const [isTesting, setIsTesting] = useState(false);
    const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

    const handleTestConnection = async () => {
        setIsTesting(true);
        setTestResult(null);

        try {
            const baseUrl = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_HUB_API_URL || '';
            const resp = await fetch(`${baseUrl}/api/test-connection`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crm_type: config.crm.crm_type,
                    crm_url: config.crm.crm_url || '',
                    auth_method: config.crm.auth_method
                })
            });
            const data = await resp.json();
            setTestResult({
                success: data.success,
                message: data.message
            });
        } catch (err) {
            console.error("Test handshake failed", err);
            setTestResult({
                success: false,
                message: "Neural handshake failed: Network error or Hub API unreachable."
            });
        } finally {
            setIsTesting(false);
        }
    };

    useEffect(() => {
        if (id) {
            const baseUrl = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_HUB_API_URL || '';
            fetch(`${baseUrl}/api/tenants/${id}`)
                .then(res => res.json())
                .then(data => {
                    setConfig(data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error("Failed to load tenant", err);
                    setLoading(false);
                });
        }
    }, [id]);

    const handleSave = async () => {
        const method = id ? 'PATCH' : 'POST';
        const baseUrl = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_HUB_API_URL || '';
        const url = id ? `${baseUrl}/api/tenants/${id}` : `${baseUrl}/api/tenants`;

        try {
            const resp = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            if (resp.ok) {
                navigate('/');
            }
        } catch (err) {
            console.error("Save failed", err);
        }
    };

    const addProduct = async (name: string, description: string) => {
        const baseUrl = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_HUB_API_URL || '';
        if (id) {
            const resp = await fetch(`${baseUrl}/api/tenants/${id}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });
            const newProduct = await resp.json();
            setConfig({ ...config, products: [...config.products, newProduct] });
        } else {
            const newProduct = { product_id: Math.random().toString(36), name, description, knowledge_generated: false, node_count: 0 };
            setConfig({ ...config, products: [...config.products, newProduct] });
        }
    };

    const removeProduct = async (pid: string) => {
        const baseUrl = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_HUB_API_URL || '';
        if (id) {
            await fetch(`${baseUrl}/api/tenants/${id}/products/${pid}`, { method: 'DELETE' });
        }
        setConfig({ ...config, products: config.products.filter(p => p.product_id !== pid) });
    };

    const generateKnowledge = async () => {
        const baseUrl = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_HUB_API_URL || '';
        if (!id) {
            const resp = await fetch(`${baseUrl}/api/tenants`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const data = await resp.json();
            navigate(`/tenants/${data.tenant_id}`);
            return;
        }

        const resp = await fetch(`${baseUrl}/api/tenants/${id}/generate-knowledge`, { method: 'POST' });
        if (resp.ok) {
            const updated = await fetch(`${baseUrl}/api/tenants/${id}`).then(r => r.json());
            setConfig(updated);
        }
    };

    if (loading) return <div className="text-center" style={{ marginTop: '100px' }}>Loading configuration...</div>;

    const steps = [
        { n: 1, title: 'CRM Connection' },
        { n: 2, title: 'Mapping & Taxonomy' },
        { n: 3, title: 'Knowledge Sources' },
        { n: 4, title: 'Product Catalog' },
        { n: 5, title: 'Agent Config' },
        { n: 6, title: 'Review & Launch' }
    ];

    return (
        <div className="wizard max-w-5xl mx-auto">
            <div className="wizard-header mb-12">
                <h1 className="text-4xl font-black mb-2 text-gradient">
                    {id ? `Reconfiguring ${config.name}` : 'Initialize Neural Tenant'}
                </h1>
                <p className="text-slate-400">
                    Precision configuration for Synapse high-fidelity agent grounding.
                </p>
            </div>

            <div className="wizard-progress flex gap-4 mb-12 p-2 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-3xl">
                {steps.map(s => (
                    <div
                        key={s.n}
                        className={`
                            flex-1 py-4 text-center rounded-xl cursor-pointer transition-all duration-500 flex flex-col items-center justify-center gap-2 relative
                            ${step === s.n
                                ? 'bg-primary-purple text-white font-bold shadow-lg shadow-primary-purple/20 scale-[1.02]'
                                : step > s.n
                                    ? 'text-emerald-400'
                                    : 'text-slate-500'
                            }
                        `}
                        onClick={() => setStep(s.n)}
                    >
                        <div className={`
                            w-8 h-8 rounded-full flex items-center justify-center text-xs font-black border-2 mb-1
                            ${step === s.n ? 'border-white bg-white/20' : step > s.n ? 'border-emerald-400 bg-emerald-400/10' : 'border-slate-700 bg-slate-800'}
                        `}>
                            {step > s.n ? '✓' : s.n}
                        </div>
                        <span className="text-[10px] uppercase font-black tracking-widest">{s.title}</span>
                        {step === s.n && (
                            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-white shadow-[0_0_10px_white]" />
                        )}
                    </div>
                ))}
            </div>

            <div className="wizard-container min-h-[500px]">
                <div className="glass-card p-10 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-purple via-transparent to-cyan-400 opacity-30" />

                    {step === 1 && (
                        <CrmConfig
                            crm={config.crm}
                            onChange={(updates) => setConfig({ ...config, crm: { ...config.crm, ...updates } })}
                            onTest={handleTestConnection}
                            isTesting={isTesting}
                            testResult={testResult}
                            tenantId={id}
                        />
                    )}

                    {step === 2 && (
                        <MappingConfig
                            crm={config.crm}
                            product_alias_map={config.product_alias_map}
                            onCrmChange={(updates) => setConfig({ ...config, crm: { ...config.crm, ...updates } })}
                            onAliasChange={(product_alias_map) => setConfig({ ...config, product_alias_map })}
                        />
                    )}

                    {step === 3 && (
                        <KnowledgeSourcesConfig
                            sources={config.knowledge_sources || []}
                            onChange={(knowledge_sources) => setConfig({ ...config, knowledge_sources })}
                        />
                    )}

                    {step === 4 && (
                        <ProductCatalog
                            products={config.products}
                            onAdd={addProduct}
                            onRemove={removeProduct}
                            onGenerate={generateKnowledge}
                        />
                    )}

                    {step === 5 && (
                        <AgentConfig
                            agent={config.agent}
                            brandName={config.brand_name}
                            onChange={(updates) => setConfig({ ...config, agent: { ...config.agent, ...updates } })}
                            onBrandChange={(brand_name) => setConfig({ ...config, brand_name, agent: { ...config.agent, brand_name } })}
                        />
                    )}

                    {step === 6 && (
                        <TestPanel tenantId={id || ''} config={config} />
                    )}
                </div>

                <div className="wizard-actions flex justify-between mt-12 pt-8 border-t border-white/5">
                    <button
                        className="btn btn-secondary"
                        onClick={() => step > 1 ? setStep(step - 1) : navigate('/')}
                    >
                        {step === 1 ? 'Abort Nexus' : '← Previous Protocol'}
                    </button>

                    {step < 6 ? (
                        <button className="btn btn-primary" onClick={() => setStep(step + 1)}>
                            Progress to {steps[step].title} →
                        </button>
                    ) : (
                        <button className="btn btn-primary bg-emerald-500 hover:bg-emerald-400 shadow-emerald-500/20" onClick={handleSave}>
                            Finalize & Launch Session 🚀
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TenantWizard;
