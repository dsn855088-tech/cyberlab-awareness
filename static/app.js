const form = document.getElementById("loginForm");
const status = document.getElementById("status");

// Random pseudonymous browser-session ID. It contains no name or login data.
const anonId = sessionStorage.getItem("cyberlab_anon_id") || (crypto.randomUUID ? crypto.randomUUID() : (
  "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === "x" ? r : (r & 0x3 | 0x8)).toString(16);
  })
)).toLowerCase();
sessionStorage.setItem("cyberlab_anon_id", anonId);

async function logEvent(type) {
  try {
    await fetch("/api/event", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({consent: true, event_type: type, anon_id: anonId})
    });
  } catch (_) {}
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!document.getElementById("consent").checked) {
    status.textContent = "Please acknowledge the training notice.";
    return;
  }
  // Deliberately never read username/password values.
  sessionStorage.setItem("cyberlab_training_consent", "yes");
  await logEvent("demo_started");
  location.href = "/lesson";
});

document.getElementById("revealBtn").addEventListener("click", async () => {
  if (!document.getElementById("consent").checked) {
    status.textContent = "Please acknowledge the training notice first.";
    return;
  }
  sessionStorage.setItem("cyberlab_training_consent", "yes");
  await logEvent("demo_started");
  location.href = "/lesson";
});
