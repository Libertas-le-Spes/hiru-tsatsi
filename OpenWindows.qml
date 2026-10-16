import QtQuick
import Quickshell.Io
import "Windows.js" as Windows

Item {
  id: openWindows

  property var windows: []
  readonly property var choices: Windows.choicesFor(windows)

  function refresh() {
    if (!clientsProc.running) clientsProc.running = true
  }

  function guessName(cmd) {
    var window = Windows.guessWindow(cmd, openWindows.windows)
    return window ? Windows.nameFor(window, openWindows.windows, cmd) : ""
  }

  Process {
    id: clientsProc
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: openWindows.windows = Windows.parse(text)
    }
  }
}
