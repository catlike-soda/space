/** PWA Service Worker registration. */

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").then(
      (reg) => {
        console.log("SW registered:", reg.scope);
        // Check for updates
        reg.addEventListener("updatefound", () => {
          const newWorker = reg.installing;
          newWorker.addEventListener("statechange", () => {
            if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
              // New content available
              if (confirm("有新版本可用，是否刷新？")) {
                window.location.reload();
              }
            }
          });
        });
      },
      (err) => console.log("SW registration failed:", err)
    );
  });
}

// iOS standalone detection
if (window.navigator.standalone) {
  document.documentElement.classList.add("ios-standalone");
}
