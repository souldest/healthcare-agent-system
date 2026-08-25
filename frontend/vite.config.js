import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    host: "0.0.0.0",
    port: 5174,

    proxy: {
      "/api": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },

      "/patients": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },

      "/cases": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
    },
  },
});
