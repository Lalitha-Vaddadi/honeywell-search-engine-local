const fs = require("fs")
const path = require("path")

const statePath = path.join(__dirname, "state.json")

function readState() {
  try {
    return JSON.parse(fs.readFileSync(statePath, "utf-8"))
  } catch {
    return {}
  }
}

function writeState(state) {
  fs.writeFileSync(statePath, JSON.stringify(state, null, 2))
}

module.exports = { readState, writeState }
