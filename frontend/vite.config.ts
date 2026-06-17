import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/backtest': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/signal': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/broker': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/diagnostic': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/brain-stats': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/forex': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/command': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/risk': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/market': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/trade': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
