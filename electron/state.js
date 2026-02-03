const fs = require("fs")
const path = require("path")
const { app } = require("electron")

function ensureStateDir() {
  const userDataPath = app.getPath("userData")
  fs.mkdirSync(userDataPath, { recursive: true })
  return userDataPath
}

function getStatePath() {
  return path.join(ensureStateDir(), "state.json")
}

function readState() {
  try {
    return JSON.parse(fs.readFileSync(getStatePath(), "utf-8"))
  } catch {
    return {}
  }
}

function writeState(state) {
  fs.writeFileSync(getStatePath(), JSON.stringify(state, null, 2))
}

module.exports = { readState, writeState }
