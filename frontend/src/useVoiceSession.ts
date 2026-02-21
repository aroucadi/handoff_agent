/**
 * Synapse — WebSocket Audio + Vision Hook
 *
 * Manages the bidirectional audio/vision connection to the Synapse backend,
 * which proxies to Gemini Live. Captures microphone PCM audio,
 * sends it via WebSocket, and plays back received audio.
 */

import { useRef, useState, useCallback, useEffect } from 'react';

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

interface UseVoiceSessionReturn {
    isConnected: boolean;
    isMicActive: boolean;
    isScreenShared: boolean;
    isAgentSpeaking: boolean;
    transcript: TranscriptEntry[];
    toolCalls: ToolCallEntry[];
    currentNode: string | null;
    connect: (sessionId: string) => void;
    disconnect: () => void;
    toggleMic: () => void;
    toggleScreenShare: () => void;
    sendText: (text: string) => void;
}

const SAMPLE_RATE = 16000;
const PLAYBACK_RATE = 24000;

export function useVoiceSession(): UseVoiceSessionReturn {
    const wsRef = useRef<WebSocket | null>(null);
    const audioCtxRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);

    // Screen Sharing Refs
    const screenStreamRef = useRef<MediaStream | null>(null);
    const captureIntervalRef = useRef<number | null>(null);

    const [isConnected, setIsConnected] = useState(false);
    const [isMicActive, setIsMicActive] = useState(false);
    const [isScreenShared, setIsScreenShared] = useState(false);
    const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
    const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
    const [toolCalls, setToolCalls] = useState<ToolCallEntry[]>([]);
    const [currentNode, setCurrentNode] = useState<string | null>(null);

    const playAudio = useCallback((base64Data: string) => {
        if (!audioCtxRef.current) {
            audioCtxRef.current = new AudioContext({ sampleRate: PLAYBACK_RATE });
        }
        const ctx = audioCtxRef.current;
        const raw = atob(base64Data);
        const bytes = new Uint8Array(raw.length);
        for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);

        // Convert Int16 PCM to Float32
        const int16 = new Int16Array(bytes.buffer);
        const float32 = new Float32Array(int16.length);
        for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;

        const buffer = ctx.createBuffer(1, float32.length, PLAYBACK_RATE);
        buffer.getChannelData(0).set(float32);

        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.start();
        setIsAgentSpeaking(true);
        source.onended = () => setIsAgentSpeaking(false);
    }, []);

    const connect = useCallback((sessionId: string) => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/sessions/${sessionId}`;

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
                    playAudio(data.data);
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
                    break;

                case 'tool_result':
                    // Could update UI with result preview
                    break;

                case 'interrupted':
                    setIsAgentSpeaking(false);
                    break;

                case 'turn_complete':
                    setIsAgentSpeaking(false);
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
    }, [playAudio]);

    const startMic = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: SAMPLE_RATE,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                },
            });

            mediaStreamRef.current = stream;
            const ctx = new AudioContext({ sampleRate: SAMPLE_RATE });
            audioCtxRef.current = ctx;

            const source = ctx.createMediaStreamSource(stream);
            // Use ScriptProcessor (deprecated but widely supported)
            const processor = ctx.createScriptProcessor(4096, 1, 1);
            processorRef.current = processor;

            processor.onaudioprocess = (e) => {
                if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

                const float32 = e.inputBuffer.getChannelData(0);
                // Convert Float32 → Int16 PCM
                const int16 = new Int16Array(float32.length);
                for (let i = 0; i < float32.length; i++) {
                    const s = Math.max(-1, Math.min(1, float32[i]));
                    int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
                }

                // Base64 encode and send
                const bytes = new Uint8Array(int16.buffer);
                let binary = '';
                for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
                const b64 = btoa(binary);

                wsRef.current.send(JSON.stringify({ type: 'audio', data: b64 }));
            };

            source.connect(processor);
            processor.connect(ctx.destination);
            setIsMicActive(true);
        } catch (err) {
            console.error('[MIC] Failed to start:', err);
        }
    }, []);

    const stopMic = useCallback(() => {
        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current = null;
        }
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(t => t.stop());
            mediaStreamRef.current = null;
        }
        setIsMicActive(false);
    }, []);

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
                    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
                    const b64 = dataUrl.split(',')[1];
                    wsRef.current.send(JSON.stringify({ type: 'image', data: b64 }));
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
        setIsConnected(false);
    }, [stopMic]);

    const sendText = useCallback((text: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
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
        isAgentSpeaking,
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
