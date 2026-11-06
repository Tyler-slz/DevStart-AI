// DevStart AI service worker
//
// On GitHub the toolbar action toggles the on-page assistant. Elsewhere it
// opens the side panel so the extension still works outside a repository.

chrome.runtime.onInstalled.addListener(() => {
  console.log("DevStart AI installed");
});

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !tab.id) return;

  const isGitHub = typeof tab.url === "string" && tab.url.startsWith("https://github.com/");

  if (isGitHub) {
    try {
      await chrome.tabs.sendMessage(tab.id, { type: "DEVSTART_TOGGLE" });
      return;
    } catch {
      /* content script not ready — fall through to the side panel */
    }
  }

  if (chrome.sidePanel && chrome.sidePanel.open) {
    try {
      await chrome.sidePanel.open({ tabId: tab.id });
    } catch {
      /* opening the panel can fail outside a user gesture */
    }
  }
});
