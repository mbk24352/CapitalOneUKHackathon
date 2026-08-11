const API_BASE = "http://localhost:5000";

async function doSignup() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorEl = document.getElementById("signup-error");
  errorEl.style.display = "none";

  if (!name || !email || !username || !password) {
    showError("Please enter your name, email, username, and password.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, username, password }),
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Signup failed.");
      return;
    }

    window.location.href = "login.html";
  } catch (e) {
    showError("Could not connect to the server. Is the backend running?");
  }
}

function showError(msg) {
  const el = document.getElementById("signup-error");
  el.textContent = msg;
  el.style.display = "block";
}

document.addEventListener("keydown", (e) => { if (e.key === "Enter") doSignup(); });
