import {
  randomFillSync,
  webcrypto as nodeWebcrypto
} from "node:crypto";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const globalWithCrypto = globalThis as typeof globalThis & {
  crypto?: typeof nodeWebcrypto;
};

if (!globalWithCrypto.crypto) {
  globalWithCrypto.crypto = nodeWebcrypto ?? ({} as typeof nodeWebcrypto);
}

if (
  globalWithCrypto.crypto &&
  typeof globalWithCrypto.crypto.getRandomValues !== "function"
) {
  globalWithCrypto.crypto.getRandomValues = (<T extends ArrayBufferView>(
    array: T
  ) => {
    randomFillSync(array);
    return array;
  }) as typeof globalWithCrypto.crypto.getRandomValues;
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true
      }
    }
  }
});
