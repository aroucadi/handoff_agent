/**
 * AudioStreamer - Manages Real-Time PCM Playback
 * 
 * Orchestrates the AudioContext and AudioWorklet for Gemini Live.
 * Handles Int16 -> Float32 conversion.
 */
export class AudioStreamer {
    private audioContext: AudioContext | null = null;
    private workletNode: AudioWorkletNode | null = null;
    private isInitialized = false;
    private initPromise: Promise<void> | null = null;

    async initialize() {
        if (this.isInitialized) return;
        if (this.initPromise) return this.initPromise;

        this.initPromise = (async () => {
            // Gemini Live output is 24kHz
            this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });

            try {
                await this.audioContext.audioWorklet.addModule('/pcm-processor.js');
                this.workletNode = new AudioWorkletNode(this.audioContext, 'pcm-processor');
                this.workletNode.connect(this.audioContext.destination);
                this.isInitialized = true;
                this.initPromise = null;
                console.log('[AudioStreamer] Initialized with Worklet at 24kHz');
            } catch (e) {
                console.error('[AudioStreamer] Worklet initialization failed', e);
                this.initPromise = null;
            }
        })();

        return this.initPromise;
    }

    /**
    * Enqueue raw Int16 PCM chunk from WebSocket
    */
    enqueue(chunk: ArrayBuffer) {
        if (!this.isInitialized || !this.workletNode) return;

        // Convert Int16 -> Float32
        const int16 = new Int16Array(chunk);
        const float32 = new Float32Array(int16.length);

        for (let i = 0; i < int16.length; i++) {
            float32[i] = int16[i] / 32768.0;
        }

        // Send to Worklet
        this.workletNode.port.postMessage(float32);
    }

    /**
     * Stop playback immediately (Barge-In)
     */
    stop() {
        if (!this.workletNode) return;
        // Tell worklet to flush
        this.workletNode.port.postMessage({ type: 'flush' });
    }

    async resume() {
        if (this.audioContext?.state === 'suspended') {
            await this.audioContext.resume();
        }
    }

    async close() {
        if (this.audioContext) {
            await this.audioContext.close();
            this.audioContext = null;
            this.workletNode = null;
            this.isInitialized = false;
            this.initPromise = null;
        }
    }
}

export const audioStreamer = new AudioStreamer();
