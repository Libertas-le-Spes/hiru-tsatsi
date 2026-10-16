// Minimal UI-string i18n. Matches the machine's configured language
// (Qt.locale().name, e.g. "pt_BR", "en_US") rather than the language the
// user happens to be typing in - those can differ. Falls back to English
// for any locale not explicitly listed here.
var TABLE = {
  "pt_BR": {
    title: "Iniciar dia de trabalho?",
    subtitle: "Abre cada app abaixo no workspace dele.",
    empty: "Nenhum app de trabalho ainda. Use Editar apps para adicionar.",
    startButton: "Iniciar aplicativos de trabalho",
    startingButton: "Iniciando aplicativos de trabalho…",
    editButton: "Editar apps…",
    workspaceLabel: "Workspace"
  },
  "en_US": {
    title: "Start your work day?",
    subtitle: "Opens each app below on its own workspace.",
    empty: "No work apps yet. Use Edit apps to add some.",
    startButton: "Start work apps",
    startingButton: "Starting work apps…",
    editButton: "Edit apps…",
    workspaceLabel: "Workspace"
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
