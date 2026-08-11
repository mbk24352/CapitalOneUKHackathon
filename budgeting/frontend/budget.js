const API_BASE = "http://localhost:5000";
const params   = new URLSearchParams(window.location.search);
const editId   = params.get("id");

async function doLogout() {
  await fetch(`${API_BASE}/logout`, { method: "POST", credentials: "include" });
  window.location.href = "login.html";
}

// Adds a new category row to the form
function addCategoryRow(category = "", expected = "", actual = "") {
  // TODO: Create a row with inputs for category name, expected amount, actual amount
  // and a remove button. Append it to the categories container.
  document.getElementById("categories-container").innerHTML+=`
      <div class="category-row">
            <div>
              <label for="category-name-1">${category}</label>
            </div>
            <div>
              <label for="expected-1">${expected}</label>
            </div>
            <div>
              <label for="actual-1">${actual}</label>
            </div>
    </div>
  `
}

// Reads all category rows from the DOM and returns them as an array
function collectCategories() {
  // TODO: Query all category rows and return an array of
  // { category, expected_amount, actual_amount }
}

// Called when the Save Budget button is clicked
async function submitBudget() {
  const income    = parseFloat(document.getElementById("monthly-income").value);
  const carryover = parseFloat(document.getElementById("carryover").value) || 0;
  const categories = collectCategories();

  // TODO: Validate inputs, then POST or PATCH to /budgets (or /budgets/<id> if editing).
  // On success hide #form-section, show #results-section and call showResults()
}

// Renders the summary box, per-category table and suggestions list after a save
function showResults(income, carryover, summary, suggestions) {
  // TODO: Hide #form-section, show #results-section. Fill #summary-box with
  // income+carryover, total expected/actual and remaining. Populate #summary-tbody
  // with one row per category (expected, actual, difference). Populate
  // #suggestions-list with one <li> per suggestion.
}

window.addEventListener("DOMContentLoaded", async () => {
  if (editId) {
    // TODO: Load existing budget from GET /budgets/<editId> and pre-fill the form
  } else {
    // TODO: Fetch GET /budgets/carryover, pre-fill carryover, add default category rows
  }
});
