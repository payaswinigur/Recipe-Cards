"""Database access for Digital Recipe Cards.

Every SQL statement in the project lives here, so the route handlers in
app.py stay about HTTP and the queries stay testable on their own.
"""

import sqlite3
from pathlib import Path

from flask import current_app, g

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"


# --------------------------------------------------------------------------
# connection handling
# --------------------------------------------------------------------------

def get_db():
    """Return this request's connection, opening one if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        # SQLite leaves foreign keys off unless you ask, per connection.
        # Without this the ON DELETE CASCADE rules never fire.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tables. Drops anything already there."""
    db = get_db()
    db.executescript(SCHEMA_PATH.read_text())
    db.commit()


def is_initialized():
    """True if the schema has already been created in this database file."""
    row = get_db().execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'recipes'"
    ).fetchone()
    return row is not None


# --------------------------------------------------------------------------
# reads
# --------------------------------------------------------------------------

def list_recipes(search=None):
    """All recipes, newest first.

    A search term matches either the recipe name or any ingredient it uses.
    Matching on ingredients is the payoff of the join table: "pancetta"
    finds every recipe using it without storing the word more than once.
    """
    db = get_db()
    if not search:
        return db.execute(
            "SELECT id, name, image_url, servings FROM recipes ORDER BY id DESC"
        ).fetchall()

    like = f"%{search}%"
    return db.execute(
        """
        SELECT DISTINCT r.id, r.name, r.image_url, r.servings
          FROM recipes r
          LEFT JOIN recipe_ingredients ri ON ri.recipe_id = r.id
          LEFT JOIN ingredients i         ON i.id = ri.ingredient_id
         WHERE r.name LIKE ? OR i.name LIKE ?
         ORDER BY r.id DESC
        """,
        (like, like),
    ).fetchall()


def get_recipe(recipe_id):
    """One recipe with its ingredients and directions, or None."""
    db = get_db()
    recipe = db.execute(
        "SELECT id, name, image_url, servings FROM recipes WHERE id = ?",
        (recipe_id,),
    ).fetchone()
    if recipe is None:
        return None

    ingredients = db.execute(
        """
        SELECT ri.quantity, i.name
          FROM recipe_ingredients ri
          JOIN ingredients i ON i.id = ri.ingredient_id
         WHERE ri.recipe_id = ?
         ORDER BY ri.position
        """,
        (recipe_id,),
    ).fetchall()

    directions = db.execute(
        """
        SELECT step_number, instruction
          FROM directions
         WHERE recipe_id = ?
         ORDER BY step_number
        """,
        (recipe_id,),
    ).fetchall()

    return {"recipe": recipe, "ingredients": ingredients, "directions": directions}


def count_recipes_using(ingredient_name):
    """How many recipes use this ingredient. Shows why the join table earns its keep."""
    db = get_db()
    row = db.execute(
        """
        SELECT COUNT(DISTINCT ri.recipe_id) AS n
          FROM recipe_ingredients ri
          JOIN ingredients i ON i.id = ri.ingredient_id
         WHERE i.name = ?
        """,
        (ingredient_name,),
    ).fetchone()
    return row["n"]


# --------------------------------------------------------------------------
# writes
# --------------------------------------------------------------------------

def _intern_ingredient(db, name):
    """Return the id for an ingredient name, inserting it only if new.

    This is what keeps the ingredients table free of duplicates. The UNIQUE
    COLLATE NOCASE constraint means "Pancetta" and "pancetta" resolve to the
    same row.
    """
    name = name.strip()
    row = db.execute("SELECT id FROM ingredients WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cur = db.execute("INSERT INTO ingredients (name) VALUES (?)", (name,))
    return cur.lastrowid


def _replace_children(db, recipe_id, ingredients, directions):
    """Rewrite a recipe's ingredient and direction rows.

    Called by both create and update so the two paths cannot drift apart.
    """
    db.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
    db.execute("DELETE FROM directions WHERE recipe_id = ?", (recipe_id,))

    seen = set()
    position = 0
    for item in ingredients:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        ingredient_id = _intern_ingredient(db, name)
        # PRIMARY KEY (recipe_id, ingredient_id) forbids listing the same
        # ingredient twice on one recipe, so skip a repeat rather than crash.
        if ingredient_id in seen:
            continue
        seen.add(ingredient_id)
        db.execute(
            """
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, position)
            VALUES (?, ?, ?, ?)
            """,
            (recipe_id, ingredient_id, (item.get("quantity") or "").strip(), position),
        )
        position += 1

    step = 1
    for instruction in directions:
        instruction = (instruction or "").strip()
        if not instruction:
            continue
        db.execute(
            "INSERT INTO directions (recipe_id, step_number, instruction) VALUES (?, ?, ?)",
            (recipe_id, step, instruction),
        )
        step += 1


def create_recipe(name, image_url, servings, ingredients, directions):
    """Insert a recipe and its children in one transaction. Returns the new id."""
    db = get_db()
    with db:  # commits on success, rolls back on any exception
        cur = db.execute(
            "INSERT INTO recipes (name, image_url, servings) VALUES (?, ?, ?)",
            (name.strip(), (image_url or "").strip(), (servings or "").strip()),
        )
        recipe_id = cur.lastrowid
        _replace_children(db, recipe_id, ingredients, directions)
    return recipe_id


def update_recipe(recipe_id, name, image_url, servings, ingredients, directions):
    """Update a recipe and rewrite its children. Returns True if the recipe existed."""
    db = get_db()
    with db:
        cur = db.execute(
            "UPDATE recipes SET name = ?, image_url = ?, servings = ? WHERE id = ?",
            (name.strip(), (image_url or "").strip(), (servings or "").strip(), recipe_id),
        )
        if cur.rowcount == 0:
            return False
        _replace_children(db, recipe_id, ingredients, directions)
    return True


def delete_recipe(recipe_id):
    """Delete a recipe. ON DELETE CASCADE removes its ingredients and directions."""
    db = get_db()
    with db:
        cur = db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    return cur.rowcount > 0


def prune_orphan_ingredients():
    """Remove ingredient names no recipe uses any more.

    ON DELETE RESTRICT protects an ingredient while a recipe still points at
    it, so this runs after deletes to keep the table from growing forever.
    """
    db = get_db()
    with db:
        db.execute(
            """
            DELETE FROM ingredients
             WHERE id NOT IN (SELECT ingredient_id FROM recipe_ingredients)
            """
        )
