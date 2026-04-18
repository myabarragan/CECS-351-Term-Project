// CHAT PAGE 
function setupChatPage() {
  const input = document.getElementById("queryInput");
  const btn = document.getElementById("searchBtn");
  const messages = document.getElementById("chatMessages");

  function doSearch() {
    const query = input.value.trim();
    if (!query) return;

    // Show user's message in chat
    const userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.textContent = query;
    messages.appendChild(userMsg);

    // Show a "searching..." bot message
    const botMsg = document.createElement("div");
    botMsg.className = "message bot";
    botMsg.textContent = "Searching...";
    messages.appendChild(botMsg);

    input.value = "";
    btn.disabled = true;

    fetch(`/api/search?query=${encodeURIComponent(query)}`)
      .then(r => r.json())
      .then(data => {
        const count = (data.results || []).length;
        botMsg.textContent = `I found ${count} matching email${count === 1 ? "" : "s"}.`;

        // Save results in sessionStorage so the results page can read them
        sessionStorage.setItem("lastQuery", query);
        sessionStorage.setItem("lastResults", JSON.stringify(data.results || []));

        setTimeout(() => { window.location.href = "/results"; }, 700);
      })
      .catch(err => {
        botMsg.textContent = "Something went wrong. Please try again.";
        console.error(err);
        btn.disabled = false;
      });
  }

  btn.addEventListener("click", doSearch);
  input.addEventListener("keydown", e => {
    if (e.key === "Enter") doSearch();
  });
}


// RESULTS PAGE
function setupResultsPage() {
  const query = sessionStorage.getItem("lastQuery") || "";
  const results = JSON.parse(sessionStorage.getItem("lastResults") || "[]");
  const heading = document.getElementById("resultsHeading");
  const list = document.getElementById("resultsList");

  heading.textContent = `Search Results (${results.length} email${results.length === 1 ? "" : "s"} found)`;

  if (results.length === 0) {
    list.innerHTML = `<div class="empty-state">
      No results for "${escapeHtml(query)}".<br>
      <button class="btn-primary" style="margin-top:16px" onclick="window.location.href='/chat'">Try another search</button>
    </div>`;
    return;
  }

  results.forEach(email => {
    const card = document.createElement("div");
    card.className = "result-card";
    card.innerHTML = `
      <div class="field"><strong>From:</strong> ${escapeHtml(email.sender || "Unknown")}</div>
      <div class="field"><strong>Subject:</strong> ${escapeHtml(email.subject || "(no subject)")}</div>
      <div class="field"><strong>Date:</strong> ${escapeHtml(email.date || "")}</div>
      <div class="snippet">${escapeHtml(email.snippet || "")}</div>
    `;
    card.addEventListener("click", () => {
      window.location.href = `/email-view/${encodeURIComponent(email.id)}`;
    });
    list.appendChild(card);
  });
}


// EMAIL DETAIL PAGE 
function setupEmailPage() {
  // Get email ID from URL path
  const parts = window.location.pathname.split("/");
  const emailId = decodeURIComponent(parts[parts.length - 1]);
  const card = document.getElementById("emailCard");

  fetch(`/api/email/${encodeURIComponent(emailId)}`)
    .then(r => {
      if (!r.ok) throw new Error("Email not found");
      return r.json();
    })
    .then(email => {
      card.innerHTML = `
        <div class="email-meta">
          <div class="field"><strong>From:</strong> ${escapeHtml(email.sender || "Unknown")}</div>
          <div class="field"><strong>Subject:</strong> ${escapeHtml(email.subject || "(no subject)")}</div>
          <div class="field"><strong>Date:</strong> ${escapeHtml(email.date || "")}</div>
        </div>
        <div class="email-body">${escapeHtml(email.body || "(no content)")}</div>
      `;
    })
    .catch(err => {
      card.innerHTML = `<div class="empty-state">Could not load email.<br>${escapeHtml(err.message)}</div>`;
    });
}


// Basic HTML escape to prevent any weirdness in email content
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}