function defaultConfig() {
  return { workspaces: [] }
}

function fromSaved(space) {
  return {
    id: Number(space.number),
    label: String(space.label || ""),
    apps: (space.apps || []).map(function(app) { return { name: String(app.name) } })
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

function hasAnyApps(config) {
  return config.workspaces.some(function(space) { return space.apps.length > 0 })
}

if (typeof module !== "undefined") {
  module.exports = {
    defaultConfig: defaultConfig,
    parseConfig: parseConfig,
    hasAnyApps: hasAnyApps
  }
}
