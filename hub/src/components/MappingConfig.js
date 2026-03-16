import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const CANONICAL_STAGES = [
    { id: 'prospecting', label: 'Prospecting' },
    { id: 'qualification', label: 'Qualification' },
    { id: 'negotiation', label: 'Negotiation' },
    { id: 'closed_won', label: 'Closed Won' },
    { id: 'implemented', label: 'Implemented' },
    { id: 'closed_lost', label: 'Closed Lost' }
];
const MappingConfig = ({ crm, product_alias_map, terminology_overrides, onCrmChange, onAliasChange, onTerminologyChange }) => {
    const handleAddStageMapping = () => {
        onCrmChange({
            ...crm,
            stage_mapping: { ...crm.stage_mapping, "": "prospecting" }
        });
    };
    const handleStageMapUpdate = (oldKey, newKey, newValue) => {
        const newMapping = { ...crm.stage_mapping };
        delete newMapping[oldKey];
        newMapping[newKey] = newValue;
        onCrmChange({ ...crm, stage_mapping: newMapping });
    };
    const handleRemoveStageMapping = (key) => {
        const newMapping = { ...crm.stage_mapping };
        delete newMapping[key];
        onCrmChange({ ...crm, stage_mapping: newMapping });
    };
    const handleAddAlias = () => {
        onAliasChange({ ...product_alias_map, "": "" });
    };
    const handleAliasUpdate = (oldKey, newKey, newValue) => {
        const newMap = { ...product_alias_map };
        delete newMap[oldKey];
        newMap[newKey] = newValue;
        onAliasChange(newMap);
    };
    const handleRemoveAlias = (key) => {
        const newMap = { ...product_alias_map };
        delete newMap[key];
        onAliasChange(newMap);
    };
    return (_jsxs("div", { className: "mapping-config", children: [_jsx("h2", { className: "text-2xl font-bold mb-6", children: "Taxonomy & Mapping" }), _jsx("p", { className: "text-slate-400 mb-8", children: "Align your business terminology with Synapse's configuration-driven architecture." }), _jsxs("section", { className: "mb-12", children: [_jsx("div", { className: "flex justify-between items-center mb-6", children: _jsxs("div", { children: [_jsx("h3", { className: "text-lg font-bold text-white", children: "Business Terminology" }), _jsx("p", { className: "text-xs text-white/30", children: "Customize how generic entities are labeled in the UI" })] }) }), _jsxs("div", { className: "grid grid-cols-2 gap-6", children: [_jsxs("div", { className: "glass-card p-4 space-y-2", children: [_jsx("label", { className: "text-[10px] font-black uppercase tracking-widest text-white/20", children: "Account Label" }), _jsx("input", { className: "input w-full !py-2 !text-xs", placeholder: "e.g. Client, Company, Account", value: terminology_overrides.account || '', onChange: (e) => onTerminologyChange({ ...terminology_overrides, account: e.target.value }) })] }), _jsxs("div", { className: "glass-card p-4 space-y-2", children: [_jsx("label", { className: "text-[10px] font-black uppercase tracking-widest text-white/20", children: "Case Label" }), _jsx("input", { className: "input w-full !py-2 !text-xs", placeholder: "e.g. Deal, Opportunity, Project, Ticket", value: terminology_overrides.case || '', onChange: (e) => onTerminologyChange({ ...terminology_overrides, case: e.target.value }) })] })] })] }), _jsxs("section", { className: "mb-12", children: [_jsxs("div", { className: "flex justify-between items-center mb-6", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-lg font-bold text-white", children: "Stage Normalization" }), _jsx("p", { className: "text-xs text-white/30", children: "Translate CRM Deal Stages to Synapse Nexus Stages" })] }), _jsx("button", { className: "btn btn-secondary text-xs py-2", onClick: handleAddStageMapping, children: "+ Add Mapping" })] }), _jsxs("div", { className: "space-y-3", children: [Object.entries(crm.stage_mapping || {}).map(([crmStage, synapseStage]) => (_jsxs("div", { className: "flex gap-4 items-center glass-card p-4", children: [_jsx("input", { className: "input flex-1 !py-2 !text-xs", placeholder: "CRM Stage Name (e.g. Discovery)", value: crmStage, onChange: (e) => handleStageMapUpdate(crmStage, e.target.value, synapseStage) }), _jsx("span", { className: "text-white/20", children: "\u2192" }), _jsx("select", { className: "input flex-1 !py-2 !text-xs", value: synapseStage, onChange: (e) => handleStageMapUpdate(crmStage, crmStage, e.target.value), children: CANONICAL_STAGES.map(s => (_jsx("option", { value: s.id, children: s.label }, s.id))) }), _jsx("button", { className: "text-rose-400 hover:text-rose-300 px-2", onClick: () => handleRemoveStageMapping(crmStage), children: "\u2715" })] }, crmStage))), Object.keys(crm.stage_mapping || {}).length === 0 && (_jsx("div", { className: "text-center py-6 border border-dashed border-white/10 rounded-xl text-white/20 text-xs", children: "No stage mappings defined. Using identity mapping." }))] })] }), _jsxs("section", { children: [_jsxs("div", { className: "flex justify-between items-center mb-6", children: [_jsxs("div", { children: [_jsx("h3", { className: "text-lg font-bold text-white", children: "Product Aliases" }), _jsx("p", { className: "text-xs text-white/30", children: "Map varied CRM product names to canonical Product IDs" })] }), _jsx("button", { className: "btn btn-secondary text-xs py-2", onClick: handleAddAlias, children: "+ Add Alias" })] }), _jsxs("div", { className: "space-y-3", children: [Object.entries(product_alias_map || {}).map(([crmName, productSlug]) => (_jsxs("div", { className: "flex gap-4 items-center glass-card p-4", children: [_jsx("input", { className: "input flex-1 !py-2 !text-xs", placeholder: "CRM Product Name", value: crmName, onChange: (e) => handleAliasUpdate(crmName, e.target.value, productSlug) }), _jsx("span", { className: "text-white/20", children: "\u2192" }), _jsx("input", { className: "input flex-1 !py-2 !text-xs", placeholder: "Synapse Product Slug", value: productSlug, onChange: (e) => handleAliasUpdate(crmName, crmName, e.target.value) }), _jsx("button", { className: "text-rose-400 hover:text-rose-300 px-2", onClick: () => handleRemoveAlias(crmName), children: "\u2715" })] }, crmName))), Object.keys(product_alias_map || {}).length === 0 && (_jsx("div", { className: "text-center py-6 border border-dashed border-white/10 rounded-xl text-white/20 text-xs", children: "No aliases defined. All products must match canonical slugs exactly." }))] })] })] }));
};
export default MappingConfig;
