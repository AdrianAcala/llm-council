import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        // Use BACKEND_URL env var for Docker internal networking,
        // fall back to VITE_API_BASE or localhost for local development
        target: process.env.BACKEND_URL || process.env.VITE_API_BASE || 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
