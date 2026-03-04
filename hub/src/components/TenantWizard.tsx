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
        <div className="wizard">
            <div className="wizard-header" style={{ marginBottom: '40px' }}>
                <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>
                    {id ? `Edit ${config.name}` : 'New Tenant Setup'}
                </h1>
                <p style={{ color: 'var(--text-secondary)' }}>
                    Complete the steps below to initialize a Synapse instance for your client.
                </p>
            </div>

            <div className="wizard-progress" style={{ display: 'flex', gap: '2px', marginBottom: '40px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', padding: '4px' }}>
                {steps.map(s => (
                    <div
                        key={s.n}
                        className="progress-step"
                        style={{
                            flex: 1,
                            padding: '16px',
                            textAlign: 'center',
                            borderRadius: 'var(--radius-sm)',
                            background: step === s.n ? 'var(--accent)' : 'transparent',
                            color: step === s.n ? 'var(--text-primary)' : 'var(--text-muted)',
                            fontWeight: step === s.n ? 700 : 500,
                            cursor: 'pointer',
                            transition: 'all 0.3s ease'
                        }}
                        onClick={() => setStep(s.n)}
                    >
                        {s.n}. {s.title}
                    </div>
                ))}
            </div>

            <div className="wizard-container">
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

                <div className="wizard-actions" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '60px', paddingTop: '32px', borderTop: '1px solid var(--border)' }}>
                    <button
                        className="btn btn-secondary"
                        onClick={() => step > 1 ? setStep(step - 1) : navigate('/')}
                    >
                        {step === 1 ? 'Cancel Configuration' : '← Back to Step ' + (step - 1)}
                    </button>

                    {step < 4 ? (
                        <button className="btn btn-primary" onClick={() => setStep(step + 1)}>
                            Next Step: {steps[step].title} →
                        </button>
                    ) : (
                        <button className="btn btn-primary" style={{ background: 'var(--green)', boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)' }} onClick={handleSave}>
                            Complete & Launch 🚀
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TenantWizard;
