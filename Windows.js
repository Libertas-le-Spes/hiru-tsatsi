function parse(json) {
  try {
    var windows = JSON.parse(json)
    return Array.isArray(windows) ? windows : []
  } catch (e) {
    return []
  }
}

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

function wordsOf(text) {
  return String(text || "").toLowerCase().split(/[\s"'\/~?&=]+/).filter(function(word) { return word.length >= 4 })
}

function telltaleWords(cmd) {
  var parts = String(cmd || "").trim().split(/\s+/)
  var argumentWords = wordsOf(parts.slice(1).join(" "))
  return argumentWords.length > 0 ? argumentWords : wordsOf(parts[0])
}

function mentionStrength(window, word) {
  var text = (String(window.class || "") + " " + String(window.title || "")).toLowerCase()
  if (text.indexOf(word) === -1) return 0
  var leads = startsWith(window.class, word) || startsWith(window.title, word)
  return word.length * 2 + (leads ? 1 : 0)
}

function strongestMention(window, words) {
  var strongest = 0
  for (var i = 0; i < words.length; i++) strongest = Math.max(strongest, mentionStrength(window, words[i]))
  return strongest
}

function guessWindow(cmd, windows) {
  var words = telltaleWords(cmd)
  var best = null
  var bestStrength = 0
  var tied = false
  for (var i = 0; i < windows.length; i++) {
    var strength = strongestMention(windows[i], words)
    if (strength > bestStrength) {
      best = windows[i]
      bestStrength = strength
      tied = false
    } else if (strength > 0 && strength === bestStrength) {
      tied = true
    }
  }
  return tied ? null : best
}

function titleStart(title) {
  return String(title || "").split(/ [–—·|-] /)[0].trim()
}

function sharesClass(window, windows) {
  return windows.filter(function(other) { return other.class === window.class }).length > 1
}

function classTells(window, windows, cmd) {
  if (sharesClass(window, windows)) return false
  var windowClass = String(window.class || "").toLowerCase()
  var words = telltaleWords(cmd)
  return words.length === 0 || words.some(function(word) { return windowClass.indexOf(word) !== -1 })
}

function nameFor(window, windows, cmd) {
  var title = titleStart(window.title)
  return classTells(window, windows, cmd) || title === "" ? String(window.class || "") : title
}

function choicesFor(windows) {
  return windows.map(function(window) {
    return { value: nameFor(window, windows), label: String(window.title || window.class), description: String(window.class || "") }
  })
}

if (typeof module !== "undefined") {
  module.exports = {
    parse: parse,
    canFind: canFind,
    belongsTo: belongsTo,
    windowOf: windowOf,
    guessWindow: guessWindow,
    nameFor: nameFor,
    choicesFor: choicesFor
  }
}
