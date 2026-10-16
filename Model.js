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

function parseConfig(text) {
  try {
    var parsed = JSON.parse(String(text || ""))
    if (!parsed || !Array.isArray(parsed.workspaces)) return defaultConfig()
    return { workspaces: parsed.workspaces.map(fromSaved) }
  } catch (e) {
    return defaultConfig()
  }
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
    nextWorkspaceId: nextWorkspaceId,
    hasWorkspace: hasWorkspace,
    hasAnyApps: hasAnyApps
  }
}
