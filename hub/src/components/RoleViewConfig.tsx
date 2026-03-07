import React from 'react';
import { LayoutDashboard, Zap, Database, Briefcase, Settings, Shield, Users } from 'lucide-react';

interface RoleView {
    display_name: string;
    stage_filter: string[];
    icon: string;
}

interface RoleViewConfigProps {
    role_views: Record<string, RoleView>;
    stage_display_config: Record<string, string>;
    onRoleViewsChange: (updates: Record<string, RoleView>) => void;
}

const ICON_OPTIONS = [
    { id: 'LayoutDashboard', icon: LayoutDashboard },
    { id: 'Zap', icon: Zap },
    { id: 'Database', icon: Database },
    { id: 'Briefcase', icon: Briefcase },
    { id: 'Settings', icon: Settings },
    { id: 'Shield', icon: Shield },
    { id: 'Users', icon: Users },
];

const RoleViewConfig: React.FC<RoleViewConfigProps> = ({ role_views, stage_display_config, onRoleViewsChange }) => {
    const handleAddRole = () => {
        const id = `role_${Math.random().toString(36).substr(2, 4)}`;
        onRoleViewsChange({
            ...role_views,
            [id]: { display_name: "New Role", stage_filter: [], icon: "LayoutDashboard" }
        });
    };

    const handleUpdateRole = (id: string, updates: Partial<RoleView>) => {
        onRoleViewsChange({
            ...role_views,
            [id]: { ...role_views[id], ...updates }
        });
    };

    const handleRemoveRole = (id: string) => {
        const newViews = { ...role_views };
        delete newViews[id];
        onRoleViewsChange(newViews);
    };

    const toggleStage = (id: string, stage: string) => {
        const currentFilter = role_views[id].stage_filter;
        const newFilter = currentFilter.includes(stage)
            ? currentFilter.filter(s => s !== stage)
            : [...currentFilter, stage];
        handleUpdateRole(id, { stage_filter: newFilter });
    };

    return (
        <div className="role-view-config">
            <h2 className="text-2xl font-bold mb-6">Workflow Persona Mapping</h2>
            <p className="text-slate-400 mb-8">
                Define how different team personas view the product landscape. Map specific roles to the stages they care about most.
            </p>

            <div className="flex justify-end mb-6">
                <button className="btn btn-secondary text-xs py-2" onClick={handleAddRole}>+ Add Persona View</button>
            </div>

            <div className="space-y-6">
                {Object.entries(role_views).map(([id, view]) => (
                    <div key={id} className="glass-card p-6 border-white/5 relative group">
                        <button
                            className="absolute top-4 right-4 text-white/10 hover:text-rose-400 transition-colors"
                            onClick={() => handleRemoveRole(id)}
                        >
                            ✕
                        </button>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-purple">View Identity</label>
                                <div className="space-y-4">
                                    <input
                                        className="input w-full !py-3"
                                        placeholder="View Name (e.g. Executive Summary)"
                                        value={view.display_name}
                                        onChange={(e) => handleUpdateRole(id, { display_name: e.target.value })}
                                    />

                                    <div className="flex flex-wrap gap-2">
                                        {ICON_OPTIONS.map(opt => {
                                            const Icon = opt.icon;
                                            return (
                                                <button
                                                    key={opt.id}
                                                    className={`p-2 rounded-lg border transition-all ${view.icon === opt.id ? 'bg-primary-purple/20 border-primary-purple text-primary-purple' : 'bg-white/5 border-white/10 text-white/30 hover:border-white/20'}`}
                                                    onClick={() => handleUpdateRole(id, { icon: opt.id })}
                                                    title={opt.id}
                                                >
                                                    <Icon size={16} />
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-purple">Stage Filter</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {Object.entries(stage_display_config).map(([stageId, label]) => (
                                        <button
                                            key={stageId}
                                            className={`text-left px-3 py-2 rounded-lg text-xs border transition-all ${view.stage_filter.includes(stageId) ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-white/5 border-white/10 text-white/20 hover:border-white/20'}`}
                                            onClick={() => toggleStage(id, stageId)}
                                        >
                                            {label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RoleViewConfig;
