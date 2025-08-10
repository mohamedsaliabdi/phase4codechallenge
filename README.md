# Heroes & Powers API (Flask)

A simple Flask REST API that models comic-book **Heroes**, their **Powers**, and the join table **HeroPower**.  
This README explains the data model, validations, required routes, setup steps (migrations + seed), and example requests/responses.

---

## ⚡ Overview

- **One `Hero` has many `Power`s through `HeroPower`.**
- **One `Power` has many `Hero`s through `HeroPower`.**
- **A `HeroPower` belongs to a `Hero` and a `Power`.**
- The `HeroPower` model **cascades deletes** when its related `Hero` or `Power` is removed.
- Serialization rules are **limited** (no infinite recursion) using `to_dict()` include/exclude fields.

---

## 🧱 Tech Stack

- Python 3.10+
- Flask
- Flask SQLAlchemy
- Flask-Migrate (Alembic)
- SQLite (local dev)

---

## 🧩 Data Model (ERD)

```
Hero <1----*> HeroPower <*----1> Power
```

### Tables

**Hero**
- `id` (PK, int)
- `name` (str)
- `super_name` (str)
- Relationship: `hero_powers` (list of `HeroPower`)

**Power**
- `id` (PK, int)
- `name` (str)
- `description` (str, **required**, **>= 20 chars**)
- Relationship: `hero_powers` (list of `HeroPower`)

**HeroPower**
- `id` (PK, int)
- `strength` (str, one of **'Strong'**, **'Weak'**, **'Average'**)
- `hero_id` (FK -> Hero.id, **on delete cascade**)
- `power_id` (FK -> Power.id, **on delete cascade**)
- Belongs to: `hero`, `power`

> Implement cascade in SQLAlchemy via `ForeignKey('heroes.id', ondelete='CASCADE')` and relationship options (`cascade='all, delete-orphan'` on parent side as needed).

---

## ✅ Validations

- `Power.description`: **required** and **minimum length = 20** characters.
- `HeroPower.strength`: must be **'Strong'**, **'Weak'**, or **'Average'**.

Recommended patterns:
- Validate in model `@validates` or in route before commit.
- Return **422 Unprocessable Entity** (or 400) with:
  ```json
  { "errors": ["validation errors"] }
  ```

---

## 🧰 Project Structure (suggested)

```
.
├─ app.py                # Flask app + routes
├─ models.py             # SQLAlchemy models and validations
├─ migrations/           # Alembic migrations (auto-created by Flask-Migrate)
├─ seed.py               # Seed script (or use provided seed)
├─ requirements.txt
└─ README.md
```

---

## 🚀 Setup & Run

1) **Clone & enter project**
```bash
git clone <your-repo-url>
cd <your-repo>
```

2) **Create & activate venv**
```bash
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

3) **Install dependencies**
```bash
pip install -r requirements.txt
```

4) **Set Flask env vars (dev)**
```bash
# macOS/Linux
export FLASK_APP=app.py
export FLASK_ENV=development
# Windows (PowerShell)
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
```

5) **Initialize DB & migrations**
```bash
flask db init        # first time only
flask db migrate -m "init"
flask db upgrade
```

6) **Seed data**
- If the provided seed file doesn't work, create your own seed script.
```bash
python seed.py
```

7) **Run the server**
```bash
flask run
# App runs at http://127.0.0.1:5000
```

---

## 🔗 Serialization Tips

Use `to_dict()` and **limit recursion** by selecting only needed fields, e.g.:
```python
hero.to_dict(only=('id', 'name', 'super_name'))
```
or include nested, but controlled, relationships:
```python
hero_power.to_dict(
  only=('id','hero_id','power_id','strength'),
  rules={'-hero.hero_powers': True, '-power.hero_powers': True}
)
```

> Be careful to avoid circular nesting (Hero -> HeroPower -> Hero -> ...).

---

## 📚 API Reference

### a) `GET /heroes`
Returns all heroes.
**200 OK**
```json
[
  { "id": 1, "name": "Kamala Khan", "super_name": "Ms. Marvel" },
  { "id": 2, "name": "Doreen Green", "super_name": "Squirrel Girl" }
]
```

### b) `GET /heroes/:id`
Returns a single hero (with hero_powers and nested power).
**200 OK**
```json
{
  "id": 1,
  "name": "Kamala Khan",
  "super_name": "Ms. Marvel",
  "hero_powers": [
    {
      "hero_id": 1,
      "id": 1,
      "power": {
        "description": "gives the wielder the ability to fly through the skies at supersonic speed",
        "id": 2,
        "name": "flight"
      },
      "power_id": 2,
      "strength": "Strong"
    }
  ]
}
```
**404 Not Found**
```json
{ "error": "Hero not found" }
```

### c) `GET /powers`
**200 OK**
```json
[
  {
    "description": "gives the wielder super-human strengths",
    "id": 1,
    "name": "super strength"
  },
  {
    "description": "gives the wielder the ability to fly through the skies at supersonic speed",
    "id": 2,
    "name": "flight"
  }
]
```

### d) `GET /powers/:id`
**200 OK**
```json
{ "description": "gives the wielder super-human strengths", "id": 1, "name": "super strength" }
```
**404 Not Found**
```json
{ "error": "Power not found" }
```

### e) `PATCH /powers/:id`
**Request Body**
```json
{ "description": "Valid Updated Description" }
```
**200 OK (on success)**
```json
{ "description": "Valid Updated Description", "id": 1, "name": "super strength" }
```
**404 Not Found**
```json
{ "error": "Power not found" }
```
**422 Unprocessable Entity (or 400)**
```json
{ "errors": ["validation errors"] }
```

### f) `POST /hero_powers`
**Request Body**
```json
{ "strength": "Average", "power_id": 1, "hero_id": 3 }
```
**201 Created (on success)**
```json
{
  "id": 11,
  "hero_id": 3,
  "power_id": 1,
  "strength": "Average",
  "hero": { "id": 3, "name": "Gwen Stacy", "super_name": "Spider-Gwen" },
  "power": { "description": "gives the wielder super-human strengths", "id": 1, "name": "super strength" }
}
```
**422 Unprocessable Entity (or 400)**
```json
{ "errors": ["validation errors"] }
```

---

## 🧪 Quick Test (curl)

```bash
# All heroes
curl http://127.0.0.1:5000/heroes

# Single hero
curl http://127.0.0.1:5000/heroes/1

# All powers
curl http://127.0.0.1:5000/powers

# Single power
curl http://127.0.0.1:5000/powers/1

# Update power (description must be >= 20 chars)
curl -X PATCH http://127.0.0.1:5000/powers/1   -H "Content-Type: application/json"   -d '{"description":"This is a valid long description."}'

# Create hero_power (strength must be Strong/Weak/Average)
curl -X POST http://127.0.0.1:5000/hero_powers   -H "Content-Type: application/json"   -d '{"strength":"Average","power_id":1,"hero_id":3}'
```

---

## 🧭 Implementation Notes

- **Cascade deletes**: configure FK with `ondelete='CASCADE'` and set relationship cascades, then enforce PRAGMA for SQLite if needed:
  ```sql
  PRAGMA foreign_keys = ON;
  ```
- **Validation errors**: collect messages and return the exact error envelope:
  ```json
  { "errors": ["validation errors"] }
  ```
- **Status codes**:
  - 200 OK (reads, successful update)
  - 201 Created (new `HeroPower`)
  - 404 Not Found (missing `Hero`/`Power`)
  - 400/422 for validation issues

---

## 📦 Seed Data

If the provided seed file fails, create your own `seed.py` inserting a few `Hero`, `Power`, then link with `HeroPower`. Ensure descriptions are >= 20 characters and strengths are valid.

---

## 📄 License

MIT (or your choice).
