import React from 'react';

interface MappingConfigProps {
    crm: {
        stage_mapping: Record<string, string>;
    };
    product_alias_map: Record<string, string>;
    onCrmChange: (updates: any) => void;
    onAliasChange: (updates: Record<string, string>) => void;
}

const CANONICAL_STAGES = [
    { id: 'prospecting', label: 'Prospecting' },
    { id: 'qualification', label: 'Qualification' },
    { id: 'negotiation', label: 'Negotiation' },
    { id: 'closed_won', label: 'Closed Won' },
    { id: 'implemented', label: 'Implemented' },
    { id: 'closed_lost', label: 'Closed Lost' }
];

const MappingConfig: React.FC<MappingConfigProps> = ({ crm, product_alias_map, onCrmChange, onAliasChange }) => {
    const handleAddStageMapping = () => {
        onCrmChange({
            ...crm,
            stage_mapping: { ...crm.stage_mapping, "": "prospecting" }
        });
    };

    const handleStageMapUpdate = (oldKey: string, newKey: string, newValue: string) => {
        const newMapping = { ...crm.stage_mapping };
        delete newMapping[oldKey];
        newMapping[newKey] = newValue;
        onCrmChange({ ...crm, stage_mapping: newMapping });
    };

    const handleRemoveStageMapping = (key: string) => {
        const newMapping = { ...crm.stage_mapping };
        delete newMapping[key];
        onCrmChange({ ...crm, stage_mapping: newMapping });
    };

    const handleAddAlias = () => {
        onAliasChange({ ...product_alias_map, "": "" });
    };

    const handleAliasUpdate = (oldKey: string, newKey: string, newValue: string) => {
        const newMap = { ...product_alias_map };
        delete newMap[oldKey];
        newMap[newKey] = newValue;
        onAliasChange(newMap);
    };

    const handleRemoveAlias = (key: string) => {
        const newMap = { ...product_alias_map };
        delete newMap[key];
        onAliasChange(newMap);
    };

    return (
        <div className="mapping-config">
            <h2 className="text-2xl font-bold mb-6">Taxonomy & Mapping</h2>
            <p className="text-slate-400 mb-8">
                Align your CRM's specific terminology with Synapse's canonical graph structure.
            </p>

            <section className="mb-12">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h3 className="text-lg font-bold text-white">Stage Normalization</h3>
                        <p className="text-xs text-white/30">Translate CRM Deal Stages to Synapse Nexus Stages</p>
                    </div>
                    <button className="btn btn-secondary text-xs py-2" onClick={handleAddStageMapping}>+ Add Mapping</button>
                </div>

                <div className="space-y-3">
                    {Object.entries(crm.stage_mapping || {}).map(([crmStage, synapseStage]) => (
                        <div key={crmStage} className="flex gap-4 items-center glass-card p-4">
                            <input
                                className="input flex-1 !py-2 !text-xs"
                                placeholder="CRM Stage Name (e.g. Discovery)"
                                value={crmStage}
                                onChange={(e) => handleStageMapUpdate(crmStage, e.target.value, synapseStage)}
                            />
                            <span className="text-white/20">→</span>
                            <select
                                className="input flex-1 !py-2 !text-xs"
                                value={synapseStage}
                                onChange={(e) => handleStageMapUpdate(crmStage, crmStage, e.target.value)}
                            >
                                {CANONICAL_STAGES.map(s => (
                                    <option key={s.id} value={s.id}>{s.label}</option>
                                ))}
                            </select>
                            <button className="text-rose-400 hover:text-rose-300 px-2" onClick={() => handleRemoveStageMapping(crmStage)}>✕</button>
                        </div>
                    ))}
                    {Object.keys(crm.stage_mapping || {}).length === 0 && (
                        <div className="text-center py-6 border border-dashed border-white/10 rounded-xl text-white/20 text-xs">
                            No stage mappings defined. Using identity mapping.
                        </div>
                    )}
                </div>
            </section>

            <section>
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h3 className="text-lg font-bold text-white">Product Aliases</h3>
                        <p className="text-xs text-white/30">Map varied CRM product names to canonical Product IDs</p>
                    </div>
                    <button className="btn btn-secondary text-xs py-2" onClick={handleAddAlias}>+ Add Alias</button>
                </div>

                <div className="space-y-3">
                    {Object.entries(product_alias_map || {}).map(([crmName, productSlug]) => (
                        <div key={crmName} className="flex gap-4 items-center glass-card p-4">
                            <input
                                className="input flex-1 !py-2 !text-xs"
                                placeholder="CRM Product Name"
                                value={crmName}
                                onChange={(e) => handleAliasUpdate(crmName, e.target.value, productSlug)}
                            />
                            <span className="text-white/20">→</span>
                            <input
                                className="input flex-1 !py-2 !text-xs"
                                placeholder="Synapse Product Slug"
                                value={productSlug}
                                onChange={(e) => handleAliasUpdate(crmName, crmName, e.target.value)}
                            />
                            <button className="text-rose-400 hover:text-rose-300 px-2" onClick={() => handleRemoveAlias(crmName)}>✕</button>
                        </div>
                    ))}
                    {Object.keys(product_alias_map || {}).length === 0 && (
                        <div className="text-center py-6 border border-dashed border-white/10 rounded-xl text-white/20 text-xs">
                            No aliases defined. All products must match canonical slugs exactly.
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
};

export default MappingConfig;
