const API_BASE = "http://localhost:5000";

async function doSignup() {
  // TODO: Read name, email, username and password from the form inputs
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
  // TODO: Validate the fields, then POST { name, email, username, password } to /register
  // TODO: Handle success (redirect to login.html) and failure appropriately
}

document.addEventListener("keydown", (e) => { if (e.key === "Enter") doSignup(); });