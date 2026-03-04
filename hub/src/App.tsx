import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import TenantList from './components/TenantList.tsx';
import TenantWizard from './components/TenantWizard.tsx';
import './index.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="hub-app">
        <header className="header">
          <div className="header__brand">
            <Link to="/" style={{ textDecoration: 'none' }}>
              <span className="header__title">Synapse Hub</span>
            </Link>
            <span className="header__tagline">Tenant Configuration</span>
          </div>
          <nav className="header__nav">
            <Link to="/tenants/new" className="btn btn-primary">+ New Tenant</Link>
          </nav>
        </header>

        <main className="container">
          <Routes>
            <Route path="/" element={<TenantList />} />
            <Route path="/tenants/new" element={<TenantWizard />} />
            <Route path="/tenants/:id" element={<TenantWizard />} /> {/* Reusing wizard for editing for now */}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
