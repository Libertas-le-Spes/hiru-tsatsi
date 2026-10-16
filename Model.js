function defaultConfig() {
  return { workspaces: [] }
}

function fromSaved(space) {
  return {
    id: Number(space.number),
    label: String(space.label || ""),
    apps: (space.apps || []).map(function(app) {
      return { name: String(app.name), cmd: String(app.command), window: String(app.learned_window || "") }
    })
  }
}

function toSaved(space) {
  return {
    number: space.id,
    label: space.label,
    apps: space.apps.map(function(app) {
      return { name: app.name, command: app.cmd, learned_window: app.window || "" }
    })
  }
}

function parseConfig(text) {
  try {
    var parsed = JSON.parse(String(text || ""))
    if (!parsed || !Array.isArray(parsed.workspaces)) return defaultConfig()
    return { workspaces: parsed.workspaces.map(fromSaved) }
  } catch (e) {
    return defaultConfig()
  }
}

function serializeConfig(config) {
  return JSON.stringify({ workspaces: config.workspaces.map(toSaved) }, null, 2) + "\n"
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

function hasWorkspace(config, workspaceId) {
  return config.workspaces.some(function(w) { return w.id === workspaceId })
}

function addWorkspace(config, workspaceId, label) {
  if (workspaceId < 1 || hasWorkspace(config, workspaceId)) return config
  var next = cloneConfig(config)
  next.workspaces.push({ id: workspaceId, label: label || "Workspace", apps: [] })
  next.workspaces.sort(function(a, b) { return a.id - b.id })
  return next
}

function removeWorkspace(config, workspaceId) {
  var next = cloneConfig(config)
  next.workspaces = next.workspaces.filter(function(w) { return w.id !== workspaceId })
  return next
}

function addApp(config, workspaceId, name, cmd) {
  var next = cloneConfig(config)
  for (var i = 0; i < next.workspaces.length; i++) {
    if (next.workspaces[i].id === workspaceId) {
      next.workspaces[i].apps.push({ name: name, cmd: cmd, window: "" })
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

function hasAnyApps(config) {
  for (var i = 0; i < config.workspaces.length; i++) {
    if (config.workspaces[i].apps.length > 0) return true
  }
  return false
}

if (typeof module !== "undefined") {
  module.exports = {
    defaultConfig: defaultConfig,
    parseConfig: parseConfig,
    serializeConfig: serializeConfig,
    nextWorkspaceId: nextWorkspaceId,
    hasWorkspace: hasWorkspace,
    addWorkspace: addWorkspace,
    removeWorkspace: removeWorkspace,
    addApp: addApp,
    removeApp: removeApp,
    hasAnyApps: hasAnyApps
  }
}
