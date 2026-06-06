import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// AgentStrike dashboard — Vite config.
// Proxies /api and /events to the FastAPI backend during development so the
// SSE stream and REST routes are reachable without CORS gymnastics.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
