import React from 'react';

interface KnowledgeSource {
    source_id: string;
    type: string;
    uri: string;
    name: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    config: Record<string, any>;
    status: string;
}

interface KnowledgeSourcesConfigProps {
    sources: KnowledgeSource[];
    onChange: (sources: KnowledgeSource[]) => void;
}

const KnowledgeSourcesConfig: React.FC<KnowledgeSourcesConfigProps> = ({ sources, onChange }) => {
    const handleAddSource = (type: string) => {
        const newSource: KnowledgeSource = {
            source_id: Math.random().toString(36).substring(7),
            type,
            uri: '',
            name: '',
            config: {},
            status: 'pending'
        };
        onChange([...sources, newSource]);
    };

    const handleUpdateSource = (id: string, updates: Partial<KnowledgeSource>) => {
        onChange(sources.map(s => s.source_id === id ? { ...s, ...updates } : s));
    };

    const handleRemoveSource = (id: string) => {
        onChange(sources.filter(s => s.source_id !== id));
    };

    const handleConfigChange = (id: string, key: string, value: string | number | boolean) => {
        onChange(sources.map(s => s.source_id === id ? { ...s, config: { ...s.config, [key]: value } } : s));
    };

    return (
        <div className="knowledge-sources-config">
            <h2 className="text-2xl font-bold mb-6">Neural Knowledge Connectors</h2>
            <p className="text-slate-400 mb-8">
                Connect external enterprise repositories to ground the agent's reasoning in your private technical documentation.
            </p>

            <div className="flex gap-4 mb-8">
                <button className="btn btn-secondary text-xs flex-1" onClick={() => handleAddSource('website_crawl')}>+ Website</button>
                <button className="btn btn-secondary text-xs flex-1" onClick={() => handleAddSource('zendesk_api')}>+ Zendesk</button>
                <button className="btn btn-secondary text-xs flex-1" onClick={() => handleAddSource('confluence_api')}>+ Confluence</button>
            </div>

            <div className="space-y-6">
                {sources.map(source => (
                    <div key={source.source_id} className="glass-card p-6 border-white/5 relative group">
                        <button
                            className="absolute top-4 right-4 text-rose-400/50 hover:text-rose-400 text-xs"
                            onClick={() => handleRemoveSource(source.source_id)}
                        >
                            [ DISCONNECT ]
                        </button>

                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-xl">
                                {source.type === 'zendesk_api' ? '🧡' : source.type === 'confluence_api' ? '💙' : '🌐'}
                            </div>
                            <div>
                                <h3 className="text-sm font-bold uppercase tracking-wider text-white">
                                    {source.type.replace('_', ' ')}
                                </h3>
                                <p className="text-[10px] text-white/20 font-mono">{source.source_id}</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="form-group mb-0">
                                <label className="label">Endpoint URI / Subdomain</label>
                                <input
                                    className="input !text-xs"
                                    value={source.uri}
                                    onChange={e => handleUpdateSource(source.source_id, { uri: e.target.value })}
                                    placeholder={source.type === 'website_crawl' ? 'https://docs.example.com' : 'instance-subdomain'}
                                />
                            </div>

                            {source.type === 'zendesk_api' && (
                                <div className="form-group mb-0">
                                    <label className="label">Zendesk API Token</label>
                                    <input
                                        className="input !text-xs"
                                        type="password"
                                        value={source.config.api_token || ''}
                                        onChange={e => handleConfigChange(source.source_id, 'api_token', e.target.value)}
                                        placeholder="••••••••••••••••"
                                    />
                                </div>
                            )}

                            {source.type === 'confluence_api' && (
                                <>
                                    <div className="form-group mb-0">
                                        <label className="label">Space Key</label>
                                        <input
                                            className="input !text-xs"
                                            value={source.config.space_key || ''}
                                            onChange={e => handleConfigChange(source.source_id, 'space_key', e.target.value)}
                                            placeholder="KB"
                                        />
                                    </div>
                                    <div className="form-group mb-0">
                                        <label className="label">Auth Token / API Key</label>
                                        <input
                                            className="input !text-xs"
                                            type="password"
                                            value={source.config.auth_token || ''}
                                            onChange={e => handleConfigChange(source.source_id, 'auth_token', e.target.value)}
                                            placeholder="••••••••••••••••"
                                        />
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                ))}

                {sources.length === 0 && (
                    <div className="text-center py-12 border border-dashed border-white/10 rounded-2xl text-white/20 text-sm">
                        No external knowledge sources connected.
                    </div>
                )}
            </div>
        </div>
    );
};

export default KnowledgeSourcesConfig;
