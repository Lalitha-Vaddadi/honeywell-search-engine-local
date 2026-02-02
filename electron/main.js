const { app, BrowserWindow, dialog, ipcMain, globalShortcut } = require("electron")
const path = require("path")
const { exec } = require("child_process")
const http = require("http")
const { readState, writeState } = require("./state")

function run(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, { windowsHide: true }, (err, stdout, stderr) => {
      if (err) reject(stderr || err)
      else resolve(stdout)
    })
  })
}

function waitForHealth(url, timeoutMs = 120000) {
  const start = Date.now()

  return new Promise((resolve, reject) => {
    const check = () => {
      if (Date.now() - start > timeoutMs) {
        reject(new Error("Backend health check timeout"))
        return
      }

      http
        .get(url, res => {
          if (res.statusCode === 200) resolve()
          else setTimeout(check, 2000)
        })
        .on("error", () => setTimeout(check, 2000))
    }
    check()
  })
}

const projectRoot = path.join(__dirname, "..")
const dockerComposePath = path.join(projectRoot, "docker", "docker-compose.yml")

let splashWindow = null
let mainWindow = null

ipcMain.on("save-theme", (_, theme) => {
  const state = readState()
  writeState({ ...state, theme })
})

function sendStatus(text) {
  if (splashWindow) {
    splashWindow.webContents.send("status", text)
  }
}

async function startDocker() {
  sendStatus("Checking Docker installation")
  await run("docker --version")

  sendStatus("Starting containers")
  await run(`docker compose -f "${dockerComposePath}" up -d`)

  sendStatus("Waiting for backend API")
  await waitForHealth("http://localhost:8000/health")
}

function createSplashWindow() {
  const { theme = "light" } = readState()

  splashWindow = new BrowserWindow({
    fullscreen: false,
    frame: true,
    resizable: false,
    alwaysOnTop: true,
    webPreferences: {
      preload: path.join(__dirname, "splash.js"),
      contextIsolation: true,
    },
  })

  splashWindow.loadFile(
    path.join(projectRoot, "electron", "splash.html"),
    { query: { theme } }
  )
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, "rendererBridge.js"),
      contextIsolation: true,
    },
  })

  mainWindow.loadFile(
    path.join(projectRoot, "frontend", "dist", "index.html")
  )

  globalShortcut.register("CommandOrControl+R", () => {
    mainWindow.reload()
  })
}

app.whenReady().then(async () => {
  createSplashWindow()

  try {
    await startDocker()

    splashWindow.close()
    splashWindow = null

    createMainWindow()
  } catch (e) {
    dialog.showErrorBox("Startup failed", String(e))
    app.quit()
  }
})

app.on("before-quit", async () => {
  try {
    await run(`docker compose -f "${dockerComposePath}" down`)
  } catch {}
})
