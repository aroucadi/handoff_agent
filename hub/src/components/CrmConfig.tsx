import React, { useEffect, useState } from 'react';

interface CrmConfigProps {
    crm: {
        crm_type: string;
        crm_url?: string;
        auth_method: string;
    };
    onChange: (updates: { crm_type?: string; crm_url?: string; auth_method?: string }) => void;
    onTest: () => void;
    tenantId?: string;
}

interface IntegrationGuide {
    webhook_url: string;
    webhook_secret: string;
    integration_status: string;
    setup: {
        title: string;
        steps: string[];
        docs_url?: string;
    };
}

const STATUS_BADGES: Record<string, { label: string; color: string; pulse: boolean }> = {
    not_configured: { label: 'Not Configured', color: 'amber', pulse: false },
    pending: { label: 'Pending Verification', color: 'blue', pulse: true },
    verified: { label: 'Verified', color: 'emerald', pulse: false },
    error: { label: 'Connection Error', color: 'red', pulse: true },
};

const CrmConfig: React.FC<CrmConfigProps> = ({ crm, onChange, onTest, tenantId }) => {
    const [guide, setGuide] = useState<IntegrationGuide | null>(null);
    const [copied, setCopied] = useState(false);
    const [secretVisible, setSecretVisible] = useState(false);

    useEffect(() => {
        if (tenantId) {
            const baseUrl = (import.meta as unknown as { env: Record<string, string> }).env?.VITE_HUB_API_URL || '';
            fetch(`${baseUrl}/api/tenants/${tenantId}/integration-guide`)
                .then(res => res.json())
                .then(data => setGuide(data))
                .catch(err => console.error('Failed to load integration guide:', err));
        }
    }, [tenantId, crm.crm_type]);

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const statusConfig = STATUS_BADGES[guide?.integration_status || 'not_configured'];

    return (
        <div className="crm-config">
            <h2 className="text-2xl font-bold mb-6">Neural CRM Bridge</h2>
            <p className="text-slate-400 mb-8">
                Establish a high-bandwidth connection to the system of record for automated graph grounding.
            </p>

            {/* Integration Status Badge */}
            {guide && (
                <div className="glass-card p-4 mb-8 flex justify-between items-center stagger-1 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent" />
                    <div className="flex items-center gap-4">
                        <div className={`
                            flex items-center gap-2 px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest
                            bg-${statusConfig.color}-500/10 text-${statusConfig.color}-400 border border-${statusConfig.color}-500/20
                        `}>
                            <div className={`w-2 h-2 rounded-full bg-${statusConfig.color}-400 ${statusConfig.pulse ? 'animate-pulse' : ''}`} />
                            {statusConfig.label}
                        </div>
                        <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider">Neural Handshake Status</span>
                    </div>
                    {guide.integration_status === 'verified' && (
                        <div className="text-emerald-400 text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
                            <span>Connection Secure</span>
                            <span className="text-lg">🛡️</span>
                        </div>
                    )}
                </div>
            )}

            <div className="crm-types grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
                {[
                    { id: 'salesforce', icon: '☁️', label: 'Salesforce' },
                    { id: 'hubspot', icon: '🟠', label: 'HubSpot' },
                    { id: 'dynamics', icon: '💎', label: 'Dynamics 365' },
                    { id: 'custom', icon: '⚙️', label: 'Custom API' }
                ].map((item, idx) => (
                    <div
                        key={item.id}
                        className={`
                            glass-card p-8 text-center cursor-pointer transition-all duration-500 group relative overflow-hidden
                            ${crm.crm_type === item.id
                                ? 'border-primary-purple bg-primary-purple/10 scale-[1.02] shadow-[0_0_30px_rgba(123,57,252,0.1)]'
                                : 'opacity-60 hover:opacity-100 hover:scale-[1.02] hover:bg-white/5'}
                            stagger-${idx + 1}
                        `}
                        onClick={() => onChange({ ...crm, crm_type: item.id })}
                    >
                        {crm.crm_type === item.id && (
                            <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary-purple shadow-[0_0_10px_#7b39fc]" />
                        )}
                        <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-500">{item.icon}</div>
                        <div className="text-[10px] font-black uppercase tracking-widest text-white">{item.label}</div>
                    </div>
                ))}
            </div>

            {/* Webhook URL (auto-provisioned) */}
            {guide?.webhook_url && (
                <div className="glass-card p-6 mb-6 stagger-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-primary-purple mb-3 block">
                        📡 Webhook Endpoint (Auto-Provisioned)
                    </label>
                    <div className="flex gap-2">
                        <input
                            className="input flex-1 text-sm font-mono bg-white/5"
                            value={guide.webhook_url}
                            readOnly
                        />
                        <button
                            className="px-4 py-2 glass-card text-xs font-bold hover:border-primary-purple/50 transition-all"
                            onClick={() => copyToClipboard(guide.webhook_url)}
                        >
                            {copied ? '✓ Copied' : 'Copy'}
                        </button>
                    </div>
                    <p className="text-white/20 text-[10px] mt-2">
                        Paste this URL in your CRM's outbound webhook configuration
                    </p>
                </div>
            )}

            {/* Webhook Secret */}
            {guide?.webhook_secret && (
                <div className="glass-card p-6 mb-6 stagger-3">
                    <label className="text-[10px] font-black uppercase tracking-widest text-cyan-400 mb-3 block">
                        🔐 Webhook Secret (HMAC-SHA256)
                    </label>
                    <div className="flex gap-2">
                        <input
                            className="input flex-1 text-sm font-mono bg-white/5"
                            value={secretVisible ? guide.webhook_secret : '••••••••••••••••••••••••••••••••'}
                            readOnly
                        />
                        <button
                            className="px-4 py-2 glass-card text-xs font-bold hover:border-cyan-500/50 transition-all"
                            onClick={() => setSecretVisible(!secretVisible)}
                        >
                            {secretVisible ? 'Hide' : 'Show'}
                        </button>
                    </div>
                    <p className="text-white/20 text-[10px] mt-2">
                        Use this key to sign webhook payloads with HMAC-SHA256 in the X-Webhook-Signature header
                    </p>
                </div>
            )}

            {/* CRM Setup Instructions */}
            {guide?.setup && (
                <div className="glass-card p-6 mb-8 stagger-4">
                    <label className="text-[10px] font-black uppercase tracking-widest text-emerald-400 mb-4 block">
                        📋 {guide.setup.title} — Setup Guide
                    </label>
                    <ol className="space-y-3">
                        {guide.setup.steps.map((step, idx) => (
                            <li key={idx} className="flex gap-3 text-sm text-white/70">
                                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-[10px] font-bold text-primary-purple">
                                    {idx + 1}
                                </span>
                                <span>{step}</span>
                            </li>
                        ))}
                    </ol>
                    {guide.setup.docs_url && (
                        <a
                            href={guide.setup.docs_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-4 inline-flex items-center gap-2 text-xs text-primary-purple hover:text-primary-purple-hover transition-colors"
                        >
                            📖 Official Documentation →
                        </a>
                    )}
                </div>
            )}

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
