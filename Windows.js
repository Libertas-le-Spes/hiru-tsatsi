function startsWith(text, prefix) {
  return String(text || "").toLowerCase().indexOf(prefix) === 0
}

function belongsTo(window, pattern) {
  var prefix = String(pattern || "").trim().toLowerCase()
  if (prefix === "") return false
  return startsWith(window.class, prefix) || startsWith(window.title, prefix)
}

function firstUnclaimed(windows, claimed, accepts) {
  for (var i = 0; i < windows.length; i++) {
    if (!claimed[windows[i].address] && accepts(windows[i])) return windows[i]
  }
  return null
}

function alreadyOpen(job, windows, claimed) {
  return firstUnclaimed(windows, claimed, function(w) { return belongsTo(w, job.window) })
}

function launchedWindow(job, windows, claimed, addressesBeforeLaunch) {
  if (String(job.window || "").trim() !== "") return alreadyOpen(job, windows, claimed)
  return firstUnclaimed(windows, claimed, function(w) {
    return !addressesBeforeLaunch[w.address] && !w.floating
  })
}

if (typeof module !== "undefined") {
  module.exports = {
    belongsTo: belongsTo,
    alreadyOpen: alreadyOpen,
    launchedWindow: launchedWindow
  }
}
