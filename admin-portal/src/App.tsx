import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AdminDashboard from './components/AdminDashboard';
import './index.css';

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <div className="admin-app">
                <header className="header p-12 pb-0">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary-purple rounded-lg flex items-center justify-center font-black italic text-xl">S</div>
                        <span className="font-black tracking-tighter text-2xl">Synapse Admin</span>
                    </div>
                </header>

                <main className="container">
                    <Routes>
                        <Route path="/" element={<AdminDashboard />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
};

export default App;
