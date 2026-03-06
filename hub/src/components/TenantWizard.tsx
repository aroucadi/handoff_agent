import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CrmConfig from './CrmConfig.tsx';
import ProductCatalog from './ProductCatalog.tsx';
import AgentConfig from './AgentConfig.tsx';
import TestPanel from './TestPanel.tsx';

const TenantWizard: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(id ? true : false);

    const [config, setConfig] = useState<any>({
        name: '',
        brand_name: '',
        crm: {
            crm_type: 'salesforce',
            crm_url: '',
            auth_method: 'api_key',
            field_mapping: {}
        },
        products: [],
        agent: {
            roles: ['csm', 'sales', 'support'],
            persona: '',
            brand_name: ''
        },
        webhook_url: '',
        status: 'configuring'
    });

    useEffect(() => {
        if (id) {
            fetch(`/api/tenants/${id}`)
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
        const url = id ? `/api/tenants/${id}` : '/api/tenants';

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
        if (id) {
            // If editing, save to backend immediately
            const resp = await fetch(`/api/tenants/${id}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });
            const newProduct = await resp.json();
            setConfig({ ...config, products: [...config.products, newProduct] });
        } else {
            // Local state if creating new
            const newProduct = { product_id: Math.random().toString(36), name, description, knowledge_generated: false, node_count: 0 };
            setConfig({ ...config, products: [...config.products, newProduct] });
        }
    };

    const removeProduct = async (pid: string) => {
        if (id) {
            await fetch(`/api/tenants/${id}/products/${pid}`, { method: 'DELETE' });
        }
        setConfig({ ...config, products: config.products.filter((p: any) => p.product_id !== pid) });
    };

    const generateKnowledge = async () => {
        if (!id) {
            // Must save tenant first to generate knowledge
            const resp = await fetch('/api/tenants', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const data = await resp.json();
            navigate(`/tenants/${data.tenant_id}`);
            // Wait for redirect or just return. User will need to click again.
            return;
        }

        const resp = await fetch(`/api/tenants/${id}/generate-knowledge`, { method: 'POST' });
        if (resp.ok) {
            // Refresh config
            const updated = await fetch(`/api/tenants/${id}`).then(r => r.json());
            setConfig(updated);
        }
    };

    if (loading) return <div className="text-center" style={{ marginTop: '100px' }}>Loading configuration...</div>;

    const steps = [
        { n: 1, title: 'CRM Connection' },
        { n: 2, title: 'Product Catalog' },
        { n: 3, title: 'Agent Config' },
        { n: 4, title: 'Review & Launch' }
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
                            onChange={(crm) => setConfig({ ...config, crm })}
                            onTest={() => { }} // TODO: trigger test
                        />
                    )}

                    {step === 2 && (
                        <ProductCatalog
                            products={config.products}
                            onAdd={addProduct}
                            onRemove={removeProduct}
                            onGenerate={generateKnowledge}
                        />
                    )}

                    {step === 3 && (
                        <AgentConfig
                            agent={config.agent}
                            brandName={config.brand_name}
                            onChange={(agent) => setConfig({ ...config, agent })}
                            onBrandChange={(brand_name) => setConfig({ ...config, brand_name, agent: { ...config.agent, brand_name } })}
                        />
                    )}

                    {step === 4 && (
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

                    {step < 4 ? (
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
