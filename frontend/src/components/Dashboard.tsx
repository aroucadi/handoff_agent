/**
 * Handoff — Dashboard Component
 *
 * Shows all client accounts with their graph status.
 * Premium glassmorphism cards with animated status indicators.
 */

import { useEffect, useState, useCallback } from 'react';

interface ClientAccount {
    client_id: string;
    status: string;
    node_count: number;
    generated_at?: string;
}

interface DashboardProps {
    onStartBriefing: (clientId: string) => void;
}

export default function Dashboard({ onStartBriefing }: DashboardProps) {
    const [clients, setClients] = useState<ClientAccount[]>([]);
    const [loading, setLoading] = useState(true);

    const loadClients = useCallback(async () => {
        try {
            const res = await fetch('/api/clients');
            const data = await res.json();
            setClients(data.clients || []);
        } catch {
            console.error('Failed to load clients');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadClients();
        const interval = setInterval(loadClients, 5000);
        return () => clearInterval(interval);
    }, [loadClients]);

    return (
        <div className="dashboard">
            <div className="dashboard__header">
                <div>
                    <h2 className="dashboard__title">Client Accounts</h2>
                    <p className="dashboard__subtitle">Select a client to begin your pre-kickoff briefing</p>
                </div>
                <div className="dashboard__stats">
                    <div className="stat">
                        <span className="stat__value">{clients.length}</span>
                        <span className="stat__label">Accounts</span>
                    </div>
                    <div className="stat">
                        <span className="stat__value">{clients.filter(c => c.status === 'ready').length}</span>
                        <span className="stat__label">Ready</span>
                    </div>
                </div>
            </div>

            <div className="dashboard__grid">
                {loading && (
                    <div className="dashboard__loading">
                        <div className="spinner" />
                        <span>Loading accounts...</span>
                    </div>
                )}

                {!loading && clients.length === 0 && (
                    <div className="dashboard__empty">
                        <div className="dashboard__empty-icon">📋</div>
                        <h3>No client accounts yet</h3>
                        <p>Close a deal in the CRM Simulator to generate a skill graph</p>
                    </div>
                )}

                {clients.map((client, i) => (
                    <div
                        key={client.client_id}
                        className={`account-card account-card--${client.status}`}
                        style={{ animationDelay: `${i * 80}ms` }}
                    >
                        <div className="account-card__header">
                            <div className={`account-card__status status--${client.status}`}>
                                {client.status === 'ready' ? '✅' : client.status === 'generating' ? '⏳' : '⚠️'}
                                <span>{client.status}</span>
                            </div>
                            <span className="account-card__nodes">{client.node_count} nodes</span>
                        </div>

                        <h3 className="account-card__id">{client.client_id}</h3>

                        {client.generated_at && (
                            <p className="account-card__date">
                                Generated: {new Date(client.generated_at).toLocaleDateString()}
                            </p>
                        )}

                        <div className="account-card__coverage">
                            <div className="coverage-bar">
                                <div
                                    className="coverage-bar__fill"
                                    style={{ width: `${Math.min(100, (client.node_count / 10) * 100)}%` }}
                                />
                            </div>
                            <span className="coverage-bar__label">
                                {Math.min(10, client.node_count)}/10 coverage
                            </span>
                        </div>

                        <button
                            className="btn btn--launch"
                            disabled={client.status !== 'ready'}
                            onClick={() => onStartBriefing(client.client_id)}
                        >
                            {client.status === 'ready' ? '🎙️ Start Briefing' : 'Graph not ready'}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
