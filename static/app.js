const form = document.getElementById("loginForm");
const status = document.getElementById("status");
async function logEvent(type) {
  try { await fetch("/api/event", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({consent:true,event_type:type})}); } catch (_) {}
}
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!document.getElementById("consent").checked) {
    status.textContent = "Please acknowledge the training notice.";
    return;
  }
  // Deliberately never read or transmit the username/password values.
  await logEvent("demo_started");
  location.href = "/lesson";
});
document.getElementById("revealBtn").addEventListener("click", async () => {
  if (!document.getElementById("consent").checked) {
    status.textContent = "Please acknowledge the training notice first.";
    return;
  }
  await logEvent("training_reveal");
  location.href = "/lesson";
});