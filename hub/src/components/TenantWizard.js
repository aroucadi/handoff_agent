import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CrmConfig from './CrmConfig';
import MappingConfig from './MappingConfig';
import KnowledgeSourcesConfig from './KnowledgeSourcesConfig';
import ProductCatalog from './ProductCatalog';
import AgentConfig from './AgentConfig';
import TestPanel from './TestPanel';
import RoleViewConfig from './RoleViewConfig';
const STEPS = [
    'Identity',
    'CRM Config',
    'Taxonomy & Mapping',
    'Role Personas',
    'Knowledge Sources',
    'Product Catalog',
    'Agent Config',
    'Review & Launch'
];
const TenantWizard = ({ step: initialStep }) => {
    const { id: legacyId, slug } = useParams();
    const navigate = useNavigate();
    const [step, setStep] = useState(initialStep || 1);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    // Resolve effective ID from context or URL
    const id = legacyId || localStorage.getItem('tenant_id');
    const [config, setConfig] = useState({
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
        terminology_overrides: {
            account: "Client",
            case: "Deal"
        },
        knowledge_sources: [],
        products: [],
        agent: {
            roles: ['csm', 'sales', 'support'],
            persona: '',
            brand_name: '',
            role_views: {
                csm: { display_name: "Success Dashboard", stage_filter: ["closed_won"], icon: "LayoutDashboard" },
                sales: { display_name: "Pipeline Intelligence", stage_filter: ["prospecting", "qualification", "negotiation"], icon: "Zap" },
                support: { display_name: "Deployment Hub", stage_filter: ["implemented"], icon: "Database" }
            },
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
    const [testResult, setTestResult] = useState(null);
    const handleTestConnection = async () => {
        setIsTesting(true);
        setTestResult(null);
        try {
            const token = localStorage.getItem('synapse_tenant_token');
            const headers = {
                'Content-Type': 'application/json',
                'X-Tenant-Id': id || ''
            };
            if (token)
                headers['Authorization'] = `Bearer ${token}`;
            const baseUrl = import.meta.env?.VITE_HUB_API_URL || '';
            const resp = await fetch(`${baseUrl}/api/test-connection`, {
                method: 'POST',
                headers,
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
        }
        catch (err) {
            console.error("Test handshake failed", err);
            setTestResult({
                success: false,
                message: "Neural handshake failed: Network error or Hub API unreachable."
            });
        }
        finally {
            setIsTesting(false);
        }
    };
    useEffect(() => {
        if (id) {
            const token = localStorage.getItem('synapse_tenant_token');
            const headers = {};
            if (token)
                headers['Authorization'] = `Bearer ${token}`;
            const baseUrl = import.meta.env?.VITE_HUB_API_URL || '';
            fetch(`${baseUrl}/api/tenants/${id}`, { headers })
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
        const baseUrl = import.meta.env?.VITE_HUB_API_URL || '';
        const url = id ? `${baseUrl}/api/tenants/${id}` : `${baseUrl}/api/tenants`;
        const token = localStorage.getItem('synapse_tenant_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token)
            headers['Authorization'] = `Bearer ${token}`;
        setSaving(true);
        try {
            const resp = await fetch(url, {
                method,
                headers,
                body: JSON.stringify(config)
            });
            if (resp.ok) {
                navigate(`/t/${slug}/hub`);
            }
        }
        catch (err) {
            console.error("Save failed", err);
        }
        finally {
            setSaving(false);
        }
    };
    const addProduct = async (name, description) => {
        const token = localStorage.getItem('synapse_tenant_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token)
            headers['Authorization'] = `Bearer ${token}`;
        const baseUrl = import.meta.env?.VITE_HUB_API_URL || '';
        if (id) {
            const resp = await fetch(`${baseUrl}/api/tenants/${id}/products`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ name, description })
            });
            const newProduct = await resp.json();
            setConfig({ ...config, products: [...config.products, newProduct] });
        }
        else {
            const newProduct = { product_id: Math.random().toString(36), name, description, knowledge_generated: false, node_count: 0 };
            setConfig({ ...config, products: [...config.products, newProduct] });
        }
    };
    const removeProduct = async (pid) => {
        const token = localStorage.getItem('synapse_tenant_token');
        const headers = {};
        if (token)
            headers['Authorization'] = `Bearer ${token}`;
        const baseUrl = import.meta.env?.VITE_HUB_API_URL || '';
        if (id) {
            await fetch(`${baseUrl}/api/tenants/${id}/products/${pid}`, { method: 'DELETE', headers });
        }
        setConfig({ ...config, products: config.products.filter(p => p.product_id !== pid) });
    };
    const generateKnowledge = async () => {
        const baseUrl = import.meta.env?.VITE_HUB_API_URL || '';
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
        const token = localStorage.getItem('synapse_tenant_token');
        const headers = {};
        if (token)
            headers['Authorization'] = `Bearer ${token}`;
        const resp = await fetch(`${baseUrl}/api/tenants/${id}/generate-knowledge`, { method: 'POST', headers });
        if (resp.ok) {
            const updated = await fetch(`${baseUrl}/api/tenants/${id}`).then(r => r.json());
            setConfig(updated);
        }
    };
    if (loading)
        return _jsx("div", { className: "text-center", style: { marginTop: '100px' }, children: "Loading configuration..." });
    return (_jsxs("div", { className: "wizard max-w-5xl mx-auto", children: [_jsxs("div", { className: "wizard-header mb-12", children: [_jsx("h1", { className: "text-4xl font-black mb-2 text-gradient", children: id ? `Reconfiguring ${config.name}` : 'Initialize Neural Tenant' }), _jsx("p", { className: "text-slate-400", children: "Precision configuration for Synapse high-fidelity agent grounding." })] }), _jsx("div", { className: "wizard-progress flex gap-4 mb-12 p-2 bg-white/5 rounded-2xl border border-white/5 backdrop-blur-3xl", children: STEPS.map((s, index) => (_jsxs("div", { className: `
                            flex-1 py-4 text-center rounded-xl cursor-pointer transition-all duration-500 flex flex-col items-center justify-center gap-2 relative
                            ${step === index + 1
                        ? 'bg-primary-purple text-white font-bold shadow-lg shadow-primary-purple/20 scale-[1.02]'
                        : step > index + 1
                            ? 'text-emerald-400'
                            : 'text-slate-500'}
                        `, onClick: () => setStep(index + 1), children: [_jsx("div", { className: `
                            w-8 h-8 rounded-full flex items-center justify-center text-xs font-black border-2 mb-1
                            ${step === index + 1 ? 'border-white bg-white/20' : step > index + 1 ? 'border-emerald-400 bg-emerald-400/10' : 'border-slate-700 bg-slate-800'}
                        `, children: step > index + 1 ? '✓' : index + 1 }), _jsx("span", { className: "text-[10px] uppercase font-black tracking-widest", children: s }), step === index + 1 && (_jsx("div", { className: "absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-white shadow-[0_0_10px_white]" }))] }, index))) }), _jsxs("div", { className: "wizard-container min-h-[500px]", children: [_jsxs("div", { className: "glass-card p-10 relative overflow-hidden", children: [_jsx("div", { className: "absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary-purple via-transparent to-cyan-400 opacity-30" }), step === 1 && (_jsxs("div", { className: "text-center text-lg", children: [_jsx("h2", { className: "text-2xl font-bold mb-4", children: "Tenant Identity" }), _jsx("p", { className: "mb-4", children: "Configure the basic identity for your tenant." }), _jsxs("div", { className: "mb-4", children: [_jsx("label", { htmlFor: "tenantName", className: "block text-sm font-medium text-gray-400", children: "Tenant Name" }), _jsx("input", { type: "text", id: "tenantName", className: "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-primary-purple focus:ring-primary-purple", value: config.name, onChange: (e) => setConfig({ ...config, name: e.target.value }) })] }), _jsxs("div", { className: "mb-4", children: [_jsx("label", { htmlFor: "brandName", className: "block text-sm font-medium text-gray-400", children: "Brand Name" }), _jsx("input", { type: "text", id: "brandName", className: "mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-primary-purple focus:ring-primary-purple", value: config.brand_name, onChange: (e) => setConfig({ ...config, brand_name: e.target.value, agent: { ...config.agent, brand_name: e.target.value } }) })] })] })), step === 2 && (_jsx(CrmConfig, { crm: config.crm, onChange: (updates) => setConfig({ ...config, crm: { ...config.crm, ...updates } }), onTest: handleTestConnection, isTesting: isTesting, testResult: testResult, tenantId: id || undefined })), step === 3 && (_jsx(MappingConfig, { crm: config.crm, product_alias_map: config.product_alias_map, terminology_overrides: config.terminology_overrides, onCrmChange: (crm) => setConfig({ ...config, crm }), onAliasChange: (map) => setConfig({ ...config, product_alias_map: map }), onTerminologyChange: (overrides) => setConfig({ ...config, terminology_overrides: overrides }) })), step === 4 && (_jsx(RoleViewConfig, { role_views: config.agent.role_views, stage_display_config: config.agent.stage_display_config, onRoleViewsChange: (views) => setConfig({
                                    ...config,
                                    agent: { ...config.agent, role_views: views, roles: Object.keys(views) }
                                }) })), step === 5 && (_jsx(KnowledgeSourcesConfig, { sources: config.knowledge_sources || [], onChange: (knowledge_sources) => setConfig({ ...config, knowledge_sources }) })), step === 6 && (_jsx(ProductCatalog, { products: config.products, onAdd: addProduct, onRemove: removeProduct, onGenerate: generateKnowledge })), step === 7 && (_jsx(AgentConfig, { agent: config.agent, brandName: config.brand_name, onChange: (updates) => setConfig({ ...config, agent: { ...config.agent, ...updates } }), onBrandChange: (brand_name) => setConfig({ ...config, brand_name, agent: { ...config.agent, brand_name } }) })), step === 8 && (_jsx(TestPanel, { tenantId: id || '', config: config }))] }), _jsxs("div", { className: "wizard-actions flex justify-between mt-12 pt-8 border-t border-white/5", children: [_jsx("button", { className: "btn btn-secondary", onClick: () => step > 1 ? setStep(step - 1) : navigate('/'), children: step === 1 ? 'Abort Nexus' : '← Previous Protocol' }), step < STEPS.length ? (_jsx("button", { className: "btn btn-primary px-12 py-4", onClick: () => setStep(step + 1), disabled: saving, children: "Next Protocol Stage \u2192" })) : (_jsx("button", { className: "btn btn-primary bg-emerald-500 hover:bg-emerald-400 shadow-emerald-500/20 px-12 py-4", onClick: handleSave, disabled: saving, children: saving ? 'Launching...' : 'Finalize & Launch Session 🚀' }))] })] })] }));
};
export default TenantWizard;
