/**
 * Synapse — Main App Component
 *
 * The Living Memory of Your Customer Journey.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import BriefingSession from './components/BriefingSession';

export default function App() {
    return (
        <BrowserRouter>
            <div className="app">
                <header className="header">
                    <div className="header__brand" onClick={() => window.location.href = '/'}>
                        <h1 className="header__title">Synapse</h1>
                        <span className="header__subtitle">Multimodal Live Agent</span>
                    </div>
                </header>

                <Routes>
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/session/:clientId" element={<BriefingSession />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}
