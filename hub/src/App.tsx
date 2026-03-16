import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import TenantSelector from './components/TenantSelector.tsx';
import TenantWizard from './components/TenantWizard.tsx';
import TenantLayout from './components/TenantLayout.tsx';
import './index.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="hub-app">
        <header className="header animate-slide-down">
          <div className="header__brand">
            <Link to="/" style={{ textDecoration: 'none' }}>
              <span className="header__title text-gradient">Synapse Nexus Hub</span>
            </Link>
            <span className="header__tagline">Control Center</span>
          </div>
        </header>

        <main className="container pt-12">
          <Routes>
            {/* Dedicated Tenant Workspace */}
            <Route path="/t/:slug/*" element={<TenantLayout />} />

            {/* Admin/Discovery Surface */}
            <Route path="/" element={<TenantSelector />} />
            <Route path="/tenants/new" element={<TenantWizard />} />

            {/* Fallback */}
            <Route path="*" element={<TenantSelector />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
