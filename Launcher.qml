import QtQuick
import Quickshell
import Quickshell.Io
import "Model.js" as Model
import "Windows.js" as Windows

Item {
  id: launcher

  property int windowTimeoutMs: 60000
  property var plan: []
  property var pending: []
  property var current: null
  property var claimed: ({})
  property var addressesBeforeLaunch: ({})
  property real launchedAt: 0
  property bool starting: false
  readonly property bool busy: starting || current !== null

  function start(newPlan) {
    if (launcher.busy || newPlan.length === 0) return
    launcher.starting = true
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

  function placeOpenAppsAndQueueTheRest(json) {
    var windows = launcher.readWindows(json)
    var toLaunch = []
    for (var i = 0; i < launcher.plan.length; i++) {
      var job = launcher.plan[i]
      var open = Windows.alreadyOpen(job, windows, launcher.claimed)
      if (open) launcher.claim(open, job.workspaceId)
      else toLaunch.push(job)
    }
    launcher.pending = toLaunch
    launcher.launchNext()
    launcher.starting = false
  }

  function launchNext() {
    if (launcher.pending.length === 0) {
      launcher.current = null
      return
    }
    launcher.current = launcher.pending[0]
    launcher.pending = launcher.pending.slice(1)
    snapshotProc.running = true
  }

  function launchCurrent(json) {
    var known = {}
    var windows = launcher.readWindows(json)
    for (var i = 0; i < windows.length; i++) known[windows[i].address] = true
    launcher.addressesBeforeLaunch = known
    launcher.launchedAt = Date.now()
    Quickshell.execDetached(["hyprctl", "dispatch", Model.dispatchArg(launcher.current.cmd, launcher.current.workspaceId)])
    pollTimer.start()
  }

  function claimLaunchedWindow(json) {
    var windows = launcher.readWindows(json)
    var launched = Windows.launchedWindow(launcher.current, windows, launcher.claimed, launcher.addressesBeforeLaunch)
    if (launched) launcher.claim(launched, launcher.current.workspaceId)
    if (launched || Date.now() - launcher.launchedAt > launcher.windowTimeoutMs) {
      pollTimer.stop()
      launcher.launchNext()
    }
  }

  Process {
    id: openWindowsProc
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: launcher.placeOpenAppsAndQueueTheRest(text)
    }
  }

  Process {
    id: snapshotProc
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: launcher.launchCurrent(text)
    }
  }

  Process {
    id: pollProc
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: launcher.claimLaunchedWindow(text)
    }
  }

  Timer {
    id: pollTimer
    interval: 500
    repeat: true
    onTriggered: if (!pollProc.running) pollProc.running = true
  }
}
