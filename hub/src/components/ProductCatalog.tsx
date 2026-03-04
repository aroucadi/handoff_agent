import React, { useState } from 'react';

interface Product {
    product_id: string;
    name: string;
    description: string;
    knowledge_generated: boolean;
    node_count: number;
}

interface ProductCatalogProps {
    products: Product[];
    onAdd: (name: string, desc: string) => void;
    onRemove: (pid: string) => void;
    onGenerate: () => void;
}

const ProductCatalog: React.FC<ProductCatalogProps> = ({ products, onAdd, onRemove, onGenerate }) => {
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [generating, setGenerating] = useState(false);

    const handleAdd = () => {
        if (!newName) return;
        onAdd(newName, newDesc);
        setNewName('');
        setNewDesc('');
    };

    const handleGenerate = async () => {
        setGenerating(true);
        await onGenerate();
        setGenerating(false);
    };

    return (
        <div className="product-catalog">
            <h2 className="text-2xl font-bold mb-6">Neural Knowledge Ingestion</h2>
            <p className="text-slate-400 mb-8">
                Define the service catalog that will ground the agent's multimodal reasoning.
            </p>

            <div className="glass-card overflow-hidden mb-10">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/10 bg-white/5">
                            <th className="p-6 text-[10px] font-black uppercase tracking-widest text-slate-500">Service Identifier</th>
                            <th className="p-6 text-[10px] font-black uppercase tracking-widest text-slate-500">Grounding Status</th>
                            <th className="p-6 text-[10px] font-black uppercase tracking-widest text-right text-slate-500">Protocols</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map(p => (
                            <tr key={p.product_id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                                <td className="p-6">
                                    <div className="font-bold text-white mb-1">{p.name}</div>
                                    <div className="text-[11px] text-slate-500 leading-relaxed max-w-xs">{p.description.substring(0, 80)}...</div>
                                </td>
                                <td className="p-6">
                                    {p.knowledge_generated ? (
                                        <div className="flex items-center gap-2 text-emerald-400">
                                            <span className="relative flex h-2 w-2">
                                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                            </span>
                                            <span className="text-[10px] font-black uppercase tracking-widest">{p.node_count} Nodes Synced</span>
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2 text-amber-500">
                                            <span className="relative flex h-2 w-2">
                                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                                                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                                            </span>
                                            <span className="text-[10px] font-black uppercase tracking-widest font-italic">Neural Drift Pending</span>
                                        </div>
                                    )}
                                </td>
                                <td className="p-6 text-right">
                                    <button
                                        className="text-[10px] font-black uppercase tracking-widest text-rose-500/60 hover:text-rose-500 transition-colors"
                                        onClick={() => onRemove(p.product_id)}
                                    >
                                        [ Purge ]
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {products.length === 0 && (
                            <tr>
                                <td colSpan={3} className="p-12 text-center text-slate-500 italic text-sm">
                                    No services initialized in catalog.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="glass-card p-8 mb-10 border-dashed border-white/10">
                <h3 className="text-sm font-black uppercase tracking-widest mb-6 text-primary-purple">Append Neural Target</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                    <div className="form-group mb-0">
                        <label className="label">Canonical Name</label>
                        <input className="input" value={newName} onChange={e => setNewName(e.target.value)} placeholder="e.g. Quantum Core" />
                    </div>
                    <div className="form-group mb-0">
                        <label className="label">Functional Specs</label>
                        <input className="input" value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="Key capabilities..." />
                    </div>
                </div>
                <button className="btn btn-secondary w-full justify-center" onClick={handleAdd}>Initialize Service</button>
            </div>

            <button
                className={`
                    btn w-full justify-center h-16 text-sm font-black relative overflow-hidden group
                    ${generating || products.filter(p => !p.knowledge_generated).length === 0
                        ? 'opacity-50 cursor-not-allowed bg-white/5 border border-white/10'
                        : 'bg-primary-purple text-white shadow-2xl shadow-primary-purple/40 hover:scale-[1.01]'
                    }
                `}
                onClick={handleGenerate}
                disabled={generating || products.filter(p => !p.knowledge_generated).length === 0}
            >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-shimmer" />
                {generating ? 'Synchronizing Neural Clusters...' : '✨ Initiate Full Knowledge Ingestion'}
            </button>
        </div>
    );
};

export default ProductCatalog;
