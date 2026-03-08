import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import TenantPicker from './components/TenantPicker';
import VoiceTenantLayout from './components/VoiceTenantLayout';

export default function App() {
    return (
        <BrowserRouter>
            <div className="app">
                <Routes>
                    {/* Dedicated Atlassian-style Tenant path */}
                    <Route path="/t/:slug/*" element={<VoiceTenantLayout />} />

                    {/* Discovery / Legacy surfaces */}
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/tenants" element={<TenantPicker />} />

                    {/* Support direct legacy routes if needed (Internal) */}
                    <Route path="/roles" element={<VoiceTenantLayout />} />
                </Routes>
            </div>
        </BrowserRouter>
    );
}
