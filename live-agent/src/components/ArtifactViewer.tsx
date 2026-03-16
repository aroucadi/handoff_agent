/**
 * Synapse — Artifact Viewer Component
 * 
 * Modal overlay for viewing, downloading, and browsing generated artifacts.
 * Supports Markdown rendering, PDF download, clipboard copy, and version history.
 */

import { useState, useEffect, useCallback } from 'react';
import { X, Download, Copy, Check, ChevronDown, FileText, Shield, Target, BookOpen, RefreshCw, Clock, Sparkles } from 'lucide-react';

// Type icon mapping
const TYPE_ICONS: Record<string, React.ReactNode> = {
    briefing: <BookOpen size={16} />,
    action_plan: <Target size={16} />,
    risk_report: <Shield size={16} />,
    recommendations: <Sparkles size={16} />,
    handoff: <RefreshCw size={16} />,
    transcript: <FileText size={16} />,
};

const TYPE_COLORS: Record<string, string> = {
    briefing: '#7B39FC',
    action_plan: '#10B981',
    risk_report: '#F59E0B',
    recommendations: '#6366F1',
    handoff: '#EC4899',
    transcript: '#06B6D4',
};

interface ArtifactOutput {
    id: string;
    type: string;
    subtype?: string;
    title: string;
    content?: string;
    generated_at: string;
    version: number;
    is_latest: boolean;
    metadata?: Record<string, unknown>;
}

interface ArtifactViewerProps {
    clientId: string;
    tenantId: string | null;
    isOpen: boolean;
    onClose: () => void;
    selectedOutputId?: string | null;
}

export default function ArtifactViewer({ clientId, tenantId, isOpen, onClose, selectedOutputId }: ArtifactViewerProps) {
    const [outputs, setOutputs] = useState<ArtifactOutput[]>([]);
    const [selectedOutput, setSelectedOutput] = useState<ArtifactOutput | null>(null);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    const apiUrl = import.meta.env.VITE_API_URL || '';

    const fetchOutputs = useCallback(async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('synapse_tenant_token');
            const headers: Record<string, string> = { 'X-Tenant-Id': tenantId || '' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const url = tenantId
                ? `${apiUrl}/api/clients/${clientId}/outputs?tenant_id=${tenantId}`
                : `${apiUrl}/api/clients/${clientId}/outputs`;
            const res = await fetch(url, { headers });
            const data = await res.json();
            setOutputs(data.outputs || []);
        } catch (err) {
            console.error('Failed to fetch outputs:', err);
        } finally {
            setLoading(false);
        }
    }, [clientId, tenantId, apiUrl]);

    const fetchOutputDetail = useCallback(async (outputId: string) => {
        try {
            const token = localStorage.getItem('synapse_tenant_token');
            const headers: Record<string, string> = { 'X-Tenant-Id': tenantId || '' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const url = tenantId
                ? `${apiUrl}/api/clients/${clientId}/outputs/${outputId}?tenant_id=${tenantId}`
                : `${apiUrl}/api/clients/${clientId}/outputs/${outputId}`;
            const res = await fetch(url, { headers });
            const data = await res.json();
            setSelectedOutput(data);
        } catch (err) {
            console.error('Failed to fetch output detail:', err);
        }
    }, [clientId, tenantId, apiUrl]);

    useEffect(() => {
        if (isOpen) {
            fetchOutputs();
        }
    }, [isOpen, fetchOutputs]);

    useEffect(() => {
        if (selectedOutputId && isOpen) {
            fetchOutputDetail(selectedOutputId);
        }
    }, [selectedOutputId, isOpen, fetchOutputDetail]);

    const handleCopy = () => {
        if (selectedOutput?.content) {
            navigator.clipboard.writeText(selectedOutput.content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const handleDownloadMd = () => {
        if (!selectedOutput?.content) return;
        const blob = new Blob([selectedOutput.content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedOutput.title.replace(/\s+/g, '_').toLowerCase()}.md`;
        a.click();
        URL.revokeObjectURL(url);
    };

    // Group outputs by type, showing latest first
    const latestByType = outputs.filter(o => o.is_latest !== false);
    const olderVersions = outputs.filter(o => o.is_latest === false);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

            {/* Panel */}
            <div className="relative w-[90vw] max-w-5xl h-[80vh] bg-[#0a0a0f] border border-white/10 rounded-2xl shadow-2xl flex overflow-hidden">
                {/* Sidebar — Artifact List */}
                <div className="w-72 border-r border-white/5 flex flex-col">
                    <div className="p-4 border-b border-white/5">
                        <h2 className="text-sm font-black uppercase tracking-[0.2em] text-white/60">Generated Artifacts</h2>
                        <p className="text-[10px] text-white/30 mt-1">{latestByType.length} artifacts · {outputs.length} total versions</p>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                        {loading ? (
                            <div className="flex items-center justify-center py-8">
                                <div className="w-6 h-6 border-2 border-primary-purple/30 border-t-primary-purple rounded-full animate-spin" />
                            </div>
                        ) : latestByType.length === 0 ? (
                            <div className="text-center py-8 text-white/20 text-xs">
                                No artifacts generated yet.
                                <br />Use smart actions during a briefing to create them.
                            </div>
                        ) : (
                            latestByType.map(output => {
                                const color = TYPE_COLORS[output.type] || '#7B39FC';
                                const isSelected = selectedOutput?.id === output.id;
                                const versionCount = outputs.filter(o => o.type === output.type && o.subtype === output.subtype).length;
                                return (
                                    <button
                                        key={output.id}
                                        className={`w-full text-left p-3 rounded-xl transition-all duration-200 border ${isSelected
                                            ? 'bg-white/10 border-white/20'
                                            : 'bg-white/[0.02] border-transparent hover:bg-white/5 hover:border-white/10'
                                            }`}
                                        onClick={() => fetchOutputDetail(output.id)}
                                    >
                                        <div className="flex items-center gap-2 mb-1">
                                            <span style={{ color }}>{TYPE_ICONS[output.type] || <FileText size={16} />}</span>
                                            <span className="text-xs font-bold text-white truncate flex-1">{output.title}</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-[10px] text-white/30">
                                            <Clock size={10} />
                                            <span>{new Date(output.generated_at).toLocaleDateString()}</span>
                                            {versionCount > 1 && (
                                                <span className="ml-auto px-1.5 py-0.5 rounded bg-white/5 text-white/40 font-bold">
                                                    v{output.version} · {versionCount} ver
                                                </span>
                                            )}
                                        </div>
                                    </button>
                                );
                            })
                        )}

                        {/* Older versions section */}
                        {olderVersions.length > 0 && (
                            <details className="mt-4">
                                <summary className="text-[10px] uppercase tracking-widest text-white/20 font-bold cursor-pointer hover:text-white/40 px-2 py-2 flex items-center gap-1">
                                    <ChevronDown size={10} />
                                    Previous Versions ({olderVersions.length})
                                </summary>
                                <div className="space-y-1 mt-1">
                                    {olderVersions.map(output => (
                                        <button
                                            key={output.id}
                                            className="w-full text-left p-2 rounded-lg text-white/30 text-[11px] hover:bg-white/5 transition-all"
                                            onClick={() => fetchOutputDetail(output.id)}
                                        >
                                            {output.title} · v{output.version}
                                        </button>
                                    ))}
                                </div>
                            </details>
                        )}
                    </div>
                </div>

                {/* Main content — Artifact Preview */}
                <div className="flex-1 flex flex-col">
                    {/* Header */}
                    <div className="p-4 border-b border-white/5 flex items-center justify-between">
                        {selectedOutput ? (
                            <div className="flex items-center gap-3">
                                <span style={{ color: TYPE_COLORS[selectedOutput.type] || '#7B39FC' }}>
                                    {TYPE_ICONS[selectedOutput.type] || <FileText size={20} />}
                                </span>
                                <div>
                                    <h3 className="text-sm font-bold text-white">{selectedOutput.title}</h3>
                                    <p className="text-[10px] text-white/30">
                                        v{selectedOutput.version} · Generated {new Date(selectedOutput.generated_at).toLocaleString()}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <span className="text-white/30 text-sm">Select an artifact to preview</span>
                        )}
                        <div className="flex items-center gap-2">
                            {selectedOutput && (
                                <>
                                    <button
                                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white/50 text-[11px] font-bold hover:bg-white/10 hover:text-white transition-all"
                                        onClick={handleCopy}
                                    >
                                        {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                                        {copied ? 'Copied!' : 'Copy'}
                                    </button>
                                    <button
                                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary-purple/20 border border-primary-purple/30 text-primary-purple text-[11px] font-bold hover:bg-primary-purple/30 transition-all"
                                        onClick={handleDownloadMd}
                                    >
                                        <Download size={12} />
                                        Download .md
                                    </button>
                                </>
                            )}
                            <button
                                className="p-2 rounded-lg hover:bg-white/10 transition-all text-white/40 hover:text-white"
                                onClick={onClose}
                            >
                                <X size={18} />
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 overflow-y-auto p-6">
                        {selectedOutput?.content ? (
                            <div className="prose prose-invert prose-sm max-w-none
                                prose-headings:font-inter prose-headings:tracking-tight
                                prose-h1:text-xl prose-h1:mb-4 prose-h1:text-white
                                prose-h2:text-lg prose-h2:text-white/90 prose-h2:mt-6
                                prose-h3:text-base prose-h3:text-white/80
                                prose-p:text-white/70 prose-p:leading-relaxed
                                prose-li:text-white/70
                                prose-strong:text-white
                                prose-code:text-primary-purple prose-code:bg-white/5 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
                                whitespace-pre-wrap font-inter text-sm">
                                {selectedOutput.content}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-white/20">
                                <FileText size={48} strokeWidth={1} />
                                <p className="mt-4 text-sm">Select an artifact from the sidebar to preview</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
