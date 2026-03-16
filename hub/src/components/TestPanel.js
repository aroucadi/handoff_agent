import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
const TestPanel = ({ tenantId, config }) => {
    const [status, setStatus] = useState([]);
    const [testing, setTesting] = useState(false);
    const runTest = async () => {
        setTesting(true);
        setStatus([{ step: 'Initializing test...', status: 'loading' }]);
        try {
            const res = await fetch(`/api/tenants/${tenantId}/test-webhook`, {
                method: 'POST'
            });
            const data = await res.json();
            setStatus(data.steps || [{ step: 'Failed to trigger test', status: 'error' }]);
        }
        catch {
            setStatus([{ step: 'Network error', status: 'error' }]);
        }
        finally {
            setTesting(false);
        }
    };
    return (_jsxs("div", { className: "test-panel", children: [_jsx("h2", { className: "text-2xl font-bold mb-6 text-gradient", children: "System Verification" }), _jsx("p", { className: "text-slate-400 mb-10", children: "Execute a low-latency pipeline handshake to verify end-to-end grounding integrity." }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-8", children: [_jsxs("div", { className: "config-summary", children: [_jsx("h3", { className: "text-[10px] font-black uppercase tracking-widest mb-4 text-slate-500", children: "Neural Configuration" }), _jsxs("div", { className: "glass-card p-6 space-y-4", children: [_jsxs("div", { className: "flex justify-between items-center border-b border-white/5 pb-3", children: [_jsx("span", { className: "text-xs text-slate-500 font-medium", children: "Active Tenant" }), _jsx("span", { className: "text-sm font-bold text-white", children: config.name })] }), _jsxs("div", { className: "flex justify-between items-center border-b border-white/5 pb-3", children: [_jsx("span", { className: "text-xs text-slate-500 font-medium", children: "Brand Entity" }), _jsx("span", { className: "text-sm font-bold text-primary-purple", children: config.brand_name })] }), _jsxs("div", { className: "flex justify-between items-center border-b border-white/5 pb-3", children: [_jsx("span", { className: "text-xs text-slate-500 font-medium", children: "Link Protocol" }), _jsx("span", { className: "text-sm font-bold text-cyan-400 uppercase tracking-tighter", children: config.crm.crm_type })] }), _jsxs("div", { className: "flex flex-col gap-2", children: [_jsx("span", { className: "text-xs text-slate-500 font-medium", children: "Enabled Perspectives" }), _jsx("div", { className: "flex flex-wrap gap-2", children: config.agent.roles.map((role) => (_jsx("span", { className: "bg-white/5 px-2 py-1 rounded text-[9px] uppercase font-black tracking-widest border border-white/10", children: role }, role))) })] })] })] }), _jsxs("div", { className: "test-runner", children: [_jsx("h3", { className: "text-[10px] font-black uppercase tracking-widest mb-4 text-slate-500", children: "Multimodal Handshake" }), _jsx("button", { className: `
                            btn w-full mb-6 h-12 justify-center group relative overflow-hidden
                            ${testing ? 'opacity-70 bg-white/5' : 'bg-white/5 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10'}
                        `, onClick: runTest, disabled: testing, children: testing ? (_jsxs("div", { className: "flex items-center gap-3", children: [_jsx("div", { className: "w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" }), _jsx("span", { className: "text-[11px] font-black uppercase tracking-widest", children: "Pipeline Analysis..." })] })) : (_jsx("span", { className: "text-[11px] font-black uppercase tracking-widest group-hover:scale-105 transition-transform", children: "\uD83D\uDE80 Trigger Neural Webhook" })) }), _jsx("div", { className: "test-results space-y-3", children: status.map((s, i) => (_jsxs("div", { className: `
                                glass-card p-4 flex items-center gap-4 border-l-2 text-[11px] font-medium transition-all duration-500
                                ${s.status === 'failed' ? 'border-l-rose-500 bg-rose-500/5' :
                                        s.status === 'ok' ? 'border-l-emerald-500 bg-emerald-500/5' :
                                            'border-l-cyan-500 bg-white/5 animate-pulse'}
                                stagger-${(i % 5) + 1}
                            `, children: [_jsx("div", { className: "text-lg", children: s.status === 'ok' ? '✅' : s.status === 'failed' ? '❌' : '⏳' }), _jsx("div", { className: "flex-1 text-slate-200 tracking-tight", children: s.step }), s.timestamp && (_jsx("div", { className: "text-[9px] font-mono text-slate-500 bg-black/20 px-1.5 py-0.5 rounded", children: new Date(s.timestamp).toLocaleTimeString() }))] }, i))) })] })] })] }));
};
export default TestPanel;
