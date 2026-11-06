// DevStart AI — microphone permission page
//
// Side panels cannot reliably show the microphone prompt, so the panel opens
// this page in a normal tab. Once getUserMedia succeeds we tell the panel and
// close the tab.

const allowBtn = document.getElementById("allowBtn");
const statusEl = document.getElementById("status");

function setStatus(text, kind) {
  statusEl.textContent = text;
  statusEl.className = "status" + (kind ? ` is-${kind}` : "");
}

async function requestMicrophone() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    setStatus("This browser does not expose microphone access.", "fail");
    return;
  }

  allowBtn.disabled = true;
  setStatus("Waiting for the browser prompt…");

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach((track) => track.stop());

    setStatus("Microphone allowed. Returning to DevStart AI…", "ok");

    try {
      await chrome.runtime.sendMessage({ type: "MIC_PERMISSION_GRANTED" });
    } catch {
      /* the panel may not be open; permission is still granted */
    }

    setTimeout(() => window.close(), 700);
  } catch (error) {
    allowBtn.disabled = false;

    if (error && (error.name === "NotAllowedError" || error.name === "SecurityError")) {
      setStatus(
        "Access was blocked. Allow the microphone for this extension in the browser's site settings, then try again.",
        "fail"
      );
    } else if (error && error.name === "NotFoundError") {
      setStatus("No microphone was found on this device.", "fail");
    } else {
      setStatus("Couldn't access the microphone. Try again.", "fail");
    }
  }
}

allowBtn.addEventListener("click", requestMicrophone);
