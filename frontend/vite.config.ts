import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { loadEnv } from 'vite';
import { defineConfig } from 'vitest/config';
import { seo } from './build/seo.ts';

export default defineConfig(({ mode }) => ({
  // VITE_SITE_URL: the site's public address, which link previews need in full
  plugins: [react(), tailwindcss(), seo(loadEnv(mode, process.cwd(), 'VITE_').VITE_SITE_URL)],
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
}));
