const rows = document.getElementById("eventRows");
function safeCell(value) {
  const td = document.createElement("td");
  td.textContent = value;
  return td;
}
async function refresh() {
  try {
    const response = await fetch("/api/admin/events", {cache:"no-store"});
    if (response.status === 401) { location.href = "/investigator"; return; }
    if (!response.ok) throw new Error("Request failed");
    const data = await response.json();
    document.getElementById("starts").textContent = data.counts.demo_started;
    document.getElementById("reveals").textContent = data.counts.training_reveal;
    document.getElementById("sessions").textContent = new Set(data.events.map(e => e.anon_id)).size;
    rows.replaceChildren();
    if (!data.events.length) {
      const tr = document.createElement("tr");
      const td = safeCell("No events yet. Open the participant page and run a consented test.");
      td.colSpan = 3; td.className = "empty"; tr.appendChild(td); rows.appendChild(tr);
    } else {
      [...data.events].reverse().forEach(event => {
        const tr = document.createElement("tr");
        tr.appendChild(safeCell(event.time));
        const eventCell = document.createElement("td");
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = event.event_type === "demo_started" ? "Demo started" : "Lesson revealed";
        eventCell.appendChild(tag); tr.appendChild(eventCell);
        tr.appendChild(safeCell(event.anon_id.slice(0, 8) + "…"));
        rows.appendChild(tr);
      });
    }
    document.getElementById("updated").textContent = "Updated " + new Date().toLocaleTimeString();
  } catch (_) {
    document.getElementById("updated").textContent = "Connection issue; retrying…";
  }
}
document.getElementById("logoutBtn").addEventListener("click", async () => {
  await fetch("/admin/logout", {method:"POST"});
  location.href = "/investigator";
});
refresh();
setInterval(refresh, 3000);
