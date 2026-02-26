/**
 * PCMProcessor - AudioWorklet for raw 16-bit PCM streaming.
 * 
 * Handles buffering and feeding the Web Audio API without main thread jank.
 * Critical for Gemini Live "Zero-Latency" feel.
 */
class PCMProcessor extends AudioWorkletProcessor {
    constructor() {
        super()
        this.buffer = new Float32Array(0)
        this.port.onmessage = this.handleMessage.bind(this)
        this.isBuffering = true;
        this.BUFFER_THRESHOLD = 4800; // 200ms at 24kHz
    }

    process(inputs, outputs, parameters) {
        const output = outputs[0]
        const channel = output[0]

        if (!channel) return true

        if (this.isBuffering) {
            if (this.buffer.length >= this.BUFFER_THRESHOLD) {
                this.isBuffering = false;
            } else {
                channel.fill(0);
                return true;
            }
        }

        if (this.buffer.length >= channel.length) {
            channel.set(this.buffer.subarray(0, channel.length))
            this.buffer = this.buffer.subarray(channel.length)

            // Send volume back to main thread for visualization
            let sum = 0
            for (let i = 0; i < channel.length; i++) {
                sum += channel[i] * channel[i]
            }
            const rms = Math.sqrt(sum / channel.length)
            this.port.postMessage({ type: 'volume', volume: rms })
        } else {
            // Underflow: fill remaining buffer, pad with silence, re-enter buffering mode
            channel.fill(0)
            if (this.buffer.length > 0) {
                channel.set(this.buffer.subarray(0, this.buffer.length))
                this.buffer = new Float32Array(0)
            }
            this.isBuffering = true;
        }

        return true
    }

    /**
     * Receive raw PCM chunks (Float32) from the Main Thread
     */
    handleMessage(e) {
        const newData = e.data
        if (newData.type === 'flush') {
            this.buffer = new Float32Array(0)
            return
        }

        // newData is Float32Array
        const newBuffer = new Float32Array(this.buffer.length + newData.length)
        newBuffer.set(this.buffer)
        newBuffer.set(newData, this.buffer.length)
        this.buffer = newBuffer
    }
}

registerProcessor('pcm-processor', PCMProcessor)
