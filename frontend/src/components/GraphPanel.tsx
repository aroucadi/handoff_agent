import dagre from 'dagre';
import { useCallback, useEffect, useState, useRef } from 'react';
import {
    ReactFlowProvider,
    useReactFlow,
    ReactFlow,
    type Node,
    type Edge,
    Background,
    Controls,
    useNodesState,
    useEdgesState,
    BackgroundVariant,
    type NodeTypes,
    Handle,
    Position,
    BaseEdge,
    getBezierPath,
    type EdgeProps,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { User, Package, Factory, ChevronRight, Activity, Zap, FileText } from 'lucide-react';
import type { ToolCallEntry } from '../useVoiceSession';

interface ServerNodeMetadata {
    node_id: string;
    title: string;
    layer: string;
    links: string[];
    description: string;
}

/* ── High-Fidelity Custom Node ─────────────────────────────── */

interface SkillNodeData {
    label: string;
    layer: string;
    isActive: boolean;
    isVisited: boolean;
    [key: string]: unknown;
}

function SkillNode({ data }: { data: SkillNodeData }) {
    const Icon = data.layer === 'client' ? User : data.layer === 'product' ? Package : Factory;

    return (
        <div className={`
            relative px-8 py-5 rounded-[20px] border transition-all duration-700 overflow-hidden min-w-[260px]
            ${data.isActive
                ? 'bg-primary-purple/20 border-primary-purple/60 scale-105 z-50 shadow-[0_0_40px_rgba(123,57,252,0.25)] ring-1 ring-primary-purple/30'
                : data.isVisited
                    ? 'bg-white/[0.03] border-white/20 hover:border-white/40'
                    : 'bg-white/[0.01] border-white/5 grayscale opacity-40 hover:grayscale-0 hover:opacity-100 hover:border-white/10'
            }
        `}>
            {/* Connection Handles - Hidden but required for XYFlow logic */}
            <Handle type="target" position={Position.Top} className="opacity-0" />

            {/* Pulsing Active State Layer */}
            {data.isActive && (
                <>
                    <div className="absolute inset-0 bg-primary-purple/10 animate-pulse pointer-events-none" />
                    <div className="absolute -inset-4 bg-primary-purple/20 blur-3xl animate-glow-pulse pointer-events-none -z-10" />
                </>
            )}

            <div className="flex items-center gap-5 relative z-10 font-manrope">
                <div className={`
                    w-12 h-12 rounded-[14px] flex items-center justify-center transition-all duration-500
                    ${data.isActive
                        ? 'bg-primary-purple text-white shadow-[0_8px_20px_rgba(123,57,252,0.5)]'
                        : 'bg-white/5 text-white/30 group-hover:bg-white/10'
                    }
                `}>
                    <Icon size={22} strokeWidth={1.5} />
                </div>
                <div className="flex flex-col gap-0.5">
                    <span className={`
                        text-[9px] font-black uppercase tracking-[0.2em] transition-colors
                        ${data.isActive ? 'text-primary-purple' : 'text-white/20'}
                    `}>
                        {data.layer} Nexus
                    </span>
                    <span className={`
                        text-md font-bold font-inter tracking-tight whitespace-nowrap
                        ${data.isActive ? 'text-white' : 'text-white/60'}
                    `}>
                        {data.label}
                    </span>
                </div>
            </div>

            {/* Glowing Active Indicator Strip */}
            {data.isActive && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[60%] h-[2px] bg-gradient-to-r from-transparent via-primary-purple to-transparent shadow-[0_0_15px_#7b39fc]" />
            )}

            <Handle type="source" position={Position.Bottom} className="opacity-0" />
        </div>
    );
}

const nodeTypes: NodeTypes = { skillNode: SkillNode };

/* ── Premium Custom Edge ───────────────────────────────────── */

function SkillEdge(props: EdgeProps) {
    const {
        sourceX,
        sourceY,
        targetX,
        targetY,
        sourcePosition,
        targetPosition,
        style = {},
        markerEnd,
        data,
    } = props;

    const [edgePath] = getBezierPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });

    const isActive = data?.isActive;

    return (
        <>
            {/* Ambient Outer Glow Layer */}
            <BaseEdge
                path={edgePath}
                markerEnd={markerEnd}
                style={{
                    ...style,
                    strokeWidth: isActive ? 6 : 2,
                    stroke: isActive ? '#7b39fc' : 'rgba(255, 255, 255, 0.03)',
                    filter: isActive ? 'blur(8px)' : 'none',
                    opacity: isActive ? 0.3 : 1,
                    transition: 'all 0.5s ease',
                }}
            />
            {/* Main Gradient Stroke */}
            <BaseEdge
                path={edgePath}
                markerEnd={markerEnd}
                style={{
                    ...style,
                    strokeWidth: isActive ? 2.5 : 1.5,
                    stroke: isActive ? 'url(#edge-gradient-active)' : 'rgba(255, 255, 255, 0.08)',
                    transition: 'all 0.5s ease',
                }}
            />
            {/* Pulsing Core Layer for Traversal */}
            {isActive && (
                <path
                    d={edgePath}
                    fill="none"
                    stroke="#fff"
                    strokeWidth={1}
                    strokeDasharray="4 12"
                    className="animate-flow-dash opacity-60"
                />
            )}
        </>
    );
}

const edgeTypes = {
    skillEdge: SkillEdge,
};

function formatNodeTitle(nodeId: string, clientId: string) {
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

function AutoGraphFitter({ nodes, activeNodeId }: { nodes: Node[], activeNodeId: string | null }) {
    const { fitView, setCenter } = useReactFlow();

    useEffect(() => {
        if (nodes.length === 0) return;

        const timeout = setTimeout(() => {
            if (activeNodeId) {
                const activeNode = nodes.find(n => n.id === activeNodeId);
                if (activeNode && activeNode.position.x !== 0 && activeNode.position.y !== 0) {
                    setCenter(
                        activeNode.position.x + 130,
                        activeNode.position.y + 50,
                        { zoom: 1, duration: 800 }
                    );
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

function getLayoutedElements(nodes: Node[], edges: Edge[], direction = 'TB') {
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

function createNodes(nodeIds: string[], activeId: string | null, visitedIds: Set<string>): Node[] {
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
                label: id.replace(/-/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
                layer,
                isActive: id === activeId,
                isVisited: visitedIds.has(id),
            },
            style: { transition: 'all 0.7s cubic-bezier(0.16, 1, 0.3, 1)' }
        } as Node;
    });
}

function buildEdges(
    nodeIds: string[],
    toolCalls: ToolCallEntry[],
    metadata: ServerNodeMetadata[]
): Edge[] {
    const edges: Edge[] = [];
    const seenEdges = new Set<string>();

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
            const sourceId = prev.args?.node_id as string;
            const targetId = curr.args?.node_id as string;
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

/* ── Main Panel ─────────────────────────────────────────── */

interface GraphPanelProps {
    clientId: string;
    toolCalls: ToolCallEntry[];
    currentNode: string | null;
}

export default function GraphPanel({ clientId, toolCalls, currentNode }: GraphPanelProps) {
    const [breadcrumb, setBreadcrumb] = useState<string[]>([]);
    const [nodeContent, setNodeContent] = useState<string | null>(null);
    const [allClientNodes, setAllClientNodes] = useState<ServerNodeMetadata[]>([]);
    const breadcrumbRef = useRef<HTMLDivElement>(null);

    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    useEffect(() => {
        const fetchAllNodes = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || '';
                const lowerId = clientId.toLowerCase();
                const res = await fetch(`${apiUrl}/api/clients/${lowerId}/graph/nodes`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.nodes) setAllClientNodes(data.nodes);
                }
            } catch (err) {
                console.error('Failed to fetch client nodes:', err);
            }
        };
        fetchAllNodes();
    }, [clientId]);

    useEffect(() => {
        const nodeIdsSet = new Set<string>(allClientNodes.map(n => n.node_id));
        toolCalls.forEach(tc => {
            if (tc.name === 'follow_link' && tc.args?.node_id) {
                nodeIdsSet.add(tc.args.node_id as string);
            }
        });
        const lowerClientId = clientId.toLowerCase();
        if (nodeIdsSet.size === 0) nodeIdsSet.add(`${lowerClientId}-index`);

        const nodeIds = Array.from(nodeIdsSet);
        const visitedNodes = new Set(toolCalls
            .filter(tc => tc.name === 'follow_link')
            .map(tc => tc.args?.node_id as string)
            .filter(Boolean));

        const rawNodes = createNodes(nodeIds, currentNode, visitedNodes);
        const rawEdges = buildEdges(nodeIds, toolCalls, allClientNodes);

        const layouted = getLayoutedElements(rawNodes, rawEdges);
        console.log(`[GRAPH] Rendered ${layouted.length} nodes and ${rawEdges.length} edges`);
        setNodes(layouted);
        setEdges(rawEdges);
    }, [allClientNodes, toolCalls, currentNode, clientId, setNodes, setEdges]);

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

    const fetchNodeContent = useCallback(async (nodeId: string) => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '';
            const lowerId = clientId.toLowerCase();
            const res = await fetch(`${apiUrl}/api/clients/${lowerId}/graph/nodes/${nodeId}`);
            if (res.ok) {
                const data = await res.json();
                setNodeContent(data.content);
            }
        } catch {
            console.error('Failed to fetch node content');
        }
    }, [clientId]);

    useEffect(() => {
        if (currentNode) fetchNodeContent(currentNode);
    }, [currentNode, fetchNodeContent]);

    return (
        <div className="flex flex-col relative bg-black/40 rounded-[32px] overflow-hidden border border-white/10 ring-1 ring-white/5 h-full backdrop-blur-3xl animate-fade-in shadow-2xl">
            {/* Nav Header */}
            <div className="h-16 flex items-center px-10 bg-white/[0.03] border-b border-white/5 shrink-0">
                <div className="flex items-center gap-5 shrink-0">
                    <Zap size={20} className="text-primary-purple" />
                    <span className="text-[11px] font-black uppercase tracking-[0.3em] text-white/40">KNOWLEDGE NEXUS</span>
                </div>
                <div className="mx-10 h-6 w-[1px] bg-white/10 shrink-0" />
                <div
                    ref={breadcrumbRef}
                    className="flex items-center gap-4 overflow-x-auto no-scrollbar scroll-smooth flex-1 py-4 min-w-0 [mask-image:linear-gradient(to_right,transparent,black_20px,black_calc(100%-40px),transparent)]"
                >
                    {breadcrumb.map((nodeId, i) => (
                        <div key={nodeId} className="flex items-center gap-4 shrink-0 transition-opacity duration-300">
                            {i > 0 && <ChevronRight size={14} className="text-white/10" />}
                            <span className={`text-sm font-bold font-inter tracking-tight transition-all ${nodeId === currentNode ? 'text-primary-purple scale-110' : 'text-white/30 hover:text-white/50'}`}>
                                {formatNodeTitle(nodeId, clientId)}
                            </span>
                        </div>
                    ))}
                    {breadcrumb.length === 0 && (
                        <span className="text-sm text-white/10 font-medium italic tracking-widest">Listening for grounding events...</span>
                    )}
                </div>
            </div>

            {/* React Flow Area */}
            <div className="flex-1 relative">
                <ReactFlowProvider>
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        nodeTypes={nodeTypes}
                        edgeTypes={edgeTypes}
                        fitView
                        proOptions={{ hideAttribution: true }}
                        minZoom={0.1}
                        maxZoom={2}
                        className="font-inter"
                    >
                        {/* Custom SVG Definitions for Gradients & Filters */}
                        <svg className="absolute w-0 h-0">
                            <defs>
                                <linearGradient id="edge-gradient-active" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor="#7b39fc" />
                                    <stop offset="50%" stopColor="#ff4081" />
                                    <stop offset="100%" stopColor="#00e5ff" />
                                </linearGradient>
                                <filter id="edge-glow">
                                    <feGaussianBlur stdDeviation="3" result="blur" />
                                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                                </filter>
                            </defs>
                        </svg>

                        <Background variant={BackgroundVariant.Dots} color="rgba(123,57,252,0.1)" gap={40} size={1} />
                        <Controls className="!bg-[#0f1016]/90 !border-white/10 !fill-white/60 hover:!fill-white !rounded-xl !overflow-hidden !m-8 !shadow-2xl" showInteractive={false} />
                        <AutoGraphFitter nodes={nodes} activeNodeId={currentNode} />
                    </ReactFlow>
                </ReactFlowProvider>

                {/* Traversal Badge */}
                <div className="absolute top-8 right-8 flex flex-col gap-2 p-4 bg-black/60 rounded-2xl border border-white/10 backdrop-blur-xl z-20 shadow-2xl">
                    <div className="flex items-center gap-3 text-[10px] uppercase tracking-[0.2em] font-black text-white/40">
                        <Activity size={12} className="text-emerald-400 animate-pulse" /> Live Grounding
                    </div>
                </div>
            </div>

            {/* Knowledge Reveal Overlay */}
            {currentNode && nodeContent && (
                <div className="absolute bottom-6 left-6 right-6 max-h-[30%] flex flex-col glass-card bg-[#0f1016]/95 border-white/30 p-6 z-30 animate-fade-in shadow-[0_30px_60px_rgba(0,0,0,0.8)] rounded-[20px]">
                    <div className="flex items-center justify-between mb-6 shrink-0">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 flex items-center justify-center bg-primary-purple/10 rounded-xl text-primary-purple border border-primary-purple/20">
                                <FileText size={20} strokeWidth={1.5} />
                            </div>
                            <div className="flex flex-col gap-0.5">
                                <span className="text-[10px] uppercase tracking-[0.3em] text-white/20 font-black">Node Context Resolved</span>
                                <h4 className="text-lg font-bold text-white tracking-tight leading-none capitalize">{currentNode.replace(/-/g, ' ')}</h4>
                            </div>
                        </div>
                        <div className="px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Grounded</span>
                        </div>
                    </div>
                    <div className="overflow-y-auto pr-4 custom-scrollbar">
                        <p className="text-md leading-relaxed text-white/70 font-medium">
                            {nodeContent}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
