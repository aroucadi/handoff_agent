import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
const STATUS_BADGES = {
    not_configured: { label: 'Not Configured', color: 'amber', pulse: false },
    pending: { label: 'Pending Verification', color: 'blue', pulse: true },
    verified: { label: 'Verified', color: 'emerald', pulse: false },
    error: { label: 'Connection Error', color: 'red', pulse: true },
};
const CrmConfig = ({ crm, onChange, onTest, tenantId, isTesting, testResult }) => {
    const [guide, setGuide] = useState(null);
    const [copied, setCopied] = useState(false);
    const [secretVisible, setSecretVisible] = useState(false);
    useEffect(() => {
        if (tenantId) {
            const token = localStorage.getItem('synapse_tenant_token');
            const headers = {};
            if (token)
                headers['Authorization'] = `Bearer ${token}`;
            const baseUrl = import.meta.env?.VITE_HUB_API_URL || '';
            fetch(`${baseUrl}/api/tenants/${tenantId}/integration-guide`, { headers })
                .then(res => res.json())
                .then(data => setGuide(data))
                .catch(err => console.error('Failed to load integration guide:', err));
        }
    }, [tenantId, crm.crm_type]);
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    const statusConfig = STATUS_BADGES[guide?.integration_status || 'not_configured'];
    return (_jsxs("div", { className: "crm-config", children: [_jsx("h2", { className: "text-2xl font-bold mb-6", children: "Neural CRM Bridge" }), _jsx("p", { className: "text-slate-400 mb-8", children: "Establish a high-bandwidth connection to the system of record for automated graph grounding." }), guide && (_jsxs("div", { className: "glass-card p-4 mb-8 flex justify-between items-center stagger-1 relative overflow-hidden", children: [_jsx("div", { className: "absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent" }), _jsxs("div", { className: "flex items-center gap-4", children: [_jsxs("div", { className: `
                            flex items-center gap-2 px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest
                            bg-${statusConfig.color}-500/10 text-${statusConfig.color}-400 border border-${statusConfig.color}-500/20
                        `, children: [_jsx("div", { className: `w-2 h-2 rounded-full bg-${statusConfig.color}-400 ${statusConfig.pulse ? 'animate-pulse' : ''}` }), statusConfig.label] }), _jsx("span", { className: "text-slate-500 text-[11px] font-bold uppercase tracking-wider", children: "Neural Handshake Status" })] }), guide.integration_status === 'verified' && (_jsxs("div", { className: "text-emerald-400 text-[10px] font-black uppercase tracking-widest flex items-center gap-2", children: [_jsx("span", { children: "Connection Secure" }), _jsx("span", { className: "text-lg", children: "\uD83D\uDEE1\uFE0F" })] }))] })), _jsx("div", { className: "crm-types grid grid-cols-2 md:grid-cols-4 gap-6 mb-12", children: [
                    { id: 'salesforce', icon: '☁️', label: 'Salesforce' },
                    { id: 'hubspot', icon: '🟠', label: 'HubSpot' },
                    { id: 'dynamics', icon: '💎', label: 'Dynamics 365' },
                    { id: 'custom', icon: '⚙️', label: 'Custom API' }
                ].map((item, idx) => (_jsxs("div", { className: `
                            glass-card p-8 text-center cursor-pointer transition-all duration-500 group relative overflow-hidden
                            ${crm.crm_type === item.id
                        ? 'border-primary-purple bg-primary-purple/10 scale-[1.02] shadow-[0_0_30px_rgba(123,57,252,0.1)]'
                        : 'opacity-60 hover:opacity-100 hover:scale-[1.02] hover:bg-white/5'}
                            stagger-${idx + 1}
                        `, onClick: () => onChange({ ...crm, crm_type: item.id }), children: [crm.crm_type === item.id && (_jsx("div", { className: "absolute top-2 right-2 w-2 h-2 rounded-full bg-primary-purple shadow-[0_0_10px_#7b39fc]" })), _jsx("div", { className: "text-4xl mb-4 group-hover:scale-110 transition-transform duration-500", children: item.icon }), _jsx("div", { className: "text-[10px] font-black uppercase tracking-widest text-white", children: item.label })] }, item.id))) }), guide?.webhook_url && (_jsxs("div", { className: "glass-card p-6 mb-6 stagger-2", children: [_jsx("label", { className: "text-[10px] font-black uppercase tracking-widest text-primary-purple mb-3 block", children: "\uD83D\uDCE1 Webhook Endpoint (Auto-Provisioned)" }), _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { className: "input flex-1 text-sm font-mono bg-white/5", value: guide.webhook_url, readOnly: true }), _jsx("button", { className: "px-4 py-2 glass-card text-xs font-bold hover:border-primary-purple/50 transition-all", onClick: () => copyToClipboard(guide.webhook_url), children: copied ? '✓ Copied' : 'Copy' })] }), _jsx("p", { className: "text-white/20 text-[10px] mt-2", children: "Paste this URL in your CRM's outbound webhook configuration" })] })), guide?.webhook_secret && (_jsxs("div", { className: "glass-card p-6 mb-6 stagger-3", children: [_jsx("label", { className: "text-[10px] font-black uppercase tracking-widest text-cyan-400 mb-3 block", children: "\uD83D\uDD10 Webhook Secret (HMAC-SHA256)" }), _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { className: "input flex-1 text-sm font-mono bg-white/5", value: secretVisible ? guide.webhook_secret : '••••••••••••••••••••••••••••••••', readOnly: true }), _jsx("button", { className: "px-4 py-2 glass-card text-xs font-bold hover:border-cyan-500/50 transition-all", onClick: () => setSecretVisible(!secretVisible), children: secretVisible ? 'Hide' : 'Show' })] }), _jsx("p", { className: "text-white/20 text-[10px] mt-2", children: "Use this key to sign webhook payloads with HMAC-SHA256 in the X-Webhook-Signature header" })] })), guide?.setup && (_jsxs("div", { className: "glass-card p-6 mb-8 stagger-4", children: [_jsxs("label", { className: "text-[10px] font-black uppercase tracking-widest text-emerald-400 mb-4 block", children: ["\uD83D\uDCCB ", guide.setup.title, " \u2014 Setup Guide"] }), _jsx("ol", { className: "space-y-3", children: guide.setup.steps.map((step, idx) => (_jsxs("li", { className: "flex gap-3 text-sm text-white/70", children: [_jsx("span", { className: "flex-shrink-0 w-6 h-6 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-[10px] font-bold text-primary-purple", children: idx + 1 }), _jsx("span", { children: step })] }, idx))) }), guide.setup.docs_url && (_jsx("a", { href: guide.setup.docs_url, target: "_blank", rel: "noopener noreferrer", className: "mt-4 inline-flex items-center gap-2 text-xs text-primary-purple hover:text-primary-purple-hover transition-colors", children: "\uD83D\uDCD6 Official Documentation \u2192" }))] })), _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { className: "label", children: "Instance Endpoint URL" }), _jsx("input", { className: "input", value: crm.crm_url || '', onChange: e => onChange({ ...crm, crm_url: e.target.value }), placeholder: "https://client-instance.crm.dynamics.com" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { className: "label", children: "Security Protocol" }), _jsxs("select", { className: "input appearance-none bg-no-repeat bg-[right_1.5rem_center]", value: crm.auth_method, onChange: e => onChange({ ...crm, auth_method: e.target.value }), children: [_jsx("option", { value: "oauth2", children: "OAuth 2.0 (Encrypted Handshake)" }), _jsx("option", { value: "api_key", children: "Static Neural Token / API Key" })] })] }), _jsxs("button", { className: `
                        btn w-full justify-center py-4 relative overflow-hidden group
                        ${isTesting ? 'opacity-70 cursor-wait' : 'btn-secondary border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/5 hover:border-cyan-500/50'}
                    `, onClick: onTest, disabled: isTesting, children: [_jsx("div", { className: "absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/5 to-transparent -translate-x-full group-hover:animate-shimmer" }), _jsxs("span", { className: "relative flex h-2 w-2 mr-2", children: [_jsx("span", { className: `animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isTesting ? 'bg-cyan-400' : 'bg-cyan-500'}` }), _jsx("span", { className: `relative inline-flex rounded-full h-2 w-2 ${isTesting ? 'bg-cyan-400' : 'bg-cyan-500'}` })] }), _jsx("span", { className: "relative z-10", children: isTesting ? 'Analyzing Connection...' : 'Initialize CRM Handshake' })] }), testResult && (_jsxs("div", { className: `
                        glass-card p-4 flex items-center gap-4 border-l-2 text-[11px] font-medium animate-in fade-in slide-in-from-top-4 duration-500
                        ${testResult.success ? 'border-l-emerald-500 bg-emerald-500/5' : 'border-l-rose-500 bg-rose-500/5'}
                    `, children: [_jsx("div", { className: "text-lg", children: testResult.success ? '✅' : '❌' }), _jsx("div", { className: `flex-1 tracking-tight ${testResult.success ? 'text-emerald-400' : 'text-rose-400'}`, children: testResult.message })] }))] })] }));
};
export default CrmConfig;
