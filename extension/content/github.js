// DevStart AI — GitHub repository overlay
//
// Injects a launcher and a floating assistant window on repository pages.
// The window is an extension iframe so the panel UI stays in one place, and
// this script feeds it repository context scraped from the GitHub page.

(() => {
  const HOST_ID = "devstart-host";
  const AUTO_OPEN_KEY = "devstart-auto-opened";
  const RESERVED_ROOTS = new Set([
    "settings",
    "notifications",
    "marketplace",
    "explore",
    "topics",
    "trending",
    "collections",
    "events",
    "sponsors",
    "login",
    "signup",
    "join",
    "new",
    "organizations",
    "orgs",
    "users",
    "search",
    "features",
    "enterprise",
    "pricing",
    "about",
    "security",
    "site",
    "apps",
    "codespaces",
    "issues",
    "pulls",
    "dashboard",
    "account",
    "sessions"
  ]);

  let host = null;
  let launcher = null;
  let shell = null;
  let frame = null;
  let lastRepoKey = "";
  let mounted = false;

  function extensionOrigin() {
    try {
      return new URL(chrome.runtime.getURL("")).origin;
    } catch {
      return "";
    }
  }

  function readRepo() {
    const meta = document.querySelector('meta[name="octolytics-dimension-repository_nwo"]');
    const parts = location.pathname.split("/").filter(Boolean);

    let fullName = meta && meta.content ? meta.content : "";
    if (!fullName && parts.length >= 2 && !RESERVED_ROOTS.has(parts[0])) {
      fullName = `${parts[0]}/${parts[1]}`;
    }

    if (!fullName || !fullName.includes("/")) return null;

    const [owner, name] = fullName.split("/");
    const publicMeta = document.querySelector('meta[name="octolytics-dimension-repository_public"]');
    const visibility = publicMeta && publicMeta.content === "false" ? "Private" : "Public";

    return {
      owner,
      name,
      fullName: `${owner}/${name}`,
      visibility,
      branch: readBranch(),
      stars: readText("#repo-stars-counter-star") || "—",
      forks: readText("#repo-network-counter") || "—",
      issues: readText("#issues-repo-tab-count") || "—"
    };
  }

  function readText(selector) {
    const el = document.querySelector(selector);
    if (!el) return "";
    return (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 24);
  }

  function readBranch() {
    const selectors = [
      ".ref-selector-button-text",
      'button[data-hotkey="w"] .Text-sc-17v1xeu-0',
      'button[data-hotkey="w"] span',
      '[data-testid="anchor-button"] span'
    ];

    for (const selector of selectors) {
      const text = readText(selector);
      if (text && text.length < 48) return text;
    }
    return "main";
  }

  function ensureUI() {
    if (mounted && host && host.isConnected) return;

    host = document.createElement("div");
    host.id = HOST_ID;

    launcher = document.createElement("button");
    launcher.type = "button";
    launcher.className = "devstart-launcher";
    launcher.setAttribute("aria-label", "Open DevStart AI repository assistant");
    launcher.innerHTML =
      '<span class="devstart-mark" aria-hidden="true"></span><span>DevStart AI</span>';
    launcher.addEventListener("click", openPanel);

    shell = document.createElement("div");
    shell.className = "devstart-shell";
    shell.hidden = true;

    frame = document.createElement("iframe");
    frame.title = "DevStart AI repository assistant";
    frame.setAttribute("allow", "microphone; clipboard-write");
    frame.addEventListener("load", sendContext);

    shell.appendChild(frame);
    host.append(launcher, shell);
    document.documentElement.appendChild(host);
    mounted = true;
  }

  function openPanel() {
    if (!readRepo()) return;
    ensureUI();
    if (!frame.src) {
      frame.src = chrome.runtime.getURL("sidepanel/sidepanel.html?embed=1");
    }

    shell.hidden = false;
    launcher.hidden = true;

    requestAnimationFrame(() => {
      if (shell) shell.classList.add("is-open");
    });

    try {
      sessionStorage.setItem(AUTO_OPEN_KEY, "1");
    } catch {
      /* storage may be unavailable */
    }

    setTimeout(sendContext, 120);
  }

  function closePanel() {
    if (!shell) return;
    shell.classList.remove("is-open");
    if (launcher) launcher.hidden = false;
    setTimeout(() => {
      if (shell && !shell.classList.contains("is-open")) shell.hidden = true;
    }, 220);
  }

  function togglePanel() {
    if (!readRepo()) return;
    ensureUI();
    if (!shell || shell.hidden || !shell.classList.contains("is-open")) {
      openPanel();
    } else {
      closePanel();
    }
  }

  function sendContext() {
    if (!frame || !frame.contentWindow) return;
    const repo = readRepo();
    if (!repo) return;
    frame.contentWindow.postMessage(
      { source: "devstart-content", type: "REPO_CONTEXT", repo },
      "*"
    );
  }

  function maybeAutoOpen() {
    try {
      if (sessionStorage.getItem(AUTO_OPEN_KEY) === "1") return;
    } catch {
      return;
    }
    setTimeout(openPanel, 750);
  }

  function unmount() {
    if (host && host.isConnected) host.remove();
    host = null;
    launcher = null;
    shell = null;
    frame = null;
    mounted = false;
    lastRepoKey = "";
  }

  function boot() {
    const repo = readRepo();

    if (!repo) {
      unmount();
      return;
    }

    ensureUI();

    if (repo.fullName !== lastRepoKey) {
      lastRepoKey = repo.fullName;
      sendContext();
    }

    maybeAutoOpen();
  }

  // Messages from the embedded panel
  window.addEventListener("message", (event) => {
    const expectedOrigin = extensionOrigin();
    if (!expectedOrigin || event.origin !== expectedOrigin) return;

    const data = event.data;
    if (!data || data.source !== "devstart-panel") return;

    if (data.type === "CLOSE" || data.type === "MINIMIZE") {
      closePanel();
    } else if (data.type === "PANEL_READY") {
      sendContext();
    }
  });

  // Toolbar action toggles the on-page assistant when it is available
  if (chrome.runtime && chrome.runtime.onMessage) {
    chrome.runtime.onMessage.addListener((message) => {
      if (message && message.type === "DEVSTART_TOGGLE") {
        togglePanel();
      }
    });
  }

  document.addEventListener("turbo:load", boot);
  document.addEventListener("pjax:end", boot);
  window.addEventListener("popstate", boot);

  boot();
})();
