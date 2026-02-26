/**
 * Synapse — Graph Panel Component
 *
 * Right side of the split-screen briefing view.
 * Shows a React Flow graph topology with animated node traversal,
 * breadcrumb navigation, and a node content card.
 */

import { useMemo, useCallback, useEffect, useState } from 'react';
import {
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
    return (
        <div className={`graph-node graph-node--${data.layer} ${data.isActive ? 'graph-node--active' : ''} ${data.isVisited ? 'graph-node--visited' : ''}`}>
            <Handle type="target" position={Position.Top} className="graph-node__handle" />
            <div className="graph-node__icon">
                {data.layer === 'client' ? '👤' : data.layer === 'product' ? '📦' : '🏭'}
            </div>
            <div className="graph-node__label">{data.label}</div>
            {data.isActive && <div className="graph-node__pulse" />}
            <Handle type="source" position={Position.Bottom} className="graph-node__handle" />
        </div>
    );
}

const nodeTypes: NodeTypes = { skillNode: SkillNode };

/* ── Graph Panel ───────────────────────────────────────── */

interface GraphPanelProps {
    clientId: string;
    toolCalls: ToolCallEntry[];
    currentNode: string | null;
}

// Layout positions for nodes in a hierarchical tree
function layoutNodes(nodeIds: string[], activeId: string | null, visitedIds: Set<string>): Node[] {
    const nodes: Node[] = [];
    const centerX = 300;
    const startY = 40;
    const spacingY = 100;
    const spacingX = 180;

    nodeIds.forEach((id, i) => {
        const row = Math.floor(i / 3);
        const col = i % 3;
        const x = centerX + (col - 1) * spacingX;
        const y = startY + row * spacingY;

        const layer = id.includes('product') || id.includes('cpq') || id.includes('revenue')
            ? 'product'
            : id.includes('manufacturing') || id.includes('industry')
                ? 'industry'
                : 'client';

        nodes.push({
            id,
            type: 'skillNode',
            position: { x, y },
            data: {
                label: id.replace(/-/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
                layer,
                isActive: id === activeId,
                isVisited: visitedIds.has(id),
            },
            style: { transition: 'all 0.5s ease-in-out' }
        });
    });

    return nodes;
}

function buildEdges(
    nodeIds: string[],
    toolCalls: ToolCallEntry[],
    metadata: ServerNodeMetadata[]
): Edge[] {
    const edges: Edge[] = [];
    const seenEdges = new Set<string>();

    // 1. Build inherent links from metadata (static structure)
    metadata.forEach(node => {
        node.links.forEach(targetId => {
            if (nodeIds.includes(targetId)) {
                const edgeId = `inherent-${node.node_id}-${targetId}`;
                seenEdges.add(`${node.node_id}->${targetId}`);
                edges.push({
                    id: edgeId,
                    source: node.node_id,
                    target: targetId,
                    animated: false,
                    style: { stroke: 'rgba(58, 64, 96, 0.4)', strokeWidth: 1 },
                });
            }
        });
    });

    // 2. Build edges from follow_link tool calls (traversal path)
    for (let i = 1; i < toolCalls.length; i++) {
        const prev = toolCalls[i - 1];
        const curr = toolCalls[i];
        if (prev.name === 'follow_link' && curr.name === 'follow_link') {
            const sourceId = prev.args?.node_id as string;
            const targetId = curr.args?.node_id as string;
            if (sourceId && targetId) {
                const edgeId = `traversal-${sourceId}-${targetId}`;
                edges.push({
                    id: edgeId,
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

export default function GraphPanel({ clientId, toolCalls, currentNode }: GraphPanelProps) {
    const [nodeContent, setNodeContent] = useState<string | null>(null);
    const [breadcrumb, setBreadcrumb] = useState<string[]>([]);
    const [allClientNodes, setAllClientNodes] = useState<ServerNodeMetadata[]>([]);

    // Fetch all nodes for this client on mount to populate the graph
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

    // Collect all node IDs
    const discoveredNodes = useMemo(() => {
        const ids = new Set<string>(allClientNodes.map(n => n.node_id));
        toolCalls.forEach(tc => {
            if (tc.name === 'follow_link' && tc.args?.node_id) {
                ids.add(tc.args.node_id as string);
            }
        });
        // Always include index
        if (ids.size === 0) ids.add(`${clientId}-index`);
        return Array.from(ids);
    }, [toolCalls, clientId, allClientNodes]);

    const visitedNodes = useMemo(() => {
        return new Set(toolCalls
            .filter(tc => tc.name === 'follow_link')
            .map(tc => tc.args?.node_id as string)
            .filter(Boolean));
    }, [toolCalls]);

    const initialNodes = useMemo(
        () => layoutNodes(discoveredNodes, currentNode, visitedNodes),
        [discoveredNodes, currentNode, visitedNodes]
    );

    const initialEdges = useMemo(
        () => buildEdges(discoveredNodes, toolCalls, allClientNodes),
        [discoveredNodes, toolCalls, allClientNodes]
    );

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    // Update nodes when tool calls change
    useEffect(() => {
        setNodes(layoutNodes(discoveredNodes, currentNode, visitedNodes));
        setEdges(buildEdges(discoveredNodes, toolCalls, allClientNodes));
    }, [discoveredNodes, currentNode, visitedNodes, toolCalls, allClientNodes, setNodes, setEdges]);

    // Breadcrumb trail
    useEffect(() => {
        if (currentNode && !breadcrumb.includes(currentNode)) {
            setBreadcrumb(prev => [...prev, currentNode]);
        }
    }, [currentNode, breadcrumb]);

    // Fetch node content when current node changes
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
        <div className="graph-panel">
            {/* Breadcrumb */}
            <div className="graph-panel__breadcrumb">
                <span className="breadcrumb__label">Path:</span>
                {breadcrumb.map((nodeId, i) => (
                    <span key={nodeId} className="breadcrumb__item">
                        {i > 0 && <span className="breadcrumb__arrow">→</span>}
                        <span className={nodeId === currentNode ? 'breadcrumb__active' : ''}>
                            {nodeId}
                        </span>
                    </span>
                ))}
                {breadcrumb.length === 0 && (
                    allClientNodes.length > 0
                        ? <span className="breadcrumb__empty">Waiting for ADK Agent traversal...</span>
                        : <span className="breadcrumb__empty animate-pulse">Loading Client Skill Graph...</span>
                )}
            </div>

            {/* React Flow Graph */}
            <div className="graph-panel__flow">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    nodeTypes={nodeTypes}
                    fitView
                    proOptions={{ hideAttribution: true }}
                >
                    <Background variant={BackgroundVariant.Dots} color="#2a2f45" gap={20} size={1} />
                    <Controls position="bottom-right" />
                </ReactFlow>
            </div>

            {/* Node Content Card */}
            {currentNode && nodeContent && (
                <div className="graph-panel__content-card">
                    <div className="content-card__header">
                        <span className="content-card__icon">📄</span>
                        <span className="content-card__title">{currentNode}</span>
                    </div>
                    <div className="content-card__body">
                        <pre>{nodeContent.slice(0, 500)}...</pre>
                    </div>
                </div>
            )}
        </div>
    );
}
