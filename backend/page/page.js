const token = document.querySelector('meta[name="token"]').content;
const workspacesBox = document.getElementById("workspaces");
let state = { workspaces: [], nextNumber: 1 };
let openChoices = null;

async function call(path, body) {
  const options = { headers: { "X-Hiru-Tsatsi-Token": token } };
  if (body !== undefined) {
    options.method = "POST";
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const answer = await fetch(path, options);
  const content = await answer.json();
  if (!answer.ok) throw new Error(content.error || "Something went wrong");
  return content;
}

function element(tag, properties = {}, children = []) {
  const made = Object.assign(document.createElement(tag), properties);
  made.append(...children);
  return made;
}

function showError(error) {
  const toast = document.getElementById("toast");
  toast.textContent = error.message;
  toast.hidden = false;
  clearTimeout(showError.timer);
  showError.timer = setTimeout(() => { toast.hidden = true; }, 5000);
}

async function change(path, body) {
  let changed = true;
  try {
    state = await call(path, body);
  } catch (error) {
    showError(error);
    changed = false;
  }
  render();
  return changed;
}

function savedField(value, properties, save) {
  const field = element("input", { value, ...properties });
  field.addEventListener("keydown", (event) => { if (event.key === "Enter") field.blur(); });
  field.addEventListener("change", () => save(field.value));
  return field;
}

function choicesFor(space, index) {
  const list = element("ul", { className: "choices" });
  call(`/api/windows?workspace=${space.number}&index=${index}`).then(({ windows }) => {
    const pick = (window) => element("button", {
      type: "button",
      onclick: () => { openChoices = null; change("/api/app/window", { workspace: space.number, index, address: window.address }); },
    }, [element("span", { textContent: window.title }), element("span", { textContent: `workspace ${window.workspace}` })]);
    const forget = element("button", {
      type: "button",
      onclick: () => { openChoices = null; change("/api/app/forget", { workspace: space.number, index }); },
    }, [element("span", { textContent: "Forget, and learn it next time Hiru Tsatsi starts it" }), element("span")]);
    list.append(...windows.map((window) => element("li", {}, [pick(window)])), element("li", {}, [forget]));
  }).catch(showError);
  return list;
}

function appRow(space, app, index) {
  const save = (name, command) => change("/api/app/change", { workspace: space.number, index, name, command });
  const toggle = element("button", {
    type: "button", className: "link", textContent: "Change",
    onclick: () => { openChoices = openChoices === `${space.number}/${index}` ? null : `${space.number}/${index}`; render(); },
  });
  const status = element("p", { className: app.status.startsWith("✓") ? "status matched" : "status" },
    [element("span", { textContent: app.status }), toggle]);
  const row = element("div", { className: "app" }, [
    element("div", { className: "row" }, [
      savedField(app.name, { "aria-label": "App name" }, (name) => save(name, app.command)),
      savedField(app.command, { className: "command", "aria-label": "Command" }, (command) => save(app.name, command)),
      element("button", {
        type: "button", className: "remove", textContent: "✕", title: `Remove ${app.name}`,
        onclick: () => change("/api/app/remove", { workspace: space.number, index }),
      }),
    ]),
    status,
  ]);
  if (openChoices === `${space.number}/${index}`) row.append(choicesFor(space, index));
  return row;
}

function newAppForm(space) {
  const name = element("input", { placeholder: "Name", "aria-label": "New app name", required: true });
  const command = element("input", { placeholder: "Command", className: "command", "aria-label": "New app command", required: true });
  return element("form", {
    className: "row new-app",
    onsubmit: (event) => {
      event.preventDefault();
      change("/api/app/add", { workspace: space.number, name: name.value, command: command.value });
    },
  }, [name, command, element("button", { textContent: "Add app" })]);
}

function workspaceCard(space) {
  const save = (newNumber, label) => change("/api/workspace/change", { number: space.number, newNumber: Number(newNumber), label });
  return element("article", { className: "workspace" }, [
    element("div", { className: "row workspace-head" }, [
      savedField(space.number, { type: "number", min: 1, "aria-label": "Workspace number" }, (number) => save(number, space.label)),
      savedField(space.label, { "aria-label": "Workspace name" }, (label) => save(space.number, label)),
      element("button", {
        type: "button", className: "remove", textContent: "✕", title: `Remove workspace ${space.number}`,
        onclick: () => change("/api/workspace/remove", { number: space.number }),
      }),
    ]),
    ...space.apps.map((app, index) => appRow(space, app, index)),
    newAppForm(space),
  ]);
}

function render() {
  document.getElementById("window-titles").checked = state.windowTitles;
  workspacesBox.replaceChildren(...state.workspaces.map(workspaceCard));
  document.getElementById("new-number").value = state.nextNumber;
}

document.getElementById("new-workspace").addEventListener("submit", (event) => {
  event.preventDefault();
  const label = document.getElementById("new-label");
  change("/api/workspace/add", { number: Number(document.getElementById("new-number").value), label: label.value })
    .then((changed) => { if (changed) label.value = ""; });
});

document.getElementById("window-titles").addEventListener("change", (event) => {
  change("/api/window-titles", { on: event.currentTarget.checked });
});

document.getElementById("start").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  const report = document.getElementById("report");
  button.disabled = true;
  button.textContent = "Starting work apps…";
  try {
    const outcome = await call("/api/start", {});
    report.textContent = `${outcome.summary}\n${outcome.details}`;
    report.hidden = false;
    state = await call("/api/list");
    render();
  } catch (error) {
    showError(error);
  }
  button.disabled = false;
  button.textContent = "Start work apps";
});

async function reload() {
  try {
    state = await call("/api/list");
    render();
  } catch (error) {
    showError(error);
  }
}

window.addEventListener("focus", reload);
setInterval(() => call("/api/alive", {}).catch(() => {}), 20000);
reload();
