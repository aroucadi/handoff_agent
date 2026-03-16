import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { LayoutDashboard, Zap, Database, Briefcase, Settings, Shield, Users } from 'lucide-react';
const ICON_OPTIONS = [
    { id: 'LayoutDashboard', icon: LayoutDashboard },
    { id: 'Zap', icon: Zap },
    { id: 'Database', icon: Database },
    { id: 'Briefcase', icon: Briefcase },
    { id: 'Settings', icon: Settings },
    { id: 'Shield', icon: Shield },
    { id: 'Users', icon: Users },
];
const RoleViewConfig = ({ role_views, stage_display_config, onRoleViewsChange }) => {
    const handleAddRole = () => {
        const id = `role_${Math.random().toString(36).substr(2, 4)}`;
        onRoleViewsChange({
            ...role_views,
            [id]: { display_name: "New Role", stage_filter: [], icon: "LayoutDashboard" }
        });
    };
    const handleUpdateRole = (id, updates) => {
        onRoleViewsChange({
            ...role_views,
            [id]: { ...role_views[id], ...updates }
        });
    };
    const handleRemoveRole = (id) => {
        const newViews = { ...role_views };
        delete newViews[id];
        onRoleViewsChange(newViews);
    };
    const toggleStage = (id, stage) => {
        const currentFilter = role_views[id].stage_filter;
        const newFilter = currentFilter.includes(stage)
            ? currentFilter.filter(s => s !== stage)
            : [...currentFilter, stage];
        handleUpdateRole(id, { stage_filter: newFilter });
    };
    return (_jsxs("div", { className: "role-view-config", children: [_jsx("h2", { className: "text-2xl font-bold mb-6", children: "Workflow Persona Mapping" }), _jsx("p", { className: "text-slate-400 mb-8", children: "Define how different team personas view the product landscape. Map specific roles to the stages they care about most." }), _jsx("div", { className: "flex justify-end mb-6", children: _jsx("button", { className: "btn btn-secondary text-xs py-2", onClick: handleAddRole, children: "+ Add Persona View" }) }), _jsx("div", { className: "space-y-6", children: Object.entries(role_views).map(([id, view]) => (_jsxs("div", { className: "glass-card p-6 border-white/5 relative group", children: [_jsx("button", { className: "absolute top-4 right-4 text-white/10 hover:text-rose-400 transition-colors", onClick: () => handleRemoveRole(id), children: "\u2715" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-8", children: [_jsxs("div", { className: "space-y-4", children: [_jsx("label", { className: "text-[10px] font-black uppercase tracking-[0.2em] text-primary-purple", children: "View Identity" }), _jsxs("div", { className: "space-y-4", children: [_jsx("input", { className: "input w-full !py-3", placeholder: "View Name (e.g. Executive Summary)", value: view.display_name, onChange: (e) => handleUpdateRole(id, { display_name: e.target.value }) }), _jsx("div", { className: "flex flex-wrap gap-2", children: ICON_OPTIONS.map(opt => {
                                                        const Icon = opt.icon;
                                                        return (_jsx("button", { className: `p-2 rounded-lg border transition-all ${view.icon === opt.id ? 'bg-primary-purple/20 border-primary-purple text-primary-purple' : 'bg-white/5 border-white/10 text-white/30 hover:border-white/20'}`, onClick: () => handleUpdateRole(id, { icon: opt.id }), title: opt.id, children: _jsx(Icon, { size: 16 }) }, opt.id));
                                                    }) })] })] }), _jsxs("div", { className: "space-y-4", children: [_jsx("label", { className: "text-[10px] font-black uppercase tracking-[0.2em] text-primary-purple", children: "Stage Filter" }), _jsx("div", { className: "grid grid-cols-2 gap-2", children: Object.entries(stage_display_config).map(([stageId, label]) => (_jsx("button", { className: `text-left px-3 py-2 rounded-lg text-xs border transition-all ${view.stage_filter.includes(stageId) ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-white/5 border-white/10 text-white/20 hover:border-white/20'}`, onClick: () => toggleStage(id, stageId), children: label }, stageId))) })] })] })] }, id))) })] }));
};
export default RoleViewConfig;
