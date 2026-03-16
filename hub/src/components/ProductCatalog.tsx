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
            <p className="text-slate-400 mb-10">
                Define the service catalog that will ground the agent's multimodal reasoning and knowledge graph traversal.
            </p>

            <div className="glass-card overflow-hidden mb-12 border-white/10 shadow-2xl">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/10 bg-white/5">
                            <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-500">Service Identifier</th>
                            <th className="p-8 text-[10px] font-black uppercase tracking-widest text-slate-500">Grounding Status</th>
                            <th className="p-8 text-[10px] font-black uppercase tracking-widest text-right text-slate-500">Protocols</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map(p => (
                            <tr key={p.product_id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors group">
                                <td className="p-8">
                                    <div className="font-bold text-white mb-2 text-base group-hover:text-primary-purple transition-colors">{p.name}</div>
                                    <div className="text-[12px] text-slate-500 leading-relaxed max-w-sm font-medium">
                                        {p.description.length > 100 ? `${p.description.substring(0, 100)}...` : p.description}
                                    </div>
                                </td>
                                <td className="p-8">
                                    {p.knowledge_generated ? (
                                        <div className="flex items-center gap-3 text-emerald-400">
                                            <div className="relative flex h-2.5 w-2.5">
                                                <div className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                                            </div>
                                            <span className="text-[10px] font-black uppercase tracking-widest">{p.node_count} Nodes Synced</span>
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-3 text-amber-500/80">
                                            <div className="relative flex h-2.5 w-2.5">
                                                <div className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></div>
                                                <div className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></div>
                                            </div>
                                            <span className="text-[10px] font-black uppercase tracking-widest italic opacity-80">Neural Drift Pending</span>
                                        </div>
                                    )}
                                </td>
                                <td className="p-8 text-right">
                                    <button
                                        className="text-[10px] font-black uppercase tracking-widest text-red-400/40 hover:text-red-400 transition-all hover:scale-105"
                                        onClick={() => onRemove(p.product_id)}
                                    >
                                        [ Purge Sync ]
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {products.length === 0 && (
                            <tr>
                                <td colSpan={3} className="p-20 text-center text-slate-500 italic text-sm font-medium">
                                    <div className="text-4xl mb-4 opacity-10">📂</div>
                                    No services initialized in catalog.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="glass-card p-10 mb-12 border-dashed border-white/10 bg-white/5">
                <h3 className="text-[11px] font-black uppercase tracking-widest mb-8 text-primary-purple flex items-center gap-2">
                    <span className="w-4 h-[1px] bg-primary-purple opacity-30"></span>
                    Append Neural Target
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
                    <div className="form-group mb-0">
                        <label className="label">Canonical Name</label>
                        <input className="input" value={newName} onChange={e => setNewName(e.target.value)} placeholder="e.g. Quantum Core" />
                    </div>
                    <div className="form-group mb-0">
                        <label className="label">Functional Specs</label>
                        <input className="input" value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="Describe core capabilities..." />
                    </div>
                </div>
                <button className="btn btn-secondary w-full justify-center py-4 text-xs tracking-[2px] hover:border-primary-purple/40" onClick={handleAdd}>
                    Initialize Service Handle
                </button>
            </div>

            <button
                className={`
                    btn w-full justify-center h-20 text-[11px] font-black relative overflow-hidden group tracking-[3px]
                    ${generating || products.filter(p => !p.knowledge_generated).length === 0
                        ? 'opacity-30 cursor-not-allowed bg-white/5 border border-white/10 text-slate-500'
                        : 'bg-primary-purple text-white shadow-2xl shadow-primary-purple/40 hover:scale-[1.01] hover:brightness-110'
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
