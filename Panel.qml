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
  moduleName: "kayu.hiru-tsatsi"
  ipcTarget: "kayu.hiru-tsatsi"

  // Follows the machine's configured language (Qt.locale()), not whatever
  // language the user happens to be typing in - those can differ.
  readonly property var s: Strings.forLocale(Qt.locale().name)

  readonly property string hiruTsatsiCommand: Qt.resolvedUrl("backend/bin/hiru-tsatsi").toString().replace("file://", "")
  readonly property bool starting: hiruTsatsiStart.running
  property var config: Model.defaultConfig()
  property string newWorkspaceLabel: ""
  property int newWorkspaceId: Model.nextWorkspaceId(root.config)
  readonly property bool newWorkspaceIdTaken: Model.hasWorkspace(root.config, root.newWorkspaceId)

  property var pendingEdits: []
  property string editProblem: ""
  property string choosingFor: ""
  property var windowChoices: []

  onConfigChanged: if (root.newWorkspaceIdTaken) root.newWorkspaceId = Model.nextWorkspaceId(root.config)
  onOpenedChanged: if (root.opened) root.refresh()
  Component.onCompleted: root.refresh()

  function refresh() {
    if (!overviewProc.running) overviewProc.running = true
  }

  function chooseWindowFor(workspaceId, appIndex) {
    var key = workspaceId + "/" + appIndex
    root.windowChoices = []
    root.choosingFor = root.choosingFor === key ? "" : key
    if (root.choosingFor === "") return
    windowsProc.command = [root.hiruTsatsiCommand, "windows-for", String(workspaceId), String(appIndex)]
    windowsProc.running = true
  }

  function pickWindow(workspaceId, appIndex, address) {
    root.choosingFor = ""
    root.change(["choose-window", String(workspaceId), String(appIndex), address])
  }

  function forgetWindow(workspaceId, appIndex) {
    root.choosingFor = ""
    root.change(["forget-window", String(workspaceId), String(appIndex)])
  }

  function launchAll() {
    if (!hiruTsatsiStart.running) hiruTsatsiStart.running = true
    root.close()
  }

  function change(edit) {
    root.pendingEdits = root.pendingEdits.concat([edit])
    root.runNextEdit()
  }

  function runNextEdit() {
    if (hiruTsatsiEdit.running || root.pendingEdits.length === 0) return
    hiruTsatsiEdit.command = [root.hiruTsatsiCommand].concat(root.pendingEdits[0])
    root.pendingEdits = root.pendingEdits.slice(1)
    root.editProblem = ""
    hiruTsatsiEdit.running = true
  }

  function addWorkspace() {
    var label = root.newWorkspaceLabel.trim()
    if (label.length === 0 || root.newWorkspaceIdTaken) return false
    root.change(["add-workspace", String(root.newWorkspaceId), label])
    root.newWorkspaceLabel = ""
    return true
  }

  function removeWorkspace(workspaceId) {
    root.change(["remove-workspace", String(workspaceId)])
  }

  function addApp(workspaceId, name, cmd) {
    if (name.trim().length === 0 || cmd.trim().length === 0) return false
    root.change(["add-app", String(workspaceId), name.trim(), cmd.trim()])
    return true
  }

  function removeApp(workspaceId, appIndex) {
    root.change(["remove-app", String(workspaceId), String(appIndex)])
  }

  Process {
    id: hiruTsatsiEdit
    stderr: StdioCollector {
      waitForEnd: true
      onStreamFinished: if (text.trim() !== "") root.editProblem = text.trim()
    }
    onExited: {
      root.refresh()
      root.runNextEdit()
    }
  }

  Process {
    id: hiruTsatsiStart
    command: [root.hiruTsatsiCommand, "start"]
    onExited: root.refresh()
  }

  Process {
    id: overviewProc
    command: [root.hiruTsatsiCommand, "overview"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: if (text.trim() !== "") root.config = Model.parseConfig(text)
    }
  }

  Process {
    id: windowsProc
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        try {
          root.windowChoices = JSON.parse(text)
        } catch (e) {
          root.windowChoices = []
        }
      }
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
    active: root.starting
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
            textFormat: Text.PlainText
            text: root.s.title
            color: root.bar.foreground
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.title
            font.bold: true
          }

          Text {
            textFormat: Text.PlainText
            text: root.s.subtitle
            color: Qt.darker(root.bar.foreground, 1.5)
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.bodySmall
            wrapMode: Text.WordWrap
            width: parent.width
          }

          Button {
            text: root.starting ? root.s.startingButton : root.s.startButton
            enabled: !root.starting
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
              if (!root.addApp(wsBlock.modelData.id, appNameField.text, appCmdField.text)) return
              appNameField.text = ""
              appCmdField.text = ""
            }

            Row {
              width: parent.width
              spacing: Style.space(8)

              Text {
                textFormat: Text.PlainText
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
                enabled: !hiruTsatsiEdit.running
                onClicked: root.removeWorkspace(wsBlock.modelData.id)
              }
            }

            Repeater {
              model: wsBlock.modelData.apps
              delegate: Column {
                id: appBlock
                required property var modelData
                required property int index
                readonly property bool choosing: root.choosingFor === wsBlock.modelData.id + "/" + appBlock.index
                spacing: Style.space(2)

                Row {
                  spacing: Style.space(8)

                  Text {
                    textFormat: Text.PlainText
                    anchors.verticalCenter: parent.verticalCenter
                    text: "• " + appBlock.modelData.name + "  (" + appBlock.modelData.cmd + ")"
                    color: Qt.darker(root.bar.foreground, 1.3)
                    font.family: root.bar.fontFamily
                    font.pixelSize: Style.font.bodySmall
                    elide: Text.ElideRight
                    width: Style.space(280)
                  }

                  PanelActionButton {
                    anchors.verticalCenter: parent.verticalCenter
                    iconText: "✕"
                    tooltipText: root.s.removeAppTip
                    foreground: root.bar.foreground
                    hoverColor: root.bar.foreground
                    fontFamily: root.bar.fontFamily
                    size: Style.space(16)
                    enabled: !hiruTsatsiEdit.running
                    onClicked: root.removeApp(wsBlock.modelData.id, appBlock.index)
                  }
                }

                Row {
                  spacing: Style.space(8)
                  leftPadding: Style.space(12)

                  Text {
                    textFormat: Text.PlainText
                    anchors.verticalCenter: parent.verticalCenter
                    text: appBlock.modelData.status
                    color: Qt.darker(root.bar.foreground, 1.6)
                    font.family: root.bar.fontFamily
                    font.pixelSize: Style.font.caption
                    elide: Text.ElideRight
                    width: Style.space(250)
                  }

                  Button {
                    anchors.verticalCenter: parent.verticalCenter
                    text: appBlock.choosing ? root.s.cancelButton : root.s.changeButton
                    foreground: root.bar.foreground
                    fontSize: Style.font.caption
                    verticalPadding: Style.space(1)
                    onClicked: root.chooseWindowFor(wsBlock.modelData.id, appBlock.index)
                  }
                }

                Repeater {
                  model: appBlock.choosing ? root.windowChoices : []

                  delegate: Button {
                    required property var modelData
                    leftAlign: true
                    width: Style.space(320)
                    text: "→ " + modelData.title + "  (" + root.s.workspaceLabel + " " + modelData.workspace + ")"
                    foreground: root.bar.foreground
                    fontSize: Style.font.caption
                    verticalPadding: Style.space(1)
                    onClicked: root.pickWindow(wsBlock.modelData.id, appBlock.index, modelData.address)
                  }
                }

                Button {
                  visible: appBlock.choosing
                  leftAlign: true
                  width: Style.space(320)
                  text: root.s.forgetButton
                  foreground: root.bar.foreground
                  fontSize: Style.font.caption
                  verticalPadding: Style.space(1)
                  onClicked: root.forgetWindow(wsBlock.modelData.id, appBlock.index)
                }
              }
            }

            Row {
              width: parent.width
              spacing: Style.space(6)

              TextField {
                id: appNameField
                width: Style.space(100)
                placeholderText: root.s.namePlaceholder
                foreground: root.bar.foreground
                verticalPadding: Style.space(4)
              }

              TextField {
                id: appCmdField
                width: Style.space(160)
                placeholderText: root.s.commandPlaceholder
                foreground: root.bar.foreground
                verticalPadding: Style.space(4)
                onAccepted: wsBlock.addApp()
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

          NumberField {
            anchors.verticalCenter: parent.verticalCenter
            value: root.newWorkspaceId
            from: 1
            to: 99
            fieldWidth: Style.space(70)
            foreground: root.bar.foreground
            fontFamily: root.bar.fontFamily
            onModified: function(value) { root.newWorkspaceId = value }
          }

          TextField {
            id: wsLabelField
            width: Style.space(170)
            placeholderText: root.s.newWorkspacePlaceholder
            foreground: root.bar.foreground
            onAccepted: {
              root.newWorkspaceLabel = text
              if (root.addWorkspace()) text = ""
            }
          }

          Button {
            text: root.s.addWorkspaceButton
            enabled: !root.newWorkspaceIdTaken
            foreground: root.bar.foreground
            bordered: true
            onClicked: {
              root.newWorkspaceLabel = wsLabelField.text
              if (root.addWorkspace()) wsLabelField.text = ""
            }
          }
        }

        Text {
          textFormat: Text.PlainText
          visible: root.newWorkspaceIdTaken
          text: root.s.workspaceTaken.arg(root.newWorkspaceId)
          color: Qt.darker(root.bar.foreground, 1.3)
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.bodySmall
        }

        Text {
          textFormat: Text.PlainText
          visible: root.editProblem !== ""
          text: root.editProblem
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.bodySmall
          wrapMode: Text.WordWrap
          width: parent.width
        }
      }
    }
  }
}
