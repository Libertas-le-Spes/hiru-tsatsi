function defaultConfig() {
  return {
    workspaces: [
      { id: 1, label: "Browser", apps: [{ name: "Chromium", cmd: "chromium" }] },
      { id: 2, label: "Herdr", apps: [{ name: "Herdr", cmd: "omarchy-launch-terminal-herdr" }] },
      { id: 3, label: "Editor", apps: [{ name: "VS Code", cmd: "code" }] },
      {
        id: 4,
        label: "Comms",
        apps: [
          { name: "WhatsApp", cmd: "omarchy-launch-webapp https://web.whatsapp.com/" },
          { name: "Teams", cmd: "teams-for-linux --gtk-version=3" }
        ]
      },
      { id: 5, label: "Database", apps: [{ name: "DBeaver", cmd: "env GTK_THEME=Adwaita:light dbeaver" }] }
    ]
  }
}

function parseConfig(text) {
  var trimmed = String(text || "").trim()
  if (trimmed === "") return defaultConfig()
  try {
    var parsed = JSON.parse(trimmed)
    if (!parsed || !Array.isArray(parsed.workspaces)) return defaultConfig()
    return parsed
  } catch (e) {
    return defaultConfig()
  }
}

function serializeConfig(config) {
  return JSON.stringify(config, null, 2) + "\n"
}

function cloneConfig(config) {
  return JSON.parse(JSON.stringify(config))
}

function nextWorkspaceId(config) {
  var max = 0
  for (var i = 0; i < config.workspaces.length; i++) {
    if (config.workspaces[i].id > max) max = config.workspaces[i].id
  }
  return max + 1
}

function addWorkspace(config, label) {
  var next = cloneConfig(config)
  next.workspaces.push({ id: nextWorkspaceId(config), label: label || "Workspace", apps: [] })
  return next
}

function removeWorkspace(config, workspaceId) {
  var next = cloneConfig(config)
  next.workspaces = next.workspaces.filter(function(w) { return w.id !== workspaceId })
  return next
}

function addApp(config, workspaceId, name, cmd, window) {
  var next = cloneConfig(config)
  for (var i = 0; i < next.workspaces.length; i++) {
    if (next.workspaces[i].id === workspaceId) {
      next.workspaces[i].apps.push({ name: name, cmd: cmd, window: window })
      break
    }
  }
  return next
}

function setAppWindow(config, workspaceId, appIndex, window) {
  var next = cloneConfig(config)
  for (var i = 0; i < next.workspaces.length; i++) {
    if (next.workspaces[i].id === workspaceId) {
      next.workspaces[i].apps[appIndex].window = window
      break
    }
  }
  return next
}

function removeApp(config, workspaceId, appIndex) {
  var next = cloneConfig(config)
  for (var i = 0; i < next.workspaces.length; i++) {
    if (next.workspaces[i].id === workspaceId) {
      next.workspaces[i].apps.splice(appIndex, 1)
      break
    }
  }
  return next
}

// Escapes a shell command for embedding inside a Lua double-quoted string
// literal passed to `hyprctl dispatch`.
function luaQuote(str) {
  return String(str).replace(/\\/g, "\\\\").replace(/"/g, '\\"')
}

function dispatchArg(cmd, workspaceId) {
  return 'hl.dsp.exec_cmd("' + luaQuote(cmd) + '", { workspace = "' + workspaceId + ' silent" })'
}

function moveArg(address, workspaceId) {
  return 'hl.dsp.window.move({ workspace = "' + workspaceId + '", follow = false, window = "address:' + luaQuote(address) + '" })'
}

// Flat list of {workspaceId, cmd} launch jobs for every app in every
// workspace, in workspace order - what the "start work apps" action fires.
function hasAnyApps(config) {
  for (var i = 0; i < config.workspaces.length; i++) {
    if (config.workspaces[i].apps.length > 0) return true
  }
  return false
}

function launchPlan(config) {
  var plan = []
  for (var i = 0; i < config.workspaces.length; i++) {
    var ws = config.workspaces[i]
    for (var j = 0; j < ws.apps.length; j++) {
      plan.push({ workspaceId: ws.id, cmd: ws.apps[j].cmd, window: ws.apps[j].window || "" })
    }
  }
  return plan
}

if (typeof module !== "undefined") {
  module.exports = {
    defaultConfig: defaultConfig,
    parseConfig: parseConfig,
    serializeConfig: serializeConfig,
    cloneConfig: cloneConfig,
    nextWorkspaceId: nextWorkspaceId,
    addWorkspace: addWorkspace,
    removeWorkspace: removeWorkspace,
    addApp: addApp,
    setAppWindow: setAppWindow,
    removeApp: removeApp,
    hasAnyApps: hasAnyApps,
    luaQuote: luaQuote,
    dispatchArg: dispatchArg,
    moveArg: moveArg,
    launchPlan: launchPlan
  }
}
