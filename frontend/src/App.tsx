/**
 * Handoff — Main App Component (R3)
 *
 * Simple client-side routing between Dashboard and Briefing views.
 */

import { useState, useCallback } from 'react';
import Dashboard from './components/Dashboard';
import BriefingSession from './components/BriefingSession';

type View = 'dashboard' | 'briefing';

interface BriefingState {
    clientId: string;
    sessionId: string;
}

export default function App() {
    const [view, setView] = useState<View>('dashboard');
    const [briefingState, setBriefingState] = useState<BriefingState | null>(null);

    const handleStartBriefing = useCallback(async (clientId: string) => {
        try {
            const res = await fetch('/api/sessions/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ client_id: clientId, csm_name: 'CSM' }),
            });
            const data = await res.json();
            setBriefingState({ clientId, sessionId: data.session_id });
            setView('briefing');
        } catch (err) {
            console.error('Failed to start session:', err);
        }
    }, []);

    const handleEndBriefing = useCallback(() => {
        setBriefingState(null);
        setView('dashboard');
    }, []);

    return (
        <div className="app">
            <header className="header">
                <div className="header__brand" onClick={() => view !== 'dashboard' && handleEndBriefing()}>
                    <h1 className="header__title">Handoff</h1>
                    <span className="header__subtitle">AI Voice Agent</span>
                </div>
                <nav className="header__nav">
                    {view === 'briefing' && (
                        <button className="btn btn--nav" onClick={handleEndBriefing}>
                            ← Dashboard
                        </button>
                    )}
                </nav>
            </header>

            {view === 'dashboard' && (
                <Dashboard onStartBriefing={handleStartBriefing} />
            )}

            {view === 'briefing' && briefingState && (
                <BriefingSession
                    clientId={briefingState.clientId}
                    sessionId={briefingState.sessionId}
                    onEnd={handleEndBriefing}
                />
            )}
        </div>
    );
}
