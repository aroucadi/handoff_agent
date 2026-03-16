import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import dagre from 'dagre';
import { useCallback, useEffect, useState, useRef } from 'react';
import { ReactFlowProvider, useReactFlow, ReactFlow, Background, Controls, useNodesState, useEdgesState, BackgroundVariant, Handle, Position, BaseEdge, getBezierPath, } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { User, Package, Factory, ChevronRight, Activity, Zap, FileText, AlertTriangle, Shield, Target, GitBranch, BookOpen, Link2, Star, Flag, MessageSquare, Handshake, Eye } from 'lucide-react';
/* ── Entity Type Colors + Icons (Ontology Mapping) ────────── */
const ENTITY_COLORS = {
    Organization: { bg: 'rgba(123,57,252,0.2)', border: 'rgba(123,57,252,0.6)', text: '#c4a5ff', icon: User },
    Deal: { bg: 'rgba(0,200,150,0.2)', border: 'rgba(0,200,150,0.6)', text: '#00c896', icon: Zap },
    Contact: { bg: 'rgba(59,130,246,0.2)', border: 'rgba(59,130,246,0.6)', text: '#93bbfd', icon: User },
    Activity: { bg: 'rgba(251,146,60,0.2)', border: 'rgba(251,146,60,0.6)', text: '#fb923c', icon: Activity },
    Contract: { bg: 'rgba(168,85,247,0.2)', border: 'rgba(168,85,247,0.6)', text: '#c084fc', icon: FileText },
    Renewal: { bg: 'rgba(34,211,238,0.2)', border: 'rgba(34,211,238,0.6)', text: '#22d3ee', icon: GitBranch },
    Product: { bg: 'rgba(16,185,129,0.2)', border: 'rgba(16,185,129,0.6)', text: '#6ee7b7', icon: Package },
    Feature: { bg: 'rgba(132,204,22,0.2)', border: 'rgba(132,204,22,0.6)', text: '#bef264', icon: Star },
    UseCase: { bg: 'rgba(14,165,233,0.2)', border: 'rgba(14,165,233,0.6)', text: '#7dd3fc', icon: Target },
    KBArticle: { bg: 'rgba(99,102,241,0.2)', border: 'rgba(99,102,241,0.6)', text: '#a5b4fc', icon: BookOpen },
    Limitation: { bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.5)', text: '#fca5a5', icon: AlertTriangle },
    Integration: { bg: 'rgba(20,184,166,0.2)', border: 'rgba(20,184,166,0.6)', text: '#5eead4', icon: Link2 },
    Risk: { bg: 'rgba(239,68,68,0.2)', border: 'rgba(239,68,68,0.6)', text: '#fca5a5', icon: AlertTriangle },
    DeriskingStrategy: { bg: 'rgba(34,197,94,0.2)', border: 'rgba(34,197,94,0.6)', text: '#86efac', icon: Shield },
    SuccessMetric: { bg: 'rgba(250,204,21,0.2)', border: 'rgba(250,204,21,0.6)', text: '#fde68a', icon: Flag },
    Milestone: { bg: 'rgba(192,132,252,0.2)', border: 'rgba(192,132,252,0.6)', text: '#e9d5ff', icon: Flag },
    Objection: { bg: 'rgba(251,146,60,0.2)', border: 'rgba(251,146,60,0.6)', text: '#fdba74', icon: MessageSquare },
    Commitment: { bg: 'rgba(34,197,94,0.2)', border: 'rgba(34,197,94,0.6)', text: '#86efac', icon: Handshake },
    CompetitorMention: { bg: 'rgba(244,63,94,0.2)', border: 'rgba(244,63,94,0.6)', text: '#fda4af', icon: Eye },
};
const DEFAULT_ENTITY_COLOR = { bg: 'rgba(148,163,184,0.2)', border: 'rgba(148,163,184,0.5)', text: '#cbd5e1', icon: Zap };
function EntityNode({ data }) {
    const colors = ENTITY_COLORS[data.entityType] || DEFAULT_ENTITY_COLOR;
    const Icon = colors.icon;
    return (_jsxs("div", { className: `
            relative px-6 py-4 rounded-[16px] border transition-all duration-500 min-w-[200px] max-w-[260px]
            ${data.isActive ? 'scale-105 z-50 shadow-[0_0_30px_rgba(123,57,252,0.2)] ring-1' : 'hover:brightness-110'}
        `, style: {
            backgroundColor: colors.bg,
            borderColor: data.isActive ? '#7b39fc' : colors.border,
        }, children: [_jsx(Handle, { type: "target", position: Position.Top, className: "opacity-0" }), data.isActive && (_jsx("div", { className: "absolute inset-0 rounded-[16px] bg-primary-purple/10 animate-pulse pointer-events-none" })), _jsxs("div", { className: "flex items-center gap-3 relative z-10", children: [_jsx("div", { className: "w-9 h-9 rounded-[10px] flex items-center justify-center", style: { backgroundColor: colors.border, color: '#fff' }, children: _jsx(Icon, { size: 18, strokeWidth: 1.5 }) }), _jsxs("div", { className: "flex flex-col gap-0.5 min-w-0", children: [_jsx("span", { className: "text-[8px] font-bold uppercase tracking-[0.15em] opacity-70", style: { color: colors.text }, children: data.entityType }), _jsx("span", { className: "text-sm font-semibold text-white/90 truncate", children: data.label })] })] }), _jsx(Handle, { type: "source", position: Position.Bottom, className: "opacity-0" })] }));
}
function SkillNode({ data }) {
    const Icon = data.layer === 'client' ? User : data.layer === 'product' ? Package : Factory;
    return (_jsxs("div", { className: `
            relative px-8 py-5 rounded-[20px] border transition-all duration-700 overflow-hidden min-w-[260px]
            ${data.isActive
            ? 'bg-primary-purple/20 border-primary-purple/60 scale-105 z-50 shadow-[0_0_40px_rgba(123,57,252,0.25)] ring-1 ring-primary-purple/30'
            : data.isVisited
                ? 'bg-white/[0.03] border-white/20 hover:border-white/40'
                : 'bg-white/[0.01] border-white/5 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 hover:border-white/10'}
        `, children: [_jsx(Handle, { type: "target", position: Position.Top, className: "opacity-0" }), data.isActive && (_jsxs(_Fragment, { children: [_jsx("div", { className: "absolute inset-0 bg-primary-purple/10 animate-pulse pointer-events-none" }), _jsx("div", { className: "absolute -inset-4 bg-primary-purple/20 blur-3xl animate-glow-pulse pointer-events-none -z-10" })] })), _jsxs("div", { className: "flex items-center gap-5 relative z-10 font-manrope", children: [_jsx("div", { className: `
                    w-12 h-12 rounded-[14px] flex items-center justify-center transition-all duration-500
                    ${data.isActive
                            ? 'bg-primary-purple text-white shadow-[0_8px_20px_rgba(123,57,252,0.5)]'
                            : 'bg-white/5 text-white/30 group-hover:bg-white/10'}
                `, children: _jsx(Icon, { size: 22, strokeWidth: 1.5 }) }), _jsxs("div", { className: "flex flex-col gap-0.5", children: [_jsxs("span", { className: `
                        text-[9px] font-black uppercase tracking-[0.2em] transition-colors
                        ${data.isActive ? 'text-primary-purple' : 'text-white/20'}
                    `, children: [data.layer, " Nexus"] }), _jsx("span", { className: `
                        text-md font-bold font-inter tracking-tight whitespace-nowrap
                        ${data.isActive ? 'text-white' : 'text-white/60'}
                    `, children: data.label })] })] }), data.isActive && (_jsx("div", { className: "absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-[2px] bg-gradient-to-r from-transparent via-primary-purple to-transparent shadow-[0_0_15px_#7b39fc]" })), _jsx(Handle, { type: "source", position: Position.Bottom, className: "opacity-0" })] }));
}
const nodeTypes = { skillNode: SkillNode, entityNode: EntityNode };
/* ── Premium Custom Edge ───────────────────────────────────── */
function SkillEdge(props) {
    const { sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style = {}, markerEnd, data, } = props;
    const [edgePath] = getBezierPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });
    const isActive = data?.isActive;
    return (_jsxs(_Fragment, { children: [_jsx(BaseEdge, { path: edgePath, markerEnd: markerEnd, style: {
                    ...style,
                    strokeWidth: isActive ? 6 : 2,
                    stroke: isActive ? '#7b39fc' : 'rgba(255, 255, 255, 0.03)',
                    filter: isActive ? 'blur(8px)' : 'none',
                    opacity: isActive ? 0.3 : 1,
                    transition: 'all 0.5s ease',
                } }), _jsx(BaseEdge, { path: edgePath, markerEnd: markerEnd, style: {
                    ...style,
                    strokeWidth: isActive ? 2.5 : 1.5,
                    stroke: isActive ? 'url(#edge-gradient-active)' : 'rgba(255, 255, 255, 0.08)',
                    transition: 'all 0.5s ease',
                } }), isActive && (_jsx("path", { d: edgePath, fill: "none", stroke: "#fff", strokeWidth: 1, strokeDasharray: "4 12", className: "animate-flow-dash opacity-60" }))] }));
}
const edgeTypes = {
    skillEdge: SkillEdge,
};
function formatNodeTitle(nodeId, clientId) {
    const parts = nodeId.split('-');
    // Improved stripping: if the first few parts match the clientId words
    const clientWords = clientId.split('-').filter(Boolean);
    let sliceIndex = 0;
    while (sliceIndex < clientWords.length && parts[sliceIndex]?.toLowerCase() === clientWords[sliceIndex]?.toLowerCase()) {
        sliceIndex++;
    }
    const relevantParts = parts.slice(sliceIndex);
    return relevantParts
        .map(w => w[0].toUpperCase() + w.slice(1))
        .join(' ');
}
/* ── Safe Layout Logic (Internal Logic UNCHANGED) ───────────────── */
function AutoGraphFitter({ nodes, activeNodeId }) {
    const { fitView, setCenter } = useReactFlow();
    useEffect(() => {
        if (nodes.length === 0)
            return;
        const timeout = setTimeout(() => {
            if (activeNodeId) {
                const activeNode = nodes.find(n => n.id === activeNodeId);
                if (activeNode && activeNode.position.x !== 0 && activeNode.position.y !== 0) {
                    setCenter(activeNode.position.x + 130, activeNode.position.y + 50, { zoom: 1, duration: 800 });
                    return;
                }
            }
            fitView({
                padding: { bottom: 280, top: 40, left: 40, right: 40 },
                duration: 800
            });
        }, 50);
        return () => clearTimeout(timeout);
    }, [nodes, activeNodeId, fitView, setCenter]);
    return null;
}
const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));
const nodeWidth = 320; // Slightly wider for premium padding
const nodeHeight = 140;
function getLayoutedElements(nodes, edges, direction = 'TB') {
    dagreGraph.setGraph({ rankdir: direction, nodesep: 160, ranksep: 200 });
    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });
    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });
    dagre.layout(dagreGraph);
    return nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
            ...node,
            position: {
                x: nodeWithPosition.x - nodeWidth / 2,
                y: nodeWithPosition.y - nodeHeight / 2,
            },
        };
    });
}
function createNodes(nodeIds, activeId, visitedIds) {
    return nodeIds.map((id) => {
        const layer = id.includes('product') || id.includes('cpq') || id.includes('revenue')
            ? 'product'
            : id.includes('manufacturing') || id.includes('industry')
                ? 'industry'
                : 'client';
        return {
            id,
            type: 'skillNode',
            position: { x: 0, y: 0 },
            data: {
                label: id.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
                layer,
                isActive: id === activeId,
                isVisited: visitedIds.has(id),
            },
            style: { transition: 'all 0.7s cubic-bezier(0.16, 1, 0.3, 1)' }
        };
    });
}
function buildEdges(nodeIds, toolCalls, metadata) {
    const edges = [];
    const seenEdges = new Set();
    metadata.forEach(node => {
        node.links.forEach(targetId => {
            if (nodeIds.includes(targetId)) {
                seenEdges.add(`${node.node_id}->${targetId}`);
                edges.push({
                    id: `inherent-${node.node_id}-${targetId}`,
                    source: node.node_id,
                    target: targetId,
                    type: 'skillEdge',
                    data: { isActive: false },
                    style: { strokeWidth: 1.5 },
                });
            }
        });
    });
    for (let i = 1; i < toolCalls.length; i++) {
        const prev = toolCalls[i - 1];
        const curr = toolCalls[i];
        if (prev.name === 'follow_link' && curr.name === 'follow_link') {
            const sourceId = prev.args?.node_id;
            const targetId = curr.args?.node_id;
            if (sourceId && targetId) {
                edges.push({
                    id: `traversal-${sourceId}-${targetId}-${i}`,
                    source: sourceId,
                    target: targetId,
                    type: 'skillEdge',
                    data: { isActive: true },
                    zIndex: 10,
                });
            }
        }
    }
    return edges;
}
export default function GraphPanel({ clientId, tenantId, toolCalls, currentNode }) {
    const [breadcrumb, setBreadcrumb] = useState([]);
    const [nodeContent, setNodeContent] = useState(null);
    const [allClientNodes, setAllClientNodes] = useState([]);
    const [graphEntities, setGraphEntities] = useState([]);
    const [graphEdges, setGraphEdges] = useState([]);
    const [graphFormat, setGraphFormat] = useState(null);
    const breadcrumbRef = useRef(null);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    // Detect graph format and fetch appropriate data
    useEffect(() => {
        const fetchGraphData = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || '';
                const lowerId = clientId.toLowerCase();
                const token = localStorage.getItem('synapse_tenant_token');
                const urlSuffix = tenantId ? `?tenant_id=${tenantId}` : '';
                const headers = { 'X-Tenant-Id': tenantId || '' };
                if (token)
                    headers['Authorization'] = `Bearer ${token}`;
                // Check status first to determine format
                const statusRes = await fetch(`${apiUrl}/api/clients/${lowerId}/graph/status${urlSuffix}`, { headers });
                if (statusRes.ok) {
                    const status = await statusRes.json();
                    const format = status.graph_format || 'markdown';
                    setGraphFormat(format);
                    if (format === 'structured') {
                        // Fetch structured entity+edge data
                        const entRes = await fetch(`${apiUrl}/api/clients/${lowerId}/graph/entities${urlSuffix}`, { headers });
                        if (entRes.ok) {
                            const entData = await entRes.json();
                            setGraphEntities(entData.entities || []);
                            setGraphEdges(entData.edges || []);
                        }
                    }
                    else {
                        // Fetch legacy markdown nodes
                        const res = await fetch(`${apiUrl}/api/clients/${lowerId}/graph/nodes${urlSuffix}`, { headers });
                        if (res.ok) {
                            const data = await res.json();
                            if (data.nodes)
                                setAllClientNodes(data.nodes);
                        }
                    }
                }
                else {
                    // Fallback: try legacy
                    setGraphFormat('markdown');
                    const res = await fetch(`${apiUrl}/api/clients/${lowerId}/graph/nodes${urlSuffix}`, { headers });
                    if (res.ok) {
                        const data = await res.json();
                        if (data.nodes)
                            setAllClientNodes(data.nodes);
                    }
                }
            }
            catch (err) {
                console.error('Failed to fetch graph data:', err);
            }
        };
        fetchGraphData();
    }, [clientId]);
    useEffect(() => {
        if (graphFormat === 'structured' && graphEntities.length > 0) {
            // Build from structured entity+edge data
            const entityNodes = graphEntities.map((entity) => ({
                id: entity.entity_id,
                type: 'entityNode',
                position: { x: 0, y: 0 },
                data: {
                    label: entity.properties?.name || entity.entity_id.split('_').pop() || entity.entity_id,
                    entityType: entity.type,
                    properties: entity.properties || {},
                    isActive: currentNode === entity.entity_id,
                },
            }));
            const entityEdgeIds = new Set(graphEntities.map(e => e.entity_id));
            const flowEdges = graphEdges
                .filter(e => entityEdgeIds.has(e.from_id) && entityEdgeIds.has(e.to_id))
                .map((e, idx) => {
                const colors = ENTITY_COLORS[e.type] || DEFAULT_ENTITY_COLOR;
                return {
                    id: `edge-${idx}`,
                    source: e.from_id,
                    target: e.to_id,
                    type: 'skillEdge',
                    label: e.type.replace(/_/g, ' '),
                    style: { stroke: colors.border },
                };
            });
            const layouted = getLayoutedElements(entityNodes, flowEdges);
            console.log(`[GRAPH] Rendered ${layouted.length} entity nodes and ${flowEdges.length} typed edges`);
            setNodes(layouted);
            setEdges(flowEdges);
        }
        else {
            // Legacy markdown wikilink graph
            const nodeIdsSet = new Set(allClientNodes.map(n => n.node_id));
            toolCalls.forEach(tc => {
                if (tc.name === 'follow_link' && tc.args?.node_id) {
                    nodeIdsSet.add(tc.args.node_id);
                }
            });
            const lowerClientId = clientId.toLowerCase();
            if (nodeIdsSet.size === 0)
                nodeIdsSet.add(`${lowerClientId}-index`);
            const nodeIds = Array.from(nodeIdsSet);
            const visitedNodes = new Set(toolCalls
                .filter(tc => tc.name === 'follow_link')
                .map(tc => tc.args?.node_id)
                .filter(Boolean));
            const rawNodes = createNodes(nodeIds, currentNode, visitedNodes);
            const rawEdges = buildEdges(nodeIds, toolCalls, allClientNodes);
            const layouted = getLayoutedElements(rawNodes, rawEdges);
            console.log(`[GRAPH] Rendered ${layouted.length} nodes and ${rawEdges.length} edges`);
            setNodes(layouted);
            setEdges(rawEdges);
        }
    }, [allClientNodes, graphEntities, graphEdges, graphFormat, toolCalls, currentNode, clientId, setNodes, setEdges]);
    useEffect(() => {
        if (currentNode && !breadcrumb.includes(currentNode)) {
            setBreadcrumb(prev => [...prev, currentNode]);
        }
    }, [currentNode, breadcrumb]);
    useEffect(() => {
        if (breadcrumbRef.current) {
            breadcrumbRef.current.scrollTo({
                left: breadcrumbRef.current.scrollWidth,
                behavior: 'smooth'
            });
        }
    }, [breadcrumb]);
    const fetchNodeContent = useCallback(async (nodeId) => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '';
            const lowerId = clientId.toLowerCase();
            const urlSuffix = tenantId ? `?tenant_id=${tenantId}` : '';
            const token = localStorage.getItem('synapse_tenant_token');
            const headers = { 'X-Tenant-Id': tenantId || '' };
            if (token)
                headers['Authorization'] = `Bearer ${token}`;
            const res = await fetch(`${apiUrl}/api/clients/${lowerId}/graph/nodes/${nodeId}${urlSuffix}`, { headers });
            if (res.ok) {
                const data = await res.json();
                setNodeContent(data.content);
            }
        }
        catch {
            console.error('Failed to fetch node content');
        }
    }, [clientId, tenantId]);
    useEffect(() => {
        if (currentNode)
            fetchNodeContent(currentNode);
    }, [currentNode, fetchNodeContent]);
    return (_jsxs("div", { className: "flex flex-col relative bg-black/40 rounded-[32px] overflow-hidden border border-white/10 ring-1 ring-white/5 h-full backdrop-blur-3xl animate-fade-in shadow-2xl", children: [_jsxs("div", { className: "h-16 flex items-center px-10 bg-white/[0.03] border-b border-white/5 shrink-0", children: [_jsxs("div", { className: "flex items-center gap-5 shrink-0", children: [_jsx(Zap, { size: 20, className: "text-primary-purple" }), _jsx("span", { className: "text-[11px] font-black uppercase tracking-[0.3em] text-white/40", children: "KNOWLEDGE NEXUS" })] }), _jsx("div", { className: "mx-10 h-6 w-[1px] bg-white/10 shrink-0" }), _jsxs("div", { ref: breadcrumbRef, className: "flex items-center gap-4 overflow-x-auto no-scrollbar scroll-smooth flex-1 py-4 min-w-0 [mask-image:linear-gradient(to_right,transparent,black_20px,black_calc(100%-40px),transparent)]", children: [breadcrumb.map((nodeId, i) => (_jsxs("div", { className: "flex items-center gap-4 shrink-0 transition-opacity duration-300", children: [i > 0 && _jsx(ChevronRight, { size: 14, className: "text-white/10" }), _jsx("span", { className: `text-sm font-bold font-inter tracking-tight transition-all ${nodeId === currentNode ? 'text-primary-purple scale-110' : 'text-white/30 hover:text-white/50'}`, children: formatNodeTitle(nodeId, clientId) })] }, nodeId))), breadcrumb.length === 0 && (_jsx("span", { className: "text-sm text-white/10 font-medium italic tracking-widest", children: "Listening for grounding events..." }))] })] }), _jsxs("div", { className: "flex-1 relative", children: [_jsx(ReactFlowProvider, { children: _jsxs(ReactFlow, { nodes: nodes, edges: edges, onNodesChange: onNodesChange, onEdgesChange: onEdgesChange, nodeTypes: nodeTypes, edgeTypes: edgeTypes, fitView: true, proOptions: { hideAttribution: true }, minZoom: 0.1, maxZoom: 2, className: "font-inter", children: [_jsx("svg", { className: "absolute w-0 h-0", children: _jsxs("defs", { children: [_jsxs("linearGradient", { id: "edge-gradient-active", x1: "0%", y1: "0%", x2: "100%", y2: "0%", children: [_jsx("stop", { offset: "0%", stopColor: "#7b39fc" }), _jsx("stop", { offset: "50%", stopColor: "#ff4081" }), _jsx("stop", { offset: "100%", stopColor: "#00e5ff" })] }), _jsxs("filter", { id: "edge-glow", children: [_jsx("feGaussianBlur", { stdDeviation: "3", result: "blur" }), _jsx("feComposite", { in: "SourceGraphic", in2: "blur", operator: "over" })] })] }) }), _jsx(Background, { variant: BackgroundVariant.Dots, color: "rgba(123,57,252,0.1)", gap: 40, size: 1 }), _jsx(Controls, { className: "!bg-[#0f1016]/90 !border-white/10 !fill-white/60 hover:!fill-white !rounded-xl !overflow-hidden !m-8 !shadow-2xl", showInteractive: false }), _jsx(AutoGraphFitter, { nodes: nodes, activeNodeId: currentNode })] }) }), _jsx("div", { className: "absolute top-8 right-8 flex flex-col gap-2 p-4 bg-black/60 rounded-2xl border border-white/10 backdrop-blur-xl z-20 shadow-2xl", children: _jsxs("div", { className: "flex items-center gap-3 text-[10px] uppercase tracking-[0.2em] font-black text-white/40", children: [_jsx(Activity, { size: 12, className: "text-emerald-400 animate-pulse" }), " Live Grounding"] }) })] }), currentNode && nodeContent && (_jsxs("div", { className: "absolute bottom-6 left-6 right-6 max-h-[30%] flex flex-col glass-card bg-[#0f1016]/95 border-white/30 p-6 z-30 animate-fade-in shadow-[0_30px_60px_rgba(0,0,0,0.8)] rounded-[20px]", children: [_jsxs("div", { className: "flex items-center justify-between mb-6 shrink-0", children: [_jsxs("div", { className: "flex items-center gap-4", children: [_jsx("div", { className: "w-12 h-12 flex items-center justify-center bg-primary-purple/10 rounded-xl text-primary-purple border border-primary-purple/20", children: _jsx(FileText, { size: 20, strokeWidth: 1.5 }) }), _jsxs("div", { className: "flex flex-col gap-0.5", children: [_jsx("span", { className: "text-[10px] uppercase tracking-[0.3em] text-white/20 font-black", children: "Node Context Resolved" }), _jsx("h4", { className: "text-lg font-bold text-white tracking-tight leading-none capitalize", children: currentNode.replace(/-/g, ' ') })] })] }), _jsxs("div", { className: "px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center gap-2", children: [_jsx("div", { className: "w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" }), _jsx("span", { className: "text-[10px] font-black uppercase tracking-widest text-emerald-400", children: "Grounded" })] })] }), _jsx("div", { className: "overflow-y-auto pr-4 custom-scrollbar", children: _jsx("p", { className: "text-md leading-relaxed text-white/70 font-medium", children: nodeContent }) })] }))] }));
}
