/// <reference types="vitest/config" />
import { env } from "node:process";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Studio talks to the backend same-origin through this proxy (backend on :8000 by default).
    proxy: { "/api": env.GUIDE_API_URL ?? "http://localhost:8000" },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["src/test-setup.ts"],
  },
});
