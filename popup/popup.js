const statusText = document.getElementById("status-text");
const toggleSwitch = document.getElementById("toggle-switch");
const sessionStatusText = document.getElementById("session-status");
const middlewareStatusText = document.getElementById("middleware-status");
const errorStatusText = document.getElementById("error-status");
const githubBtn = document.getElementById("github-btn");

/**
 * Updates the popup's UI elements based on the feature's state.
 * @param {boolean} isEnabled - The current state of the feature.
 */
function updateUI(isEnabled) {
  toggleSwitch.checked = isEnabled;
  statusText.textContent = `DBSC is ${isEnabled ? "enabled" : "disabled"}`;
}

function updateAdvancedStatus() {
  browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
    if (tabs.length === 0) return;

    let domain = "";
    try {
      domain = new URL(tabs[0].url).hostname;
    } catch (e) {
      // Internal pages or invalid URLs (e.g., about:blank)
    }

    browser.runtime
      .sendMessage({ action: "getStatus", domain })
      .then((response) => {
        if (!response) return;

        middlewareStatusText.textContent = `Middleware: ${response.isMiddlewareConnected ? "🟢 Connected" : "🔴 Disconnected"}`;
        sessionStatusText.textContent = `Current Session DBSC: ${response.isSessionBound ? "🔒 Active" : "🔓 Inactive"}`;

        if (response.lastError) {
          errorStatusText.textContent = `⚠️ Error: ${response.lastError}`;
          errorStatusText.style.display = "block";
        } else {
          errorStatusText.style.display = "none";
        }
      })
      .catch((err) => {
        middlewareStatusText.textContent = "Middleware: 🔴 Disconnected";
        sessionStatusText.textContent = "Current Session DBSC: 🔓 Inactive";
        errorStatusText.textContent =
          "⚠️ Error: Unable to communicate with extension background.";
        errorStatusText.style.display = "block";
      });
  });
}

// Initialize the popup UI when it's opened
browser.storage.local.get("isEnabled").then((result) => {
  updateUI(result.isEnabled || false);
  updateAdvancedStatus();
});

// Listen for clicks on the toggle switch
toggleSwitch.addEventListener("change", () => {
  const isEnabled = toggleSwitch.checked;

  // 1. Save the new state
  browser.storage.local.set({ isEnabled });

  // 2. Update the popup UI
  updateUI(isEnabled);

  // 3. Tell the background script to update the browser icon
  browser.runtime.sendMessage({ action: "updateIcon", isEnabled });

  // 4. Update the detailed status slightly after state changes
  setTimeout(updateAdvancedStatus, 150);
});

// GitHub Redirect Button
githubBtn.addEventListener("click", () => {
  browser.tabs.create({ url: "https://github.com/FlaMax404/DBSC/" });
});
