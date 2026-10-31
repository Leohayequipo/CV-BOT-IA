import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Fixed ports away from Vite's defaults, so the site runs next to other local projects
  server: {
    port: 5180,
    strictPort: true,
    // Vite serves only this folder by default; the design-token test reads docs/DESIGN.md
    fs: { allow: ['.', '../docs'] },
  },
  preview: { port: 4180, strictPort: true },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    // Vitest replaces CSS with empty modules; the token test needs the real file
    css: { include: [/tokens\.css/] },
  },
});
