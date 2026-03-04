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
            <h2 style={{ marginBottom: '24px' }}>Configure Product Knowledge</h2>

            <div className="card" style={{ marginBottom: '32px', background: 'rgba(15, 16, 22, 0.4)' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border)' }}>
                            <th style={{ padding: '16px' }}>Product Name</th>
                            <th style={{ padding: '16px' }}>Knowledge Status</th>
                            <th style={{ padding: '16px' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map(p => (
                            <tr key={p.product_id} style={{ borderBottom: '1px solid var(--border)' }}>
                                <td style={{ padding: '16px' }}>
                                    <div style={{ fontWeight: 600 }}>{p.name}</div>
                                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{p.description.substring(0, 60)}...</div>
                                </td>
                                <td style={{ padding: '16px' }}>
                                    {p.knowledge_generated ? (
                                        <span style={{ color: 'var(--green)' }}>✅ {p.node_count} nodes generated</span>
                                    ) : (
                                        <span style={{ color: 'var(--amber)' }}>⏳ Pending AI generation</span>
                                    )}
                                </td>
                                <td style={{ padding: '16px' }}>
                                    <button className="btn btn-secondary" onClick={() => onRemove(p.product_id)} style={{ padding: '4px 8px' }}>
                                        Remove
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="card" style={{ marginBottom: '24px' }}>
                <h3 style={{ marginBottom: '16px' }}>Add New Product</h3>
                <div className="form-group">
                    <label className="label">Product Name</label>
                    <input className="input" value={newName} onChange={e => setNewName(e.target.value)} placeholder="e.g. Acme Cloud Storage" />
                </div>
                <div className="form-group">
                    <label className="label">Product Description</label>
                    <textarea
                        className="textarea"
                        rows={3}
                        value={newDesc}
                        onChange={e => setNewDesc(e.target.value)}
                        placeholder="Capabilities, target personas, implementation details..."
                    />
                </div>
                <button className="btn btn-secondary" onClick={handleAdd}>Add Product</button>
            </div>

            <button
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center', height: '50px', fontSize: '18px' }}
                onClick={handleGenerate}
                disabled={generating || products.filter(p => !p.knowledge_generated).length === 0}
            >
                {generating ? 'AI Generation in Progress...' : '✨ Generate All Product Knowledge'}
            </button>
        </div>
    );
};

export default ProductCatalog;
