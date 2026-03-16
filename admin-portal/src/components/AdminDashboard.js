import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
import { Search, Plus, Building2, Trash2, ArrowRight, Loader2, Key } from 'lucide-react';
const AdminDashboard = () => {
    const [tenants, setTenants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [adminKey, setAdminKey] = useState(localStorage.getItem('synapse_admin_key') || '');
    const [showKeyModal, setShowKeyModal] = useState(!localStorage.getItem('synapse_admin_key'));
    const fetchTenants = async () => {
        setLoading(true);
        try {
            const resp = await fetch('/api/tenants', {
                headers: { 'X-Synapse-Admin-Key': adminKey }
            });
            if (resp.status === 401) {
                setShowKeyModal(true);
                throw new Error('Unauthorized');
            }
            const data = await resp.json();
            setTenants(data.tenants || []);
        }
        catch (err) {
            console.error('Fetch failed', err);
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        if (adminKey)
            fetchTenants();
    }, [adminKey]);
    const saveKey = (e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const key = formData.get('key');
        localStorage.setItem('synapse_admin_key', key);
        setAdminKey(key);
        setShowKeyModal(false);
    };
    const deleteTenant = async (id) => {
        if (!confirm('Are you sure you want to decommission this tenant? All data will be lost.'))
            return;
        await fetch(`/api/tenants/${id}`, {
            method: 'DELETE',
            headers: { 'X-Synapse-Admin-Key': adminKey }
        });
        fetchTenants();
    };
    const filtered = tenants.filter(t => t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.slug.toLowerCase().includes(searchTerm.toLowerCase()));
    return (_jsxs("div", { className: "admin-portal p-12 max-w-7xl mx-auto animate-fade-in", children: [showKeyModal && (_jsx("div", { className: "fixed inset-0 bg-black/80 backdrop-blur-xl z-50 flex items-center justify-center p-6", children: _jsxs("div", { className: "glass-card p-10 max-w-md w-full border-primary-purple/30", children: [_jsx(Key, { className: "text-primary-purple mb-6", size: 48 }), _jsx("h2", { className: "text-3xl font-black mb-2", children: "Synapse Admin Access" }), _jsx("p", { className: "text-white/40 mb-8", children: "Enter the master administrative key to oversee the Synapse registry." }), _jsxs("form", { onSubmit: saveKey, className: "space-y-6", children: [_jsx("input", { name: "key", type: "password", placeholder: "Master Admin Key", className: "w-full bg-white/5 border border-white/10 rounded-2xl p-5 focus:border-primary-purple outline-none", required: true }), _jsx("button", { className: "w-full bg-white text-black font-black py-5 rounded-2xl hover:scale-105 transition-all", children: "Authorize Session" })] })] }) })), _jsxs("header", { className: "flex items-center justify-between mb-16", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-5xl font-black text-gradient mb-2", children: "Synapse Admin Portal" }), _jsx("p", { className: "text-white/40 font-medium tracking-wide uppercase text-sm", children: "Registry Oversight & Provisioning" })] }), _jsxs("div", { className: "flex gap-4", children: [_jsxs("div", { className: "relative", children: [_jsx(Search, { className: "absolute left-4 top-1/2 -translate-y-1/2 text-white/20", size: 20 }), _jsx("input", { value: searchTerm, onChange: (e) => setSearchTerm(e.target.value), placeholder: "Search Tenants...", className: "bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-6 focus:border-primary-purple/50 outline-none w-64" })] }), _jsxs("button", { className: "bg-primary-purple px-8 rounded-2xl font-black flex items-center gap-2 hover:bg-purple-500 transition-all", children: [_jsx(Plus, { size: 20 }), " Provision New"] })] })] }), loading ? (_jsxs("div", { className: "flex flex-col items-center justify-center py-32 opacity-20 animate-pulse", children: [_jsx(Loader2, { className: "animate-spin mb-4", size: 64 }), _jsx("span", { className: "font-black tracking-widest uppercase text-xs", children: "Accessing Data Grounding..." })] })) : (_jsxs("div", { className: "grid gap-4", children: [filtered.map(t => (_jsxs("div", { className: "glass-card p-8 flex items-center justify-between group hover:border-white/20 transition-all", children: [_jsxs("div", { className: "flex items-center gap-8", children: [_jsx("div", { className: "w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:bg-primary-purple/10 group-hover:border-primary-purple/20 transition-all text-white/20 group-hover:text-primary-purple", children: _jsx(Building2, { size: 32 }) }), _jsxs("div", { children: [_jsx("h3", { className: "text-2xl font-black mb-1", children: t.name }), _jsxs("div", { className: "flex gap-4 text-xs font-bold uppercase tracking-widest", children: [_jsxs("span", { className: "text-white/30", children: ["ID: ", t.tenant_id] }), _jsxs("span", { className: "text-secondary-cyan", children: ["SLUG: ", t.slug] }), _jsx("span", { className: t.status === 'active' ? 'text-emerald-400' : 'text-amber-400', children: t.status })] })] })] }), _jsxs("div", { className: "flex gap-3", children: [_jsx("button", { onClick: () => window.open(`${import.meta.env.VITE_HUB_URL || ''}/t/${t.slug}/hub`, '_blank'), className: "p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all shadow-sm", title: "Go to Hub", children: _jsx(ArrowRight, { size: 20, className: "text-white/40" }) }), _jsx("button", { onClick: () => deleteTenant(t.tenant_id), className: "p-4 rounded-xl bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 transition-all shadow-sm", title: "Decommission", children: _jsx(Trash2, { size: 20, className: "text-red-500/60" }) })] })] }, t.tenant_id))), filtered.length === 0 && (_jsx("div", { className: "text-center py-32 border-2 border-dashed border-white/5 rounded-[40px]", children: _jsx("p", { className: "text-white/20 font-black uppercase tracking-widest", children: "No matching workspaces found" }) }))] }))] }));
};
export default AdminDashboard;
