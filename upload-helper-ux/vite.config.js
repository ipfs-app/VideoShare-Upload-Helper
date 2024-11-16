import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    assetsDir: "./",
    rollupOptions: {
        output: {
            entryFileNames: "[hash].js",
            assetFileNames: "[hash].[ext]"
        }
    }
  },
  base: "./",
})
