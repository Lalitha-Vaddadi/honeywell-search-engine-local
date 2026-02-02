const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("electron", {
  saveTheme: (theme) => ipcRenderer.send("save-theme", theme),
})
