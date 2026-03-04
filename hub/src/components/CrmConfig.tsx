import React from 'react';

interface CrmConfigProps {
    crm: any;
    onChange: (updates: any) => void;
    onTest: () => void;
}

const CrmConfig: React.FC<CrmConfigProps> = ({ crm, onChange, onTest }) => {
    return (
        <div className="crm-config">
            <h2 className="text-2xl font-bold mb-6">Neural CRM Bridge</h2>
            <p className="text-slate-400 mb-8">
                Establish a high-bandwidth connection to the system of record for automated graph grounding.
            </p>

            <div className="crm-types grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                {[
                    { id: 'salesforce', icon: '☁️', label: 'Salesforce' },
                    { id: 'hubspot', icon: '🟠', label: 'HubSpot' },
                    { id: 'dynamics', icon: '💎', label: 'Dynamics 365' },
                    { id: 'custom', icon: '⚙️', label: 'Custom API' }
                ].map((item, idx) => (
                    <div
                        key={item.id}
                        className={`
                            glass-card p-6 text-center cursor-pointer transition-all duration-300 group
                            ${crm.crm_type === item.id ? 'border-primary-purple bg-primary-purple/10 scale-[1.02]' : 'opacity-60 hover:opacity-100 hover:scale-[1.02]'}
                            stagger-${idx + 1}
                        `}
                        onClick={() => onChange({ ...crm, crm_type: item.id })}
                    >
                        <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-500">{item.icon}</div>
                        <div className="text-[10px] font-black uppercase tracking-widest">{item.label}</div>
                    </div>
                ))}
            </div>

            <div className="space-y-6">
                <div className="form-group">
                    <label className="label">Instance Endpoint URL</label>
                    <input
                        className="input"
                        value={crm.crm_url || ''}
                        onChange={e => onChange({ ...crm, crm_url: e.target.value })}
                        placeholder="https://client-instance.crm.dynamics.com"
                    />
                </div>

                <div className="form-group">
                    <label className="label">Security Protocol</label>
                    <select
                        className="input appearance-none bg-no-repeat bg-[right_1.5rem_center]"
                        value={crm.auth_method}
                        onChange={e => onChange({ ...crm, auth_method: e.target.value })}
                    >
                        <option value="oauth2">OAuth 2.0 (Encrypted Handshake)</option>
                        <option value="api_key">Static Neural Token / API Key</option>
                    </select>
                </div>

                <button
                    className="btn btn-secondary w-full justify-center py-4 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/5 hover:border-cyan-500/50 relative overflow-hidden group"
                    onClick={onTest}
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/5 to-transparent -translate-x-full group-hover:animate-shimmer" />
                    <span className="relative flex h-2 w-2 mr-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                    </span>
                    <span className="relative z-10">Initialize CRM Handshake</span>
                </button>
            </div>
        </div>
    );
};

export default CrmConfig;
