import React from 'react';

interface AgentConfigProps {
    agent: any;
    brandName: string;
    onChange: (updates: any) => void;
    onBrandChange: (val: string) => void;
}

const AgentConfig: React.FC<AgentConfigProps> = ({ agent, brandName, onChange, onBrandChange }) => {
    return (
        <div className="agent-config">
            <h2 style={{ marginBottom: '24px' }}>Step 3: Agent Personality</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
                Define how Synapse identifies itself and which perspectives it can take.
            </p>

            <div className="form-group">
                <label className="label">Custom Brand Name</label>
                <input
                    className="input"
                    value={brandName}
                    onChange={e => onBrandChange(e.target.value)}
                    placeholder="e.g. AcmeView"
                />
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    The agent will refer to the platform by this name instead of synonyms.
                </p>
            </div>

            <div className="form-group">
                <label className="label">Enabled Agent Roles</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                    {['csm', 'sales', 'support', 'strategy'].map(role => (
                        <label key={role} className="card" style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px',
                            cursor: 'pointer',
                            background: agent.roles.includes(role) ? 'var(--bg-card-hover)' : 'var(--bg-card)',
                            borderColor: agent.roles.includes(role) ? 'var(--accent)' : 'var(--border)'
                        }}>
                            <input
                                type="checkbox"
                                checked={agent.roles.includes(role)}
                                onChange={e => {
                                    const nextRoles = e.target.checked
                                        ? [...agent.roles, role]
                                        : agent.roles.filter((r: string) => r !== role);
                                    onChange({ ...agent, roles: nextRoles });
                                }}
                            />
                            <span style={{ textTransform: 'uppercase', fontWeight: 600 }}>{role}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="form-group">
                <label className="label">Agent Persona Overlay</label>
                <textarea
                    className="textarea"
                    rows={4}
                    value={agent.persona}
                    onChange={e => onChange({ ...agent, persona: e.target.value })}
                    placeholder="E.g. Professional but warm, focused on driving long-term ROI for enterprise clients..."
                />
            </div>

            <div className="card" style={{ background: 'rgba(166, 13, 242, 0.05)', borderStyle: 'dashed' }}>
                <h4 style={{ color: 'var(--accent-light)', marginBottom: '8px', fontSize: '14px' }}>Preview Context</h4>
                <p style={{ fontSize: '13px', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                    "Hi, I'm Synapse, your **{brandName}** assistant. I've analyzed your account health..."
                </p>
            </div>
        </div>
    );
};

export default AgentConfig;
