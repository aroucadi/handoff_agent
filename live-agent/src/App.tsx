import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import VoiceTenantLayout from './components/VoiceTenantLayout';
import Dashboard from './components/Dashboard';
import BriefingSession from './components/BriefingSession';
import RoleSelection from './components/RoleSelection';

export default function App() {
    return (
        <BrowserRouter>
            <div className="live-agent-app">
                <Routes>
                    {/* Dedicated Synapse Live Agent path */}
                    <Route path="/t/:slug/voice/*" element={<VoiceTenantLayout />} />

                    {/* Direct-access routes (query-param based) */}
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/briefing/:clientId" element={<BriefingSession />} />
                    <Route path="/roles" element={<RoleSelection />} />

                    {/* Discovery / Help */}
                    <Route path="/" element={<LandingPage />} />

                    {/* Fallback */}
                    <Route path="*" element={<div className="text-center p-20 text-white/30">404: Live Session Not Found</div>} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}
