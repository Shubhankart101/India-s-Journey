import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backend = process.env.DJANGO_URL || 'http://127.0.0.1:8000';

export default defineConfig(({ mode }) => {
  const staticBuild = mode === 'static' || process.env.VITE_STATIC === '1';
  return {
    base: staticBuild ? './' : '/',
    define: { 'import.meta.env.VITE_STATIC': JSON.stringify(staticBuild ? '1' : process.env.VITE_STATIC || '') },
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': backend,
      '/admin': backend,
      '/accounts': backend,
      '/static': backend,
    },
  },
  build: {
    outDir: staticBuild ? '../docs' : 'dist',
    assetsDir: staticBuild ? 'build' : 'assets',
    emptyOutDir: staticBuild ? false : true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/chart.js') || id.includes('node_modules/react-chartjs-2')) return 'charts';
          if (id.includes('node_modules')) return 'vendor';
          return undefined;
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.jsx'],
    include: ['src/**/*.test.{js,jsx}'],
    css: false,
    testTimeout: 20000,
  },
  };
});
