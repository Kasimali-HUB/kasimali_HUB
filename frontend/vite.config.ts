import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Codespaces (and Docker/WSL/any remote dev container) can only forward
    // a port if the dev server listens on all network interfaces, not just
    // localhost. Without this, the port can look "active" from inside the
    // container while being completely unreachable from outside it - which
    // shows up as a confusing 404 from the forwarding proxy, not a clear
    // connection error.
    host: true,
    port: 5173,
    strictPort: true,
    // The forwarded Codespaces/Gitpod/etc. hostname differs from
    // "localhost", which some Vite versions reject by default as a
    // dev-only anti-DNS-rebinding check. Safe to disable for local dev.
    allowedHosts: true,
  },
})
