import React from 'react';

interface AgentConfigProps {
    agent: {
        roles: string[];
        persona: string;
        brand_name: string;
    };
    brandName: string;
    onChange: (updates: { roles: string[]; persona: string; brand_name: string }) => void;
    onBrandChange: (val: string) => void;
}

const AgentConfig: React.FC<AgentConfigProps> = ({ agent, brandName, onChange, onBrandChange }) => {
    return (
        <div className="agent-config">
            <h2 className="text-2xl font-bold mb-6">Agent Personality Protocol</h2>
            <p className="text-slate-400 mb-8">
                Define the neural identity and conversational boundaries for this tenant.
            </p>

            <div className="form-group">
                <label className="label">Neural Brand Identifier</label>
                <input
                    className="input"
                    value={brandName}
                    onChange={e => onBrandChange(e.target.value)}
                    placeholder="e.g. Acme Intelligence"
                />
                <p className="text-[11px] text-slate-500 mt-2 italic">
                    The agent will prioritize this identity in all multimodal interactions.
                </p>
            </div>

            <div className="form-group">
                <label className="label">Operational Perspectives</label>
                <div className="grid grid-cols-2 gap-3">
                    {['csm', 'sales', 'support', 'strategy'].map((role, idx) => (
                        <label key={role} className={`
                            glass-card flex items-center gap-4 p-4 cursor-pointer transition-all duration-300
                            ${agent.roles.includes(role) ? 'border-primary-purple bg-primary-purple/10' : 'opacity-60 hover:opacity-100'}
                            stagger-${idx + 1}
                        `}>
                            <input
                                type="checkbox"
                                className="w-4 h-4 rounded border-white/20 bg-white/5 text-primary-purple focus:ring-primary-purple"
                                checked={agent.roles.includes(role)}
                                onChange={e => {
                                    const nextRoles = e.target.checked
                                        ? [...agent.roles, role]
                                        : agent.roles.filter(r => r !== role);
                                    onChange({ ...agent, roles: nextRoles });
                                }}
                            />
                            <span className="uppercase text-[11px] font-black tracking-widest">{role}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="form-group">
                <label className="label">Persona Bias Overlay</label>
                <textarea
                    className="textarea"
                    rows={4}
                    value={agent.persona}
                    onChange={e => onChange({ ...agent, persona: e.target.value })}
                    placeholder="Define the specific tone, empathy level, and technical depth..."
                />
            </div>

            <div className="glass-card p-6 bg-primary-purple/5 border-dashed border-primary-purple/30 relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-primary-purple/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <h4 className="text-primary-purple font-black text-[10px] uppercase tracking-widest mb-3 relative z-10">Live Identity Preview</h4>
                <p className="text-sm italic text-slate-300 leading-relaxed relative z-10">
                    "Initializing session. I am your **{brandName || 'Synapse'}** neural operative. Account health metrics are now synchronized..."
                </p>
            </div>
        </div>
    );
};

export default AgentConfig;
