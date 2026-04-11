const statusText = document.getElementById("status-text");
const toggleSwitch = document.getElementById("toggle-switch");

/**
 * Updates the popup's UI elements based on the feature's state.
 * @param {boolean} isEnabled - The current state of the feature.
 */
function updateUI(isEnabled) {
  toggleSwitch.checked = isEnabled;
  statusText.textContent = `DBSC is ${isEnabled ? "enabled" : "disabled"}`;
}

// Initialize the popup UI when it's opened
browser.storage.local.get("isEnabled").then((result) => {
  updateUI(result.isEnabled || false);
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
});
