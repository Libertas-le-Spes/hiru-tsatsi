function startsWith(text, prefix) {
  return String(text || "").toLowerCase().indexOf(prefix) === 0
}

function windowName(job) {
  return String(job.window || "").trim().toLowerCase()
}

function canFind(job) {
  return windowName(job) !== ""
}

function belongsTo(window, job) {
  var prefix = windowName(job)
  if (prefix === "") return false
  return startsWith(window.class, prefix) || startsWith(window.title, prefix)
}

function windowOf(job, windows, claimed) {
  for (var i = 0; i < windows.length; i++) {
    if (!claimed[windows[i].address] && belongsTo(windows[i], job)) return windows[i]
  }
  return null
}

if (typeof module !== "undefined") {
  module.exports = {
    canFind: canFind,
    belongsTo: belongsTo,
    windowOf: windowOf
  }
}
