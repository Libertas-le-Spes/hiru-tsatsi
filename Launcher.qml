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
  property real launchedAt: 0
  property bool reading: false
  readonly property bool busy: reading || awaiting.length > 0

  function start(newPlan) {
    if (launcher.busy || newPlan.length === 0) return
    launcher.reading = true
    launcher.plan = newPlan
    launcher.claimed = {}
    openWindowsProc.running = true
  }

  function readWindows(json) {
    try {
      return JSON.parse(json)
    } catch (e) {
      return []
    }
  }

  function claim(window, workspaceId) {
    launcher.claimed[window.address] = true
    if (window.workspace && window.workspace.id === workspaceId) return
    Quickshell.execDetached(["hyprctl", "dispatch", Model.moveArg(window.address, workspaceId)])
  }

  function placeWindowsOf(jobs, json) {
    var windows = launcher.readWindows(json)
    var unplaced = []
    for (var i = 0; i < jobs.length; i++) {
      var window = Windows.windowOf(jobs[i], windows, launcher.claimed)
      if (window) launcher.claim(window, jobs[i].workspaceId)
      else unplaced.push(jobs[i])
    }
    return unplaced
  }

  function launchMissing(json) {
    var missing = launcher.placeWindowsOf(launcher.plan, json)
    for (var i = 0; i < missing.length; i++) {
      Quickshell.execDetached(["hyprctl", "dispatch", Model.dispatchArg(missing[i].cmd, missing[i].workspaceId)])
    }
    launcher.launchedAt = Date.now()
    launcher.awaiting = missing.filter(Windows.canFind)
    launcher.reading = false
    if (launcher.awaiting.length > 0) pollTimer.start()
  }

  function placeArrivals(json) {
    var stillAwaiting = launcher.placeWindowsOf(launcher.awaiting, json)
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
