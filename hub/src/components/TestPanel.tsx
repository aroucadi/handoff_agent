import React, { useState } from 'react';

interface TestPanelProps {
    tenantId: string;
    config: any;
}

const TestPanel: React.FC<TestPanelProps> = ({ tenantId, config }) => {
    const [status, setStatus] = useState<any[]>([]);
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
        } catch (err) {
            setStatus([{ step: 'Network error', status: 'error' }]);
        } finally {
            setTesting(false);
        }
    };

    return (
        <div className="test-panel">
            <h2 style={{ marginBottom: '24px' }}>Review & Launch</h2>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                <div className="config-summary">
                    <h3 style={{ marginBottom: '16px' }}>Summary</h3>
                    <div className="card" style={{ padding: '16px', fontSize: '14px' }}>
                        <div style={{ marginBottom: '12px' }}>
                            <strong style={{ color: 'var(--text-secondary)' }}>Tenant:</strong> {config.name}
                        </div>
                        <div style={{ marginBottom: '12px' }}>
                            <strong style={{ color: 'var(--text-secondary)' }}>Brand:</strong> {config.brand_name}
                        </div>
                        <div style={{ marginBottom: '12px' }}>
                            <strong style={{ color: 'var(--text-secondary)' }}>CRM:</strong> {config.crm.crm_type.toUpperCase()}
                        </div>
                        <div>
                            <strong style={{ color: 'var(--text-secondary)' }}>Agent Roles:</strong> {config.agent.roles.join(', ')}
                        </div>
                    </div>
                </div>

                <div className="test-runner">
                    <h3 style={{ marginBottom: '16px' }}>Live Pipeline Test</h3>
                    <button
                        className="btn btn-primary"
                        style={{ width: '100%', marginBottom: '20px' }}
                        onClick={runTest}
                        disabled={testing}
                    >
                        {testing ? 'Pipeline testing...' : '🚀 Fire Test Webhook'}
                    </button>

                    <div className="test-results" style={{ fontSize: '14px' }}>
                        {status.map((s, i) => (
                            <div key={i} style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '10px',
                                marginBottom: '10px',
                                color: s.status === 'failed' ? 'var(--red)' :
                                    s.status === 'ok' ? 'var(--green)' : 'var(--text-primary)'
                            }}>
                                <span>{s.status === 'ok' ? '✅' : s.status === 'failed' ? '❌' : '⏳'}</span>
                                <div>{s.step}</div>
                                {s.timestamp && <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginLeft: 'auto' }}>{new Date(s.timestamp).toLocaleTimeString()}</span>}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TestPanel;
