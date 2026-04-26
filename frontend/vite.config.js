import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'

export default defineConfig({
  base: './',
  plugins: [
    vue(),
    {
      name: 'write-port-to-file',
      configureServer(server) {
        server.httpServer?.once('listening', () => {
          const address = server.httpServer.address()
          const port = typeof address === 'string' ? address : address.port
          fs.writeFileSync('.vite-port', port.toString())
        })
        server.httpServer?.once('close', () => {
          if (fs.existsSync('.vite-port')) fs.unlinkSync('.vite-port')
        })
      }
    }
  ],
})