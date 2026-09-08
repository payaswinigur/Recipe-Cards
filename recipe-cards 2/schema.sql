-- Digital Recipe Cards — schema
--
-- Normalized to third normal form across four tables.
--
-- The design decision worth explaining: ingredient NAMES live in their own
-- table, and `recipe_ingredients` joins them to a recipe with a quantity.
-- "olive oil" is therefore stored exactly once no matter how many recipes
-- use it. That is what makes questions like "which recipes use pancetta?"
-- a single indexed join instead of a scan over repeated text.
--
-- Quantity belongs on the join row, not on the ingredient: 200g of
-- spaghetti is a fact about this recipe's use of spaghetti, not about
-- spaghetti itself.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS directions;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipes;

CREATE TABLE recipes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    image_url   TEXT,
    servings    TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One row per distinct ingredient name, ever.
CREATE TABLE ingredients (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE COLLATE NOCASE
);

-- Join table: which ingredients a recipe uses, in how much, in what order.
CREATE TABLE recipe_ingredients (
    recipe_id      INTEGER NOT NULL REFERENCES recipes(id)     ON DELETE CASCADE,
    ingredient_id  INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    quantity       TEXT,
    position       INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id)
);

-- Directions are ordered and belong to exactly one recipe, so they stay a
-- child table rather than a many-to-many.
CREATE TABLE directions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id    INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    step_number  INTEGER NOT NULL,
    instruction  TEXT NOT NULL,
    UNIQUE (recipe_id, step_number)
);

CREATE INDEX idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);
CREATE INDEX idx_directions_recipe             ON directions(recipe_id, step_number);
CREATE INDEX idx_recipes_name                  ON recipes(name);
