import React from 'react';

interface CrmConfigProps {
    crm: any;
    onChange: (updates: any) => void;
    onTest: () => void;
}

const CrmConfig: React.FC<CrmConfigProps> = ({ crm, onChange, onTest }) => {
    return (
        <div className="crm-config">
            <h2 style={{ marginBottom: '24px' }}>Step 1: CRM Connection</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
                Connect Synapse to your client's CRM to enable automated graph generation.
            </p>

            <div className="crm-types" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
                {['salesforce', 'hubspot', 'dynamics', 'custom'].map(type => (
                    <div
                        key={type}
                        className={`card ${crm.crm_type === type ? 'active' : ''}`}
                        onClick={() => onChange({ ...crm, crm_type: type })}
                        style={{
                            textAlign: 'center',
                            padding: '20px',
                            cursor: 'pointer',
                            borderColor: crm.crm_type === type ? 'var(--accent)' : 'var(--border)',
                            background: crm.crm_type === type ? 'var(--bg-card-hover)' : 'var(--bg-card)'
                        }}
                    >
                        <div style={{ fontSize: '24px', marginBottom: '8px' }}>
                            {type === 'salesforce' && '☁️'}
                            {type === 'hubspot' && '🟠'}
                            {type === 'dynamics' && '💎'}
                            {type === 'custom' && '⚙️'}
                        </div>
                        <div style={{ textTransform: 'capitalize', fontWeight: 600 }}>{type}</div>
                    </div>
                ))}
            </div>

            <div className="form-group">
                <label className="label">CRM Instance URL</label>
                <input
                    className="input"
                    value={crm.crm_url || ''}
                    onChange={e => onChange({ ...crm, crm_url: e.target.value })}
                    placeholder="https://acme.my.salesforce.com"
                />
            </div>

            <div className="form-group">
                <label className="label">Authentication Method</label>
                <select
                    className="input"
                    value={crm.auth_method}
                    onChange={e => onChange({ ...crm, auth_method: e.target.value })}
                >
                    <option value="oauth2">OAuth 2.0 (Recommended)</option>
                    <option value="api_key">API Key / Token</option>
                </select>
            </div>

            <button className="btn btn-secondary" onClick={onTest} style={{ color: 'var(--neon-cyan)' }}>
                ⚡ Test CRM Connection
            </button>
        </div>
    );
};

export default CrmConfig;
