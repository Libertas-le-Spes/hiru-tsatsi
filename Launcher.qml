import QtQuick
import Quickshell
import Quickshell.Io
import "Model.js" as Model
import "Windows.js" as Windows

Item {
  id: launcher

  property int windowTimeoutMs: 60000
  property var plan: []
  property var awaiting: []
  property var claimed: ({})
  property var knownBefore: ({})
  property real launchedAt: 0
  property bool reading: false
  readonly property bool busy: reading || awaiting.length > 0

  signal windowLearned(var job, string name)

  function start(newPlan) {
    if (launcher.busy || newPlan.length === 0) return
    launcher.reading = true
    launcher.plan = newPlan
    launcher.claimed = {}
    openWindowsProc.running = true
  }

  function claim(window, workspaceId) {
    launcher.claimed[window.address] = true
    if (window.workspace && window.workspace.id === workspaceId) return
    Quickshell.execDetached(["hyprctl", "dispatch", Model.moveArg(window.address, workspaceId)])
  }

  function unclaimedNew(windows) {
    return windows.filter(function(window) {
      return !launcher.knownBefore[window.address] && !launcher.claimed[window.address]
    })
  }

  function findWindow(job, windows) {
    if (Windows.canFind(job)) return Windows.windowOf(job, windows, launcher.claimed)
    var guessed = Windows.guessWindow(job.cmd, launcher.unclaimedNew(windows))
    if (guessed) launcher.windowLearned(job, Windows.nameFor(guessed, windows, job.cmd))
    return guessed
  }

  function namedFirst(jobs) {
    return jobs.filter(Windows.canFind).concat(jobs.filter(function(job) { return !Windows.canFind(job) }))
  }

  function placeWindowsOf(jobs, windows) {
    var ordered = launcher.namedFirst(jobs)
    var unplaced = []
    for (var i = 0; i < ordered.length; i++) {
      var window = launcher.findWindow(ordered[i], windows)
      if (window) launcher.claim(window, ordered[i].workspaceId)
      else unplaced.push(ordered[i])
    }
    return unplaced
  }

  function remember(windows) {
    var known = {}
    for (var i = 0; i < windows.length; i++) known[windows[i].address] = true
    launcher.knownBefore = known
  }

  function launchMissing(json) {
    var windows = Windows.parse(json)
    launcher.remember(windows)
    var missing = launcher.placeWindowsOf(launcher.plan, windows)
    for (var i = 0; i < missing.length; i++) {
      Quickshell.execDetached(["hyprctl", "dispatch", Model.dispatchArg(missing[i].cmd, missing[i].workspaceId)])
    }
    launcher.launchedAt = Date.now()
    launcher.awaiting = missing
    launcher.reading = false
    if (launcher.awaiting.length > 0) pollTimer.start()
  }

  function placeArrivals(json) {
    var stillAwaiting = launcher.placeWindowsOf(launcher.awaiting, Windows.parse(json))
    var timedOut = Date.now() - launcher.launchedAt > launcher.windowTimeoutMs
    launcher.awaiting = timedOut ? [] : stillAwaiting
    if (launcher.awaiting.length === 0) pollTimer.stop()
  }

  Process {
    id: openWindowsProc
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: launcher.launchMissing(text)
    }
  }

  Process {
    id: pollProc
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: launcher.placeArrivals(text)
    }
  }

  Timer {
    id: pollTimer
    interval: 500
    repeat: true
    onTriggered: if (!pollProc.running) pollProc.running = true
  }
}
