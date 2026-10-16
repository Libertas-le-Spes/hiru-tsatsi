import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import qs.Ui
import qs.Commons
import "Model.js" as Model
import "Strings.js" as Strings

Panel {
  id: root
  moduleName: "io.github.diegovrocha.omastart"
  ipcTarget: "io.github.diegovrocha.omastart"

  // Follows the machine's configured language (Qt.locale()), not whatever
  // language the user happens to be typing in - those can differ.
  readonly property var s: Strings.forLocale(Qt.locale().name)

  readonly property string configPath: Quickshell.env("HOME") + "/.local/state/omarchy/settings/omastart.json"
  // Id of the last boot the startup prompt was shown for, persisted to disk
  // so it survives shell restarts - promptedThisSession used to be an
  // in-memory flag, which meant "once per session" was really "every time
  // the shell process restarts" since the process itself is short-lived.
  // This used to track by calendar date instead of boot id, which meant a
  // same-day reboot never re-prompted, since "today" was already recorded
  // from before the reboot.
  readonly property string promptStatePath: Quickshell.env("HOME") + "/.local/state/omarchy/settings/omastart_last_prompt.txt"
  readonly property string bootIdPath: "/proc/sys/kernel/random/boot_id"
  property string currentBootId: ""
  property bool bootIdLoaded: false
  property bool promptStateLoaded: false
  property var config: Model.defaultConfig()
  property string newWorkspaceLabel: ""

  function maybePromptForBoot(lastPromptedBootId) {
    if (!root.bootIdLoaded || !root.promptStateLoaded) return
    if (lastPromptedBootId.trim() !== root.currentBootId.trim()) {
      promptStateFile.setText(root.currentBootId)
      Qt.callLater(root.open)
    }
  }

  function saveConfig() {
    configFile.setText(Model.serializeConfig(root.config))
  }

  function launchAll() {
    launcher.start(Model.launchPlan(root.config))
    root.close()
  }

  function addWorkspace() {
    var label = root.newWorkspaceLabel.trim()
    if (label.length === 0) return
    root.config = Model.addWorkspace(root.config, label)
    root.newWorkspaceLabel = ""
    root.saveConfig()
  }

  function removeWorkspace(workspaceId) {
    root.config = Model.removeWorkspace(root.config, workspaceId)
    root.saveConfig()
  }

  function addApp(workspaceId, name, cmd, window) {
    if (name.trim().length === 0 || cmd.trim().length === 0) return false
    root.config = Model.addApp(root.config, workspaceId, name.trim(), cmd.trim(), window.trim())
    root.saveConfig()
    return true
  }

  function setAppWindow(workspaceId, appIndex, window) {
    root.config = Model.setAppWindow(root.config, workspaceId, appIndex, window.trim())
    root.saveConfig()
  }

  function removeApp(workspaceId, appIndex) {
    root.config = Model.removeApp(root.config, workspaceId, appIndex)
    root.saveConfig()
  }

  Launcher {
    id: launcher
    onWindowLearned: function(job, name) { root.setAppWindow(job.workspaceId, job.appIndex, name) }
  }

  OpenWindows {
    id: openWindows
  }

  onOpenedChanged: if (root.opened) openWindows.refresh()

  FileView {
    id: configFile
    path: root.configPath
    watchChanges: true
    atomicWrites: true
    printErrors: false
    onLoaded: root.config = Model.parseConfig(text())
    onLoadFailed: {
      root.config = Model.defaultConfig()
      root.saveConfig()
    }
  }

  FileView {
    id: bootIdFile
    path: root.bootIdPath
    watchChanges: false
    printErrors: false
    onLoaded: {
      root.currentBootId = text()
      root.bootIdLoaded = true
      root.maybePromptForBoot(promptStateFile.text())
    }
    onLoadFailed: {
      root.bootIdLoaded = true
      root.maybePromptForBoot(promptStateFile.text())
    }
  }

  FileView {
    id: promptStateFile
    path: root.promptStatePath
    watchChanges: false
    atomicWrites: true
    printErrors: false
    onLoaded: {
      root.promptStateLoaded = true
      root.maybePromptForBoot(text())
    }
    onLoadFailed: {
      root.promptStateLoaded = true
      root.maybePromptForBoot("")
    }
  }

  visible: true
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  // Filled lightning bolt once at least one app is configured somewhere;
  // outline while empty. Nerd Font (Material Design Icons) glyphs, not
  // emoji, so the glyph follows bar.barForeground like every other icon -
  // emoji ignore the color property and always render in their own fixed
  // colors.
  readonly property bool hasAnyApps: Model.hasAnyApps(root.config)

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.hasAnyApps ? "󱐋" : "󱐌"
    active: launcher.busy
    onPressed: root.toggle()
  }

  KeyboardPanel {
    id: panel
    anchorItem: button
    owner: root
    bar: root.bar
    open: root.opened
    focusTarget: keyCatcher
    contentWidth: panel.fittedContentWidth(Style.space(400))
    contentHeight: panel.fittedContentHeight(column.implicitHeight, Style.space(560))

    PanelKeyCatcher {
      id: keyCatcher
      anchors.fill: parent
      onCloseRequested: root.close()

      Column {
        id: column
        anchors.fill: parent
        spacing: Style.space(14)

        Column {
          width: parent.width
          spacing: Style.space(8)

          Text {
            text: root.s.title
            color: root.bar.foreground
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.title
            font.bold: true
          }

          Text {
            text: root.s.subtitle
            color: Qt.darker(root.bar.foreground, 1.5)
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.bodySmall
            wrapMode: Text.WordWrap
            width: parent.width
          }

          Button {
            text: launcher.busy ? root.s.startingButton : root.s.startButton
            enabled: !launcher.busy
            foreground: root.bar.foreground
            bordered: true
            onClicked: root.launchAll()
          }
        }

        PanelSeparator {
          foreground: root.bar.foreground
        }

        PanelSectionHeader {
          text: root.s.workspacesHeader
          foreground: root.bar.foreground
          fontFamily: root.bar.fontFamily
        }

        ListView {
          id: wsList
          width: parent.width
          height: Math.min(contentHeight, Style.space(320))
          spacing: Style.space(14)
          clip: true
          interactive: contentHeight > height
          model: root.config.workspaces

          delegate: Column {
            id: wsBlock
            required property var modelData
            width: wsList.width
            spacing: Style.space(6)

            function addApp() {
              var window = appWindowPicker.value || openWindows.guessName(appCmdField.text)
              if (!root.addApp(wsBlock.modelData.id, appNameField.text, appCmdField.text, window)) return
              appNameField.text = ""
              appCmdField.text = ""
              appWindowPicker.value = ""
            }

            Row {
              width: parent.width
              spacing: Style.space(8)

              Text {
                anchors.verticalCenter: parent.verticalCenter
                text: root.s.workspaceLabel + " " + wsBlock.modelData.id + " — " + wsBlock.modelData.label
                color: root.bar.foreground
                font.family: root.bar.fontFamily
                font.pixelSize: Style.font.body
                font.bold: true
              }

              PanelActionButton {
                anchors.verticalCenter: parent.verticalCenter
                iconText: "✕"
                tooltipText: root.s.removeWorkspaceTip
                foreground: root.bar.foreground
                hoverColor: root.bar.foreground
                fontFamily: root.bar.fontFamily
                onClicked: root.removeWorkspace(wsBlock.modelData.id)
              }
            }

            Repeater {
              model: wsBlock.modelData.apps
              delegate: Row {
                required property var modelData
                required property int index
                spacing: Style.space(8)

                Text {
                  anchors.verticalCenter: parent.verticalCenter
                  text: "• " + modelData.name + "  (" + modelData.cmd + ")"
                  color: Qt.darker(root.bar.foreground, 1.3)
                  font.family: root.bar.fontFamily
                  font.pixelSize: Style.font.bodySmall
                  elide: Text.ElideRight
                  width: Style.space(170)
                }

                SearchableDropdown {
                  anchors.verticalCenter: parent.verticalCenter
                  width: Style.space(110)
                  showLabel: false
                  value: modelData.window || ""
                  options: openWindows.choices
                  placeholderText: root.s.windowPlaceholder
                  emptyText: root.s.noWindowsText
                  fontFamily: root.bar.fontFamily
                  onChanged: function(window) { root.setAppWindow(wsBlock.modelData.id, index, window) }
                }

                PanelActionButton {
                  anchors.verticalCenter: parent.verticalCenter
                  iconText: "✕"
                  tooltipText: root.s.removeAppTip
                  foreground: root.bar.foreground
                  hoverColor: root.bar.foreground
                  fontFamily: root.bar.fontFamily
                  size: Style.space(16)
                  onClicked: root.removeApp(wsBlock.modelData.id, index)
                }
              }
            }

            Row {
              width: parent.width
              spacing: Style.space(6)

              TextField {
                id: appNameField
                width: Style.space(80)
                placeholderText: root.s.namePlaceholder
                foreground: root.bar.foreground
                verticalPadding: Style.space(4)
              }

              TextField {
                id: appCmdField
                width: Style.space(110)
                placeholderText: root.s.commandPlaceholder
                foreground: root.bar.foreground
                verticalPadding: Style.space(4)
                onEditingFinished: if (appWindowPicker.value === "") appWindowPicker.value = openWindows.guessName(text)
                onAccepted: wsBlock.addApp()
              }

              SearchableDropdown {
                id: appWindowPicker
                width: Style.space(110)
                showLabel: false
                options: openWindows.choices
                placeholderText: root.s.windowPlaceholder
                emptyText: root.s.noWindowsText
                fontFamily: root.bar.fontFamily
              }

              PanelActionButton {
                iconText: "+"
                tooltipText: root.s.addAppTip
                foreground: root.bar.foreground
                hoverColor: root.bar.foreground
                fontFamily: root.bar.fontFamily
                onClicked: wsBlock.addApp()
              }
            }
          }
        }

        PanelSeparator {
          foreground: root.bar.foreground
        }

        Row {
          width: parent.width
          spacing: Style.space(6)

          TextField {
            id: wsLabelField
            width: Style.space(240)
            placeholderText: root.s.newWorkspacePlaceholder
            foreground: root.bar.foreground
            onAccepted: {
              root.newWorkspaceLabel = text
              root.addWorkspace()
              text = ""
            }
          }

          Button {
            text: root.s.addWorkspaceButton
            foreground: root.bar.foreground
            bordered: true
            onClicked: {
              root.newWorkspaceLabel = wsLabelField.text
              root.addWorkspace()
              wsLabelField.text = ""
            }
          }
        }
      }
    }
  }
}
