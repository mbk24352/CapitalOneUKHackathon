from flask import Flask, request, jsonify, session
from flask_cors import CORS
from calculator import calculate_budget_summary, validate_budget, generate_suggestions
import sqlite3, os, csv
from datetime import date

app = Flask(__name__)
app.secret_key = "hackathon-secret-key"
CORS(app, supports_credentials=True)

DATA_DIR = os.path.dirname(__file__)
DB_PATH  = os.path.join(DATA_DIR, "data.db")


# ══════════════════════════════════════════════════════════════════════════════
# DATA LAYER — swap between SQLite and CSV by commenting/uncommenting each block
#
# To use SQLite: keep the DB block uncommented, comment out the CSV block
# To use CSV:    keep the CSV block uncommented, comment out the DB block
# ══════════════════════════════════════════════════════════════════════════════


# ── SQLITE DATA FUNCTIONS (uncomment to use) ──────────────────────────────────

# def get_db():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn
#
# def find_user(username, password):
#     conn = get_db()
#     row  = conn.execute(
#         "SELECT * FROM users WHERE username = ? AND password = ?",
#         (username, password)
#     ).fetchone()
#     conn.close()
#     return row
#
# def find_user_by_id(user_id):
#     conn = get_db()
#     row  = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
#     conn.close()
#     return row
#
# def get_budgets_for_user(user_id):
#     # TODO: query budgets table for all budgets belonging to user_id
#     pass
#
# def get_budget_by_id(budget_id):
#     # TODO: query budgets table for a single budget by id
#     pass
#
# def get_categories_for_budget(budget_id):
#     # TODO: query categories table for all rows with matching budget_id
#     pass
#
# def get_latest_budget(user_id):
#     # TODO: return the most recently created budget for this user, or None
#     pass
#
# def save_budget(user_id, monthly_income, carryover, categories):
#     # TODO: INSERT a new budget row and its categories, return the new budget id
#     pass
#
# def update_budget(budget_id, monthly_income, carryover, categories):
#     # TODO: UPDATE the budget row, DELETE old categories, INSERT new ones
#     pass
#
# def delete_budget(budget_id):
#     # TODO: DELETE the budget and its categories
#     pass
#
# def register_user(username, password, name, email):
#     # TODO: check username not taken, INSERT new user, return True/False
#     pass


# ── CSV DATA FUNCTIONS (active by default) ────────────────────────────────────

def _read_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def _write_csv(filename, rows, fieldnames):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def _next_id(rows):
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1

def find_user(username, password):
    for row in _read_csv("users.csv"):
        if row["username"] == username and row["password"] == password:
            return row
    return None

def find_user_by_id(user_id):
    for row in _read_csv("users.csv"):
        if row["id"] == str(user_id):
            return row
    return None

def get_budgets_for_user(user_id):
    # TODO: read budgets.csv and return all rows where user_id matches
    budgets = _read_csv("budgets.csv")
    return [budget for budget in budgets if budget["user_id"] == str(user_id)]


def get_budget_by_id(budget_id):
    # TODO: read budgets.csv and return the row where id matches, or None
    budgets = _read_csv("budgets.csv")
    for budget in budgets:
        if budget["id"] == str(budget_id):
            return budget
    return None

def get_categories_for_budget(budget_id):
    # TODO: read categories.csv and return all rows where budget_id matches
    categories = _read_csv("categories.csv")
    return [cat for cat in categories if cat["budget_id"] == str(budget_id)]



def get_latest_budget(user_id):
    # TODO: get all budgets for this user and return the most recently created, or None
    budgets = get_budgets_for_user(user_id)
    if not budgets:
        return None
    budgets.sort(key=lambda b: b.get("created_at", ""), reverse=True)
    return budgets[0]


def save_budget(user_id, monthly_income, carryover, categories):
    # TODO: append a new row to budgets.csv and save categories, return the new id
    budgets = _read_csv("budgets.csv")
    new_id = _next_id(budgets) if budgets else 1
    new_budget = {
        "id": new_id,
        "user_id": user_id,
        "monthly_income": f"{float(monthly_income):.2f}",
        "carryover": f"{float(carryover):.2f}",
        "created_at": date.today().isoformat()
    }
    budgets.append(new_budget)
    _write_csv("budgets.csv", budgets, ["id", "user_id", "monthly_income", "carryover", "created_at"])
    _save_categories(new_id, categories)    

    return new_id

def update_budget(budget_id, monthly_income, carryover, categories):
    # TODO: update the matching row in budgets.csv, replace its categories in categories.csv
    budgets = _read_csv("budgets.csv")
    for budget in budgets:
        if budget["id"] == str(budget_id):
            budget["monthly_income"] = f"{float(monthly_income):.2f}"
            budget["carryover"] = f"{float(carryover):.2f}"
            break
    _write_csv("budgets.csv", budgets, ["id", "user_id", "monthly_income", "carryover", "created_at"])
    _save_categories(budget_id, categories)

    return True

def delete_budget(budget_id):
    # TODO: remove the budget row from budgets.csv and its categories from categories.csv
    budgets = _read_csv("budgets.csv")
    budgets = [b for b in budgets if b["id"] != str(budget_id)]
    _write_csv("budgets.csv", budgets, ["id", "user_id", "monthly_income", "carryover", "created_at"])
    categories = _read_csv("categories.csv")
    categories = [c for c in categories if c["budget_id"] != str(budget_id)]
    _write_csv("categories.csv", categories, ["id", "budget_id", "category", "expected_amount", "actual_amount"])
    return True

def register_user(username, password, name, email):
    # TODO: check username not already taken, append new user to users.csv, return True/False
    users = _read_csv("users.csv")
    if any(u["username"] == username for u in users):
        return False
    new_user = {
        "id": _next_id(users) if users else 1,
        "username": username,
        "password": password,
        "name": name,
        "email": email
    }
    users.append(new_user)
    _write_csv("users.csv", users, ["id", "username", "password", "name", "email"])
    return True

def _save_categories(budget_id, categories):
    all_cats = _read_csv("categories.csv")
    next_id  = _next_id(all_cats) if all_cats else 1
    for c in categories:
        all_cats.append({
            "id": next_id, "budget_id": budget_id,
            "category":        c["category"],
            "expected_amount": f"{float(c['expected_amount']):.2f}",
            "actual_amount":   f"{float(c['actual_amount']):.2f}",
        })
        next_id += 1
    _write_csv("categories.csv", all_cats,
               ["id","budget_id","category","expected_amount","actual_amount"])


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — use this /login route as your reference for the others
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = find_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = int(user["id"])
    return jsonify({"message": "Login successful", "name": user["name"]}), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@app.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip()

    if not all([username, password, name, email]):
        return jsonify({"error": "All fields are required"}), 400

    if not register_user(username, password, name, email):
        return jsonify({"error": "Username already taken"}), 400

    return jsonify({"message": "Account created successfully"}), 201


@app.route("/customer", methods=["GET"])
def customer():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # TODO: fetch the user using find_user_by_id and return their name and email
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"name": user["name"], "email": user["email"]}), 200


@app.route("/budgets", methods=["GET"])
def list_budgets():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # TODO: fetch all budgets for this user and return them as a list. For each
    # budget also include total_outgoings (total actual spend) and spend_percentage
    # = (total_outgoings / (monthly_income + carryover)) * 100

    pass


@app.route("/budgets", methods=["POST"])
def create_budget():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data       = request.get_json()
    income     = data.get("monthly_income")
    carryover  = data.get("carryover", 0)
    categories = data.get("categories", [])

    # TODO: validate inputs, call validate_budget(), save the budget,
    # then return the summary and suggestions
    pass


@app.route("/budgets/<int:budget_id>", methods=["GET"])
def get_budget(budget_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # TODO: fetch the budget, verify it belongs to this user, return with categories and summary
    pass


@app.route("/budgets/<int:budget_id>", methods=["PATCH"])
def edit_budget(budget_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # TODO: validate inputs, update the budget, return updated summary and suggestions
    
    pass


@app.route("/budgets/<int:budget_id>", methods=["DELETE"])
def remove_budget(budget_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # TODO: verify the budget belongs to this user, then delete it
    pass


@app.route("/budgets/carryover", methods=["GET"])
def get_carryover():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    # TODO: get the latest budget for this user, calculate remaining_actual
    # and return it as {"carryover": <value>}. Return 0 if no budget exists.
    pass


if __name__ == "__main__":
    from seed import seed
    if not os.path.exists(DB_PATH):
        seed()
    app.run(debug=True, port=5000)
