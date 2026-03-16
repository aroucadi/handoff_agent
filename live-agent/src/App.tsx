import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import VoiceTenantLayout from './components/VoiceTenantLayout';

export default function App() {
    return (
        <BrowserRouter>
            <div className="live-agent-app">
                <Routes>
                    {/* Dedicated Synapse Live Agent path */}
                    <Route path="/t/:slug/voice/*" element={<VoiceTenantLayout />} />

                    {/* Discovery / Help */}
                    <Route path="/" element={<LandingPage />} />

                    {/* Fallback */}
                    <Route path="*" element={<div className="text-center p-20 text-white/30">404: Live Session Not Found</div>} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}
