import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

export default defineConfig({
  server: {
    https: {
      key: fs.readFileSync('../ssl/key.pem'),
      cert: fs.readFileSync('../ssl/cert.pem'),
    },
    host: '0.0.0.0',
    port: 5173
  },
  plugins: [react()]
})
