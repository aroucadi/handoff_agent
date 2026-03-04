/**
 * Synapse — Main App Component
 *
 * The Living Memory of Your Customer Journey.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import RoleSelection from './components/RoleSelection';
import Dashboard from './components/Dashboard';
import BriefingSession from './components/BriefingSession';

export default function App() {
    return (
        <BrowserRouter>
            <div className="app">


                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/roles" element={<RoleSelection />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/briefing/:clientId" element={<BriefingSession />} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}
