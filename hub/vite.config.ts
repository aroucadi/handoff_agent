import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// @ts-ignore - IDE type resolution conflict across portals
export default defineConfig({
    plugins: [react() as any],
    build: {
        rollupOptions: {
            output: {
                manualChunks: {
                    'vendor-react': ['react', 'react-dom', 'react-router-dom'],
                    'vendor-icons': ['lucide-react'],
                },
            },
        },
        chunkSizeWarningLimit: 1000,
    },
    server: {
        port: 5174,
        proxy: {
            '/api': {
                target: 'http://localhost:8003',
                changeOrigin: true,
            },
        },
    },
});
