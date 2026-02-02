const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("splash", {
  onStatus: (cb) => ipcRenderer.on("status", (_, msg) => cb(msg))
})
