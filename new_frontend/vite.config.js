import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const isVercelBuild = process.env.VERCEL === '1';

// https://vite.dev/config/
export default defineConfig({
  base: isVercelBuild ? '/' : '/static/',
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/users': 'http://localhost:8000',
      '/feed': 'http://localhost:8000',
      '/uploadfile': 'http://localhost:8000',
      '/posts': 'http://localhost:8000',
    },
  },
  build: {
    outDir: isVercelBuild ? 'dist' : '../static/dist',
    emptyOutDir: true,
  },
})
