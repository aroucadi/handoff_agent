/**
 * MicProcessor - AudioWorklet for raw audio input.
 * 
 * Captures Float32 audio from microphone and sends it to the main thread.
 * Optimizes performance by avoiding main thread ScriptProcessor.
 */
class MicProcessor extends AudioWorkletProcessor {
    constructor() {
        super()
        this.buffer = new Int16Array(1024)
        this.offset = 0
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0]
        if (!input || !input[0]) return true

        const channelData = input[0]

        for (let i = 0; i < channelData.length; i++) {
            const s = Math.max(-1, Math.min(1, channelData[i]))
            const val = s < 0 ? s * 0x8000 : s * 0x7FFF
            this.buffer[this.offset++] = val

            if (this.offset >= this.buffer.length) {
                // Calculate RMS Volume for UI Telemetry
                let sum = 0;
                for (let j = 0; j < this.buffer.length; j++) {
                    const norm = this.buffer[j] / 32768.0;
                    sum += norm * norm;
                }
                const rms = Math.sqrt(sum / this.buffer.length);

                this.port.postMessage({ type: 'audio', data: this.buffer, volume: rms })
                this.buffer = new Int16Array(1024)
                this.offset = 0
            }
        }

        return true
    }
}

registerProcessor('mic-processor', MicProcessor)
