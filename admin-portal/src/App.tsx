import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AdminDashboard from './components/AdminDashboard';
import './index.css';

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <div className="admin-app">
                <header className="header p-20 pb-0">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-primary-purple rounded-xl flex items-center justify-center font-black italic text-2xl shadow-premium">S</div>
                        <span className="font-black tracking-tighter text-3xl text-gradient">Synapse Admin</span>
                    </div>
                </header>

                <main className="container pt-12 pb-24">
                    <Routes>
                        <Route path="/" element={<AdminDashboard />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
};

export default App;
