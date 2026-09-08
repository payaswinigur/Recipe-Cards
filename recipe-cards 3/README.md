# Digital Recipe Cards

A Flask web app for creating, editing, and organizing recipes as clean printable
cards, backed by a normalized SQLite database.

The index-card recipe box, moved to the browser — with the things paper cannot
do: search across every recipe you own, including by an ingredient you have
sitting in the fridge.

## Features

- **Full CRUD** — create, read, update, and delete recipes through the browser.
- **Search by recipe or by ingredient** — "garlic" returns every recipe that
  uses it, resolved through a single indexed join.
- **Structured recipe data** — ingredients keep quantity and name in separate
  fields, and directions stay an ordered sequence, so the card layout stays
  correct for a recipe of any length.
- **Server-side validation** that reports what is missing and gives back what
  you already typed instead of clearing the form.

## The schema

Four tables, normalized to third normal form:

```
recipes ──┬── recipe_ingredients ──── ingredients
          └── directions
```

The decision worth explaining is `recipe_ingredients`. Ingredient *names* live
in their own table with a `UNIQUE` constraint, and the join table connects a
name to a recipe along with a quantity.

That means "olive oil" is stored exactly once no matter how many recipes use
it. The alternative — repeating the text on every recipe row — makes
"which recipes use pancetta?" a scan over duplicated strings, and makes a typo
in one row invisible. Here it is an indexed lookup.

Quantity lives on the join row rather than on the ingredient, because 200 g of
spaghetti is a fact about *this recipe's use of* spaghetti, not about spaghetti.

Directions stay a plain child table: a step belongs to exactly one recipe, so
there is nothing to deduplicate and a many-to-many would only add a join.

Two constraints do real work:

- `ON DELETE CASCADE` on both child tables means deleting a recipe removes its
  ingredient links and directions in the same statement — no orphan rows.
- `ON DELETE RESTRICT` on `ingredients` stops a name being deleted while a
  recipe still points at it. `prune_orphan_ingredients()` clears names nothing
  references any more.

SQLite leaves foreign keys **off** by default, per connection, so `db.py` issues
`PRAGMA foreign_keys = ON` on every connection. Without it the cascade rules are
silently inert.

## Running it

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

flask --app app init-db           # create the tables and load starter recipes
flask --app app run --debug
```

Open http://127.0.0.1:5000.

`init-db` drops and recreates the tables, so re-running it resets everything.

## Deploying

This is a Flask app, so it needs a Python process running. GitHub Pages serves
static files only and cannot host it.

It is set up for [Render](https://render.com) via `render.yaml`:

1. Push this repo to GitHub.
2. On Render: **New → Blueprint**, pick the repo, **Apply**.
3. Render reads `render.yaml`, installs the dependencies, and starts gunicorn.

The free tier has an ephemeral disk, so `DATABASE_PATH` points at `/tmp` and
`create_app()` builds and seeds the database on startup whenever the file is
missing. A restart therefore restores the starter recipes rather than serving an
empty page. That is deliberate for a public demo: anyone can try the delete
button, and the site repairs itself.

Gunicorn runs a single worker with four threads. SQLite is one file, and
multiple worker processes writing to it produce "database is locked" errors;
threads give the concurrency without the contention.

For persistent data instead, attach a Render disk and point `DATABASE_PATH` at
it, or deploy to a host with a persistent filesystem.

## Layout

```
app.py           routes and form handling
db.py            every SQL statement in the project
schema.sql       table definitions, constraints, indexes
seed.py          starter recipes
templates/       Jinja templates (base, index, detail, form, 404)
static/style.css hand-written CSS, no framework
```

SQL is kept out of the route handlers entirely: `app.py` is about HTTP, `db.py`
is about data. Create and update share one `_replace_children()` helper so the
two write paths cannot drift apart.

## Built with

Python · Flask · SQLite · Jinja2 · SQL · HTML · CSS
