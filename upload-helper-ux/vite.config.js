import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    assetsDir: "./",
    rollupOptions: {
      input: {
        upload: path.resolve(__dirname, 'upload.html'),
        index: path.resolve(__dirname, 'index.html')
      },
      output: {
        entryFileNames: "[hash].js",
        assetFileNames: "[hash].[ext]",
      }
    }
  },
  base: "./",
})
