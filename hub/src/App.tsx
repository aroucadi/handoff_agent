import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import TenantLayout from './components/TenantLayout.tsx';
import TenantHub from './components/TenantHub.tsx';
import TenantWizard from './components/TenantWizard.tsx';
import './index.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="hub-app">
        <header className="header animate-slide-down">
          <div className="header__brand">
            <Link to="/" style={{ textDecoration: 'none' }}>
              <span className="header__title text-gradient">Synapse Hub</span>
            </Link>
            <span className="header__tagline">Workplace Configuration</span>
          </div>
        </header>

        <main className="container pt-12">
          <Routes>
            {/* Dedicated Tenant Workspace */}
            <Route path="/t/:slug/hub/*" element={<TenantLayout />}>
              <Route index element={<TenantHub />} />
              <Route path="crm" element={<TenantWizard step={2} />} />
              <Route path="mapping" element={<TenantWizard step={3} />} />
              <Route path="products" element={<TenantWizard step={6} />} />
              <Route path="agent" element={<TenantWizard step={7} />} />
              <Route path="knowledge" element={<TenantWizard step={5} />} />
              <Route path="test" element={<TenantWizard step={8} />} />
            </Route>

            {/* Landing / Help */}
            <Route path="/" element={<div className="text-center p-20 text-white/30">Select a tenant workspace URL to begin configuration.</div>} />

            {/* Fallback */}
            <Route path="*" element={<div className="text-center p-20 text-white/30">404: Context Loss Detected</div>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
