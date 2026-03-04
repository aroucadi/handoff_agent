/**
 * Synapse — Graph Panel Component
 *
 * Right side of the split-screen briefing view.
 * Shows a React Flow graph topology with animated node traversal,
 * breadcrumb navigation, and a node content card.
 */

import dagre from 'dagre';
import { useCallback, useEffect, useState } from 'react';
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
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { User, Package, Factory, Share2, FileText, ChevronRight } from 'lucide-react';
import type { ToolCallEntry } from '../useVoiceSession';

interface ServerNodeMetadata {
    node_id: string;
    title: string;
    layer: string;
    links: string[];
    description: string;
}

/* ── Custom Node Component ─────────────────────────────── */

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
        <div className={`graph-node graph-node--${data.layer} ${data.isActive ? 'graph-node--active' : ''} ${data.isVisited ? 'graph-node--visited' : ''}`}>
            <Handle type="target" position={Position.Top} className="graph-node__handle" />
            <div className="graph-node__icon-wrapper">
                <Icon size={18} strokeWidth={2.5} />
            </div>
            <div className="graph-node__label">{data.label}</div>
            {data.isActive && <div className="graph-node__pulse" />}
            <Handle type="source" position={Position.Bottom} className="graph-node__handle" />
        </div>
    );
}

const nodeTypes: NodeTypes = { skillNode: SkillNode };

/* ── Auto Layout Fitter ────────────────────────────────── */

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
            fitView({ padding: 0.2, duration: 800 });
        }, 50);

        return () => clearTimeout(timeout);
    }, [nodes, activeNodeId, fitView, setCenter]);

    return null;
}

/* ── Graph Layout Logic (Dagre) ─────────────────────────── */

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 260;
const nodeHeight = 100;

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

/* ── Helper Functions ──────────────────────────────────── */

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
            style: { transition: 'all 0.5s ease-in-out' }
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
                    animated: false,
                    style: { stroke: 'rgba(100, 116, 139, 0.3)', strokeWidth: 1.5 },
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
                    animated: true,
                    style: { stroke: '#38bdf8', strokeWidth: 3 },
                    zIndex: 10,
                });
            }
        }
    }

    return edges;
}

/* ── Main Component ────────────────────────────────────── */

interface GraphPanelProps {
    clientId: string;
    toolCalls: ToolCallEntry[];
    currentNode: string | null;
}

export default function GraphPanel({ clientId, toolCalls, currentNode }: GraphPanelProps) {
    const [nodeContent, setNodeContent] = useState<string | null>(null);
    const [breadcrumb, setBreadcrumb] = useState<string[]>([]);
    const [allClientNodes, setAllClientNodes] = useState<ServerNodeMetadata[]>([]);

    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    useEffect(() => {
        const fetchAllNodes = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || '';
                const res = await fetch(`${apiUrl}/api/clients/${clientId}/graph/nodes`);
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
        if (nodeIdsSet.size === 0) nodeIdsSet.add(`${clientId}-index`);

        const nodeIds = Array.from(nodeIdsSet);
        const visitedNodes = new Set(toolCalls
            .filter(tc => tc.name === 'follow_link')
            .map(tc => tc.args?.node_id as string)
            .filter(Boolean));

        const rawNodes = createNodes(nodeIds, currentNode, visitedNodes);
        const rawEdges = buildEdges(nodeIds, toolCalls, allClientNodes);

        const layouted = getLayoutedElements(rawNodes, rawEdges);
        setNodes(layouted);
        setEdges(rawEdges);
    }, [allClientNodes, toolCalls, currentNode, clientId, setNodes, setEdges]);

    useEffect(() => {
        if (currentNode && !breadcrumb.includes(currentNode)) {
            setBreadcrumb(prev => [...prev, currentNode]);
        }
    }, [currentNode, breadcrumb]);

    const fetchNodeContent = useCallback(async (nodeId: string) => {
        try {
            const apiUrl = import.meta.env.VITE_API_URL || '';
            const res = await fetch(`${apiUrl}/api/clients/${clientId}/graph/nodes/${nodeId}`);
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
        <div className="graph-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', background: '#090a0f', borderRadius: '16px', overflow: 'hidden' }}>
            <div className="graph-panel__breadcrumb" style={{ height: '3.5rem', display: 'flex', alignItems: 'center', paddingLeft: '1.5rem', paddingRight: '1.5rem', background: 'rgba(0,0,0,0.2)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <div className="flex items-center gap-3">
                    <Share2 size={14} className="text-slate-500" />
                    <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-slate-500">Path</span>
                </div>
                <div className="mx-4 h-4 w-[1px] background-white/10" />
                <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
                    {breadcrumb.map((nodeId, i) => (
                        <div key={nodeId} className="flex items-center gap-2">
                            {i > 0 && <ChevronRight size={10} className="text-slate-700" />}
                            <span className={`font-mono text-xs ${nodeId === currentNode ? 'text-white font-bold' : 'text-slate-500'}`}>
                                {nodeId}
                            </span>
                        </div>
                    ))}
                    {breadcrumb.length === 0 && (
                        <span className="font-mono text-xs text-slate-600 italic">Awaiting traversal...</span>
                    )}
                </div>
            </div>

            <div className="graph-panel__flow">
                <ReactFlowProvider>
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        nodeTypes={nodeTypes}
                        fitView
                        proOptions={{ hideAttribution: true }}
                        minZoom={0.2}
                        maxZoom={2}
                    >
                        <Background variant={BackgroundVariant.Dots} color="#2a2f45" gap={24} size={1} />
                        <Controls position="bottom-right" />
                        <AutoGraphFitter nodes={nodes} activeNodeId={currentNode} />
                    </ReactFlow>
                </ReactFlowProvider>
            </div>

            {currentNode && nodeContent && (
                <div className="graph-panel__content-card glass-card-premium" style={{ position: 'absolute', bottom: '1.5rem', left: '1.5rem', right: '1.5rem', maxHeight: '200px', display: 'flex', flexDirection: 'column', background: 'rgba(15, 16, 22, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '16px', padding: '1.25rem', zIndex: 10 }}>
                    <div className="content-card__header flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                            <div className="bg-sky-500/10 p-1.5 rounded-lg text-sky-400">
                                <FileText size={16} />
                            </div>
                            <span className="font-mono text-xs text-white/90 font-bold">{currentNode}</span>
                        </div>
                    </div>
                    <div className="content-card__body overflow-y-auto">
                        <pre className="font-mono text-[11px] leading-relaxed text-slate-400 whitespace-pre-wrap">
                            {nodeContent.slice(0, 1000)}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    );
}
