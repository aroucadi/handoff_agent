/**
 * Synapse — WebSocket Audio + Vision Hook
 *
 * Manages the bidirectional audio/vision connection to the Synapse backend,
 * which proxies to Gemini Live. Captures microphone PCM audio,
 * sends it via WebSocket, and plays back received audio.
 */

import { useRef, useState, useCallback, useEffect } from 'react';
import { audioStreamer } from './infrastructure/audio/AudioStreamer';

export interface TranscriptEntry {
    role: 'user' | 'agent';
    text: string;
    timestamp: string;
}

export interface ToolCallEntry {
    name: string;
    args: Record<string, unknown>;
    timestamp: string;
}

export type AgentStatus = 'listening' | 'thinking' | 'speaking';

interface UseVoiceSessionReturn {
    isConnected: boolean;
    isMicActive: boolean;
    isScreenShared: boolean;
    agentStatus: AgentStatus;
    transcript: TranscriptEntry[];
    toolCalls: ToolCallEntry[];
    currentNode: string | null;
    connect: (sessionId: string) => void;
    disconnect: () => void;
    toggleMic: () => void;
    toggleScreenShare: () => void;
    sendText: (text: string) => void;
}

const INPUT_SAMPLE_RATE = 16000;

export function useVoiceSession(): UseVoiceSessionReturn {
    const wsRef = useRef<WebSocket | null>(null);
    // Audio Refs
    const micWorkletRef = useRef<AudioWorkletNode | null>(null);
    const micCtxRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);

    // Screen Sharing Refs
    const screenStreamRef = useRef<MediaStream | null>(null);
    const captureIntervalRef = useRef<number | null>(null);

    const [isConnected, setIsConnected] = useState(false);
    const [isMicActive, setIsMicActive] = useState(false);
    const [isScreenShared, setIsScreenShared] = useState(false);
    const [agentStatus, setAgentStatus] = useState<AgentStatus>('listening');
    const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
    const [toolCalls, setToolCalls] = useState<ToolCallEntry[]>([]);
    const [currentNode, setCurrentNode] = useState<string | null>(null);
    const isStartingMicRef = useRef(false);

    const handleAudioChunk = useCallback((base64Data: string) => {
        const raw = atob(base64Data);
        const bytes = new Uint8Array(raw.length);
        for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);

        audioStreamer.enqueue(bytes.buffer);
        audioStreamer.resume();
        setAgentStatus('speaking');
    }, []);

    const connect = useCallback(async (sessionId: string) => {
        // Enforce strict WebSocket singleton. 
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        // KILL the playback context so ghost voices from buffered chunks stop immediately
        await audioStreamer.close();
        await audioStreamer.initialize();

        setTranscript([]);
        setToolCalls([]);
        setCurrentNode(null);

        let wsUrl: string;
        const envWsUrl = import.meta.env.VITE_WS_URL;
        const envApiUrl = import.meta.env.VITE_API_URL;

        if (envWsUrl) {
            wsUrl = `${envWsUrl}/ws/sessions/${sessionId}`;
        } else if (envApiUrl) {
            // Bulletproof derivation from the known-working API URL
            const derivedWsUrl = envApiUrl.replace(/^http/, 'ws');
            wsUrl = `${derivedWsUrl}/ws/sessions/${sessionId}`;
        } else {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            wsUrl = `${protocol}//${window.location.host}/ws/sessions/${sessionId}`;
        }

        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            setIsConnected(true);
            console.log('[WS] Connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'audio':
                    handleAudioChunk(data.data);
                    break;

                case 'text':
                    setTranscript(prev => [...prev, {
                        role: 'agent',
                        text: data.text,
                        timestamp: new Date().toISOString(),
                    }]);
                    break;

                case 'tool_call':
                    setToolCalls(prev => [...prev, {
                        name: data.name,
                        args: data.args,
                        timestamp: new Date().toISOString(),
                    }]);
                    // Track current node from follow_link calls
                    if (data.name === 'follow_link' && data.args?.node_id) {
                        setCurrentNode(data.args.node_id as string);
                    }
                    setAgentStatus('thinking'); // Agent is processing the tool call
                    break;

                case 'tool_result':
                    try {
                        const parsedResult = JSON.parse(data.result);
                        if (parsedResult.node_id) {
                            setCurrentNode(parsedResult.node_id);
                        }
                    } catch (e) {
                        // ignore parse errors if result is not json
                    }
                    break;

                case 'interrupted':
                    audioStreamer.flush(); // Instant Barge-in!
                    setAgentStatus('listening');
                    break;

                case 'turn_complete':
                    setAgentStatus('listening');
                    break;

                case 'error':
                    console.error('[WS] Error:', data.error);
                    break;
            }
        };

        ws.onclose = () => {
            setIsConnected(false);
            setIsMicActive(false);
            setIsScreenShared(false);
            console.log('[WS] Disconnected');
        };
    }, [handleAudioChunk]);

    const stopMic = useCallback(() => {
        if (micWorkletRef.current) {
            micWorkletRef.current.disconnect();
            micWorkletRef.current = null;
        }
        if (micCtxRef.current) {
            micCtxRef.current.close().catch(console.error);
            micCtxRef.current = null;
        }
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(t => t.stop());
            mediaStreamRef.current = null;
        }
        setIsMicActive(false);
    }, []);

    const startMic = useCallback(async () => {
        if (isStartingMicRef.current) return;
        try {
            isStartingMicRef.current = true;
            stopMic(); // Enforce singleton mic

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: INPUT_SAMPLE_RATE,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                },
            });

            mediaStreamRef.current = stream;

            const micCtx = new (window.AudioContext || (window as any).webkitAudioContext)({
                sampleRate: INPUT_SAMPLE_RATE
            });
            micCtxRef.current = micCtx;

            // Browser Autoplay Policy: Force resume after user gesture
            if (micCtx.state === 'suspended') {
                await micCtx.resume();
            }

            await micCtx.audioWorklet.addModule('/mic-processor.js');

            // Check for race condition during async addModule
            if (micCtx.state === 'closed') return;

            const source = micCtx.createMediaStreamSource(stream);
            const micNode = new AudioWorkletNode(micCtx, 'mic-processor');
            micWorkletRef.current = micNode;

            micNode.port.onmessage = (e) => {
                if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

                const { data } = e.data;
                const int16 = data as Int16Array;

                // Base64 encode and send
                const bytes = new Uint8Array(int16.buffer);
                let binary = '';
                for (let i = 0; i < bytes.byteLength; i++) {
                    binary += String.fromCharCode(bytes[i]);
                }
                const b64 = btoa(binary);

                wsRef.current.send(JSON.stringify({ type: 'audio', data: b64 }));
            };

            source.connect(micNode);
            setIsMicActive(true);
        } catch (err) {
            console.error('[MIC] Failed to start:', err);
        } finally {
            isStartingMicRef.current = false;
        }
    }, [stopMic]);

    const toggleMic = useCallback(() => {
        if (isMicActive) {
            stopMic();
        } else {
            startMic();
        }
    }, [isMicActive, startMic, stopMic]);

    // --- Screen Sharing (Vision) Implementation ---
    const startScreenShare = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    frameRate: { ideal: 1 }, // Need low framerate for Live API limits
                },
                audio: false,
            });

            screenStreamRef.current = stream;
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            // Listen for user stopping via browser UI
            stream.getVideoTracks()[0].onended = () => {
                stopScreenShare();
            };

            // Capture frame every 1 second
            captureIntervalRef.current = window.setInterval(() => {
                if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
                if (!video.videoWidth) return;

                // Lock native resolution, or downscale if too large
                const scale = Math.min(1, 1280 / video.videoWidth);
                canvas.width = video.videoWidth * scale;
                canvas.height = video.videoHeight * scale;

                if (ctx) {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    // Get base64 JPEG
                    // const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
                    // const b64 = dataUrl.split(',')[1];
                    // wsRef.current.send(JSON.stringify({ type: 'image', data: b64 }));
                    // Disable image send for 2.5-flash-native-audio-latest as it throws 1007 errors
                }
            }, 1000);

            setIsScreenShared(true);
        } catch (err) {
            console.error('[SCREEN] Failed to share screen:', err);
        }
    }, []);

    const stopScreenShare = useCallback(() => {
        if (captureIntervalRef.current) {
            clearInterval(captureIntervalRef.current);
            captureIntervalRef.current = null;
        }
        if (screenStreamRef.current) {
            screenStreamRef.current.getTracks().forEach(t => t.stop());
            screenStreamRef.current = null;
        }
        setIsScreenShared(false);
    }, []);

    const toggleScreenShare = useCallback(() => {
        if (isScreenShared) {
            stopScreenShare();
        } else {
            startScreenShare();
        }
    }, [isScreenShared, startScreenShare, stopScreenShare]);

    const disconnect = useCallback(() => {
        stopMic();
        stopScreenShare();
        if (wsRef.current) {
            wsRef.current.send(JSON.stringify({ type: 'end' }));
            wsRef.current.close();
            wsRef.current = null;
        }

        // KILL the playback context so ghost voices from buffered chunks stop immediately
        audioStreamer.close().catch(console.error);

        setIsConnected(false);
    }, [stopMic]);

    const sendText = useCallback((text: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        // Text interruption instantly kills current audio
        audioStreamer.flush();
        setAgentStatus('thinking');

        wsRef.current.send(JSON.stringify({ type: 'text', text }));
        setTranscript(prev => [...prev, {
            role: 'user',
            text,
            timestamp: new Date().toISOString(),
        }]);
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopMic();
            stopScreenShare();
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [stopMic]);

    return {
        isConnected,
        isMicActive,
        isScreenShared,
        agentStatus,
        transcript,
        toolCalls,
        currentNode,
        connect,
        disconnect,
        toggleMic,
        toggleScreenShare,
        sendText,
    };
}
