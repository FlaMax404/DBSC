console.log("Background script 'app.js' started successfully!");

// The name of your local application. This MUST match the name
// you define in your Native Application Manifest later.
const NATIVE_APP_NAME = "com.dbsc.local_messenger";
let nativePort;

// In-memory cache to prevent slow storage lookups on every single HTTP request
let domainTokensCache = {};

// 1. Connect to the local machine program
function connectToNativeApp() {
  if (nativePort) return; // Prevent multiple active connections

  nativePort = browser.runtime.connectNative(NATIVE_APP_NAME);

  // 2. Listen for encrypted credentials or responses from the local machine
  nativePort.onMessage.addListener((message) => {
    console.log("Received response from local program:", message);

    if (message.action === "encryption_complete") {
      // Store the bound token tied to the specific domain to prevent leaking
      const domain = message.domain;
      if (domain) {
        domainTokensCache[domain] = message.token;
        browser.storage.local.set({ domainTokens: domainTokensCache });
        console.log(`DBSC token bound and stored for domain: ${domain}`);
      }
    } else if (message.action === "set_secure_cookie") {
      // Example: Middleware commands the browser to set an encrypted session cookie
      browser.cookies.set({
        url: message.url,
        name: message.cookieName,
        value: message.cookieValue,
        secure: true,
        httpOnly: true,
      });
    }
  });

  nativePort.onDisconnect.addListener((p) => {
    console.error(
      "Disconnected from local program.",
      browser.runtime.lastError,
    );
    nativePort = null;
  });
  console.log("Connected to local program.");
}

function disconnectFromNativeApp() {
  if (nativePort) {
    nativePort.disconnect();
    nativePort = null;
    console.log("Disconnected from local program (by the user).");
  }
}

// 3. Function to trigger the DBSC encryption process
function encryptSessionCredentials(credentials) {
  if (!nativePort) return; // Do not send messages if disconnected
  nativePort.postMessage({ action: "encrypt_session", data: credentials });
}

// --- Icon and State Management ---

/**
 * Updates the browser action icon based on the enabled state.
 * @param {boolean} isEnabled - The current state of the feature.
 */
function updateIcon(isEnabled) {
  const iconPaths = isEnabled
    ? {
        19: "icons/padlock.png",
        38: "icons/padlock-38.png",
      }
    : {
        19: "icons/open-padlock.png",
        38: "icons/open-padlock-38.png",
      };
  browser.action.setIcon({ path: iconPaths });
}

// Listen for messages from the popup to update the icon
browser.runtime.onMessage.addListener((message) => {
  if (message.action === "updateIcon") {
    updateIcon(message.isEnabled);

    // Start or stop native connection based on toggle state
    if (message.isEnabled) {
      connectToNativeApp();
    } else {
      disconnectFromNativeApp();
    }
  }
});

// Set the initial icon and connection state when the extension starts up
browser.storage.local.get("isEnabled").then((result) => {
  const isEnabled = result.isEnabled || false;
  updateIcon(isEnabled); // Default to disabled

  // Load existing tokens into memory cache
  browser.storage.local.get("domainTokens").then((tokenResult) => {
    domainTokensCache = tokenResult.domainTokens || {};
  });

  if (isEnabled) {
    connectToNativeApp();
  }
});

// --- Browser Traffic Interception (DBSC Implementation) ---

// 1. Listen for new sessions (e.g., after login) to send to middleware
browser.webRequest.onHeadersReceived.addListener(
  (details) => {
    if (!nativePort) return {}; // Skip if disabled

    // Look for a challenge header from the server asking for a Device Bound Session
    const challengeHeader = details.responseHeaders.find(
      (header) => header.name.toLowerCase() === "sec-session-challenge",
    );

    if (challengeHeader) {
      const domain = new URL(details.url).hostname;
      console.log(
        `Challenge received from ${domain}. Sending to native middleware...`,
      );
      encryptSessionCredentials({
        domain: domain,
        challenge: challengeHeader.value,
      });
    }

    return { responseHeaders: details.responseHeaders };
  },
  { urls: ["<all_urls>"] },
  ["blocking", "responseHeaders"],
);

// 2. Intercept outgoing requests to inject DBSC proofs/tokens
browser.webRequest.onBeforeSendHeaders.addListener(
  (details) => {
    if (!nativePort) return {}; // Skip if disabled

    const domain = new URL(details.url).hostname;
    const boundToken = domainTokensCache[domain];

    if (boundToken) {
      // Inject the bound session token into the request headers for the server to verify
      details.requestHeaders.push({
        name: "Sec-Session-Response",
        value: boundToken,
      });
    }

    return { requestHeaders: details.requestHeaders };
  },
  { urls: ["<all_urls>"] },
  ["blocking", "requestHeaders"],
);
