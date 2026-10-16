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

  readonly property string configPath: (Quickshell.env("XDG_CONFIG_HOME") || Quickshell.env("HOME") + "/.config") + "/workbench/apps.json"
  readonly property string workbenchCommand: Qt.resolvedUrl("backend/bin/workbench").toString().replace("file://", "")
  readonly property bool starting: workbenchStart.running
  property var config: Model.defaultConfig()

  function launchAll() {
    if (!workbenchStart.running) workbenchStart.running = true
    root.close()
  }

  function editApps() {
    Quickshell.execDetached([root.workbenchCommand, "edit"])
    root.close()
  }

  Process {
    id: workbenchStart
    command: [root.workbenchCommand, "start"]
  }

  FileView {
    id: configFile
    path: root.configPath
    watchChanges: true
    printErrors: false
    onLoaded: root.config = Model.parseConfig(text())
    onLoadFailed: root.config = Model.defaultConfig()
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
    contentWidth: panel.fittedContentWidth(Style.space(360))
    contentHeight: panel.fittedContentHeight(column.implicitHeight, Style.space(480))

    PanelKeyCatcher {
      id: keyCatcher
      anchors.fill: parent
      onCloseRequested: root.close()

      Column {
        id: column
        anchors.fill: parent
        spacing: Style.space(12)

        Text {
          text: root.s.title
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.title
          font.bold: true
        }

        Text {
          text: root.hasAnyApps ? root.s.subtitle : root.s.empty
          color: Qt.darker(root.bar.foreground, 1.5)
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.bodySmall
          wrapMode: Text.WordWrap
          width: parent.width
        }

        Row {
          spacing: Style.space(8)

          Button {
            text: root.starting ? root.s.startingButton : root.s.startButton
            enabled: !root.starting && root.hasAnyApps
            foreground: root.bar.foreground
            bordered: true
            onClicked: root.launchAll()
          }

          Button {
            text: root.s.editButton
            foreground: root.bar.foreground
            bordered: true
            onClicked: root.editApps()
          }
        }

        PanelSeparator {
          visible: root.hasAnyApps
          foreground: root.bar.foreground
        }

        Repeater {
          model: root.config.workspaces

          delegate: Text {
            required property var modelData
            width: column.width
            text: root.s.workspaceLabel + " " + modelData.id + " — " + modelData.label + ": "
                  + modelData.apps.map(function(app) { return app.name }).join(", ")
            color: Qt.darker(root.bar.foreground, 1.2)
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.bodySmall
            elide: Text.ElideRight
          }
        }
      }
    }
  }
}
