// Minimal UI-string i18n. Matches the machine's configured language
// (Qt.locale().name, e.g. "pt_BR", "en_US") rather than the language the
// user happens to be typing in - those can differ. Falls back to English
// for any locale not explicitly listed here.
var TABLE = {
  "pt_BR": {
    title: "Iniciar dia de trabalho?",
    subtitle: "Abre cada app configurado abaixo no workspace dele.",
    startButton: "Iniciar aplicativos de trabalho",
    workspacesHeader: "WORKSPACES",
    workspaceLabel: "Workspace",
    removeWorkspaceTip: "Remover workspace",
    removeAppTip: "Remover app",
    namePlaceholder: "Nome",
    commandPlaceholder: "Comando",
    windowPlaceholder: "Classe ou título da janela",
    addAppTip: "Adicionar app",
    newWorkspacePlaceholder: "Nome do novo workspace",
    addWorkspaceButton: "Adicionar workspace"
  },
  "en_US": {
    title: "Start your work day?",
    subtitle: "Opens each app configured below on its own workspace.",
    startButton: "Start work apps",
    workspacesHeader: "WORKSPACES",
    workspaceLabel: "Workspace",
    removeWorkspaceTip: "Remove workspace",
    removeAppTip: "Remove app",
    namePlaceholder: "Name",
    commandPlaceholder: "Command",
    windowPlaceholder: "Window class or title",
    addAppTip: "Add app",
    newWorkspacePlaceholder: "New workspace name",
    addWorkspaceButton: "Add workspace"
  }
}

function forLocale(localeName) {
  var name = String(localeName || "")
  if (TABLE[name]) return TABLE[name]
  // Match by language regardless of region (e.g. "pt_PT" -> "pt_BR" table).
  var lang = name.split("_")[0]
  for (var key in TABLE) {
    if (key.split("_")[0] === lang) return TABLE[key]
  }
  return TABLE["en_US"]
}

if (typeof module !== "undefined") {
  module.exports = { forLocale: forLocale }
}
