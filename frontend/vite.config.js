import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    host: "0.0.0.0",
    port: 5174,

    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
      },

      "/patients": {
        target: "http://backend:8000",
        changeOrigin: true,
      },

      "/cases": {
        target: "http://backend:8000",
        changeOrigin: true,
      },
    },
  },
});
