import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
const KnowledgeSourcesConfig = ({ sources, onChange }) => {
    const handleAddSource = (type) => {
        const newSource = {
            source_id: Math.random().toString(36).substring(7),
            type,
            uri: '',
            name: '',
            config: {},
            status: 'pending'
        };
        onChange([...sources, newSource]);
    };
    const handleUpdateSource = (id, updates) => {
        onChange(sources.map(s => s.source_id === id ? { ...s, ...updates } : s));
    };
    const handleRemoveSource = (id) => {
        onChange(sources.filter(s => s.source_id !== id));
    };
    const handleConfigChange = (id, key, value) => {
        onChange(sources.map(s => s.source_id === id ? { ...s, config: { ...s.config, [key]: value } } : s));
    };
    return (_jsxs("div", { className: "knowledge-sources-config", children: [_jsx("h2", { className: "text-2xl font-bold mb-6", children: "Neural Knowledge Connectors" }), _jsx("p", { className: "text-slate-400 mb-8", children: "Connect external enterprise repositories to ground the agent's reasoning in your private technical documentation." }), _jsxs("div", { className: "flex gap-4 mb-8", children: [_jsx("button", { className: "btn btn-secondary text-xs flex-1", onClick: () => handleAddSource('website_crawl'), children: "+ Website" }), _jsx("button", { className: "btn btn-secondary text-xs flex-1", onClick: () => handleAddSource('zendesk_api'), children: "+ Zendesk" }), _jsx("button", { className: "btn btn-secondary text-xs flex-1", onClick: () => handleAddSource('confluence_api'), children: "+ Confluence" })] }), _jsxs("div", { className: "space-y-6", children: [sources.map(source => (_jsxs("div", { className: "glass-card p-6 border-white/5 relative group", children: [_jsx("button", { className: "absolute top-4 right-4 text-rose-400/50 hover:text-rose-400 text-xs", onClick: () => handleRemoveSource(source.source_id), children: "[ DISCONNECT ]" }), _jsxs("div", { className: "flex items-center gap-4 mb-6", children: [_jsx("div", { className: "w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-xl", children: source.type === 'zendesk_api' ? '🧡' : source.type === 'confluence_api' ? '💙' : '🌐' }), _jsxs("div", { children: [_jsx("h3", { className: "text-sm font-bold uppercase tracking-wider text-white", children: source.type.replace('_', ' ') }), _jsx("p", { className: "text-[10px] text-white/20 font-mono", children: source.source_id })] })] }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-6", children: [_jsxs("div", { className: "form-group mb-0", children: [_jsx("label", { className: "label", children: "Endpoint URI / Subdomain" }), _jsx("input", { className: "input !text-xs", value: source.uri, onChange: e => handleUpdateSource(source.source_id, { uri: e.target.value }), placeholder: source.type === 'website_crawl' ? 'https://docs.example.com' : 'instance-subdomain' })] }), source.type === 'zendesk_api' && (_jsxs("div", { className: "form-group mb-0", children: [_jsx("label", { className: "label", children: "Zendesk API Token" }), _jsx("input", { className: "input !text-xs", type: "password", value: source.config.api_token || '', onChange: e => handleConfigChange(source.source_id, 'api_token', e.target.value), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022" })] })), source.type === 'confluence_api' && (_jsxs(_Fragment, { children: [_jsxs("div", { className: "form-group mb-0", children: [_jsx("label", { className: "label", children: "Space Key" }), _jsx("input", { className: "input !text-xs", value: source.config.space_key || '', onChange: e => handleConfigChange(source.source_id, 'space_key', e.target.value), placeholder: "KB" })] }), _jsxs("div", { className: "form-group mb-0", children: [_jsx("label", { className: "label", children: "Auth Token / API Key" }), _jsx("input", { className: "input !text-xs", type: "password", value: source.config.auth_token || '', onChange: e => handleConfigChange(source.source_id, 'auth_token', e.target.value), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022" })] })] }))] })] }, source.source_id))), sources.length === 0 && (_jsx("div", { className: "text-center py-12 border border-dashed border-white/10 rounded-2xl text-white/20 text-sm", children: "No external knowledge sources connected." }))] })] }));
};
export default KnowledgeSourcesConfig;
