import React, { useState } from 'react';

interface TestPanelProps {
    tenantId: string;
    config: {
        name: string;
        brand_name: string;
        crm: { crm_type: string };
        agent: { roles: string[] };
    };
}

const TestPanel: React.FC<TestPanelProps> = ({ tenantId, config }) => {
    const [status, setStatus] = useState<{ step: string; status: string; timestamp?: string }[]>([]);
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
        } catch {
            setStatus([{ step: 'Network error', status: 'error' }]);
        } finally {
            setTesting(false);
        }
    };

    return (
        <div className="test-panel">
            <h2 className="text-2xl font-bold mb-6 text-gradient">System Verification</h2>
            <p className="text-slate-400 mb-10">
                Execute a low-latency pipeline handshake to verify end-to-end grounding integrity.
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="config-summary">
                    <h3 className="text-[10px] font-black uppercase tracking-widest mb-4 text-slate-500">Neural Configuration</h3>
                    <div className="glass-card p-6 space-y-4">
                        <div className="flex justify-between items-center border-b border-white/5 pb-3">
                            <span className="text-xs text-slate-500 font-medium">Active Tenant</span>
                            <span className="text-sm font-bold text-white">{config.name}</span>
                        </div>
                        <div className="flex justify-between items-center border-b border-white/5 pb-3">
                            <span className="text-xs text-slate-500 font-medium">Brand Entity</span>
                            <span className="text-sm font-bold text-primary-purple">{config.brand_name}</span>
                        </div>
                        <div className="flex justify-between items-center border-b border-white/5 pb-3">
                            <span className="text-xs text-slate-500 font-medium">Link Protocol</span>
                            <span className="text-sm font-bold text-cyan-400 uppercase tracking-tighter">{config.crm.crm_type}</span>
                        </div>
                        <div className="flex flex-col gap-2">
                            <span className="text-xs text-slate-500 font-medium">Enabled Perspectives</span>
                            <div className="flex flex-wrap gap-2">
                                {config.agent.roles.map((role: string) => (
                                    <span key={role} className="bg-white/5 px-2 py-1 rounded text-[9px] uppercase font-black tracking-widest border border-white/10">
                                        {role}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="test-runner">
                    <h3 className="text-[10px] font-black uppercase tracking-widest mb-4 text-slate-500">Multimodal Handshake</h3>
                    <button
                        className={`
                            btn w-full mb-6 h-12 justify-center group relative overflow-hidden
                            ${testing ? 'opacity-70 bg-white/5' : 'bg-white/5 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10'}
                        `}
                        onClick={runTest}
                        disabled={testing}
                    >
                        {testing ? (
                            <div className="flex items-center gap-3">
                                <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                                <span className="text-[11px] font-black uppercase tracking-widest">Pipeline Analysis...</span>
                            </div>
                        ) : (
                            <span className="text-[11px] font-black uppercase tracking-widest group-hover:scale-105 transition-transform">
                                🚀 Trigger Neural Webhook
                            </span>
                        )}
                    </button>

                    <div className="test-results space-y-3">
                        {status.map((s, i) => (
                            <div key={i} className={`
                                glass-card p-4 flex items-center gap-4 border-l-2 text-[11px] font-medium transition-all duration-500
                                ${s.status === 'failed' ? 'border-l-rose-500 bg-rose-500/5' :
                                    s.status === 'ok' ? 'border-l-emerald-500 bg-emerald-500/5' :
                                        'border-l-cyan-500 bg-white/5 animate-pulse'}
                                stagger-${(i % 5) + 1}
                            `}>
                                <div className="text-lg">
                                    {s.status === 'ok' ? '✅' : s.status === 'failed' ? '❌' : '⏳'}
                                </div>
                                <div className="flex-1 text-slate-200 tracking-tight">{s.step}</div>
                                {s.timestamp && (
                                    <div className="text-[9px] font-mono text-slate-500 bg-black/20 px-1.5 py-0.5 rounded">
                                        {new Date(s.timestamp).toLocaleTimeString()}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TestPanel;
