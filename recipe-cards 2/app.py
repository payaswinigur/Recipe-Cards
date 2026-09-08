"""Digital Recipe Cards — a Flask CRUD app over a normalized SQLite database.

Routes:
    GET   /                       list every recipe, with search
    GET   /recipe/<id>            one recipe card
    GET   /recipe/new             blank form
    POST  /recipe/new             create
    GET   /recipe/<id>/edit       form filled with existing values
    POST  /recipe/<id>/edit       update
    POST  /recipe/<id>/delete     delete
"""

import os
from pathlib import Path

from flask import (
    Flask, abort, flash, redirect, render_template, request, url_for
)

import db as database
import seed as seeder

BASE_DIR = Path(__file__).resolve().parent


def create_app(database_path=None):
    app = Flask(__name__)
    app.config["DATABASE"] = database_path or str(BASE_DIR / "recipes.db")
    # Only used to sign flash-message cookies. Set a real value in the
    # environment before running anywhere but your own machine.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-not-a-secret")

    app.teardown_appcontext(database.close_db)

    # ---------------------------------------------------------------- read

    @app.route("/")
    def index():
        search = (request.args.get("q") or "").strip()
        recipes = database.list_recipes(search or None)
        return render_template("index.html", recipes=recipes, search=search)

    @app.route("/recipe/<int:recipe_id>")
    def detail(recipe_id):
        data = database.get_recipe(recipe_id)
        if data is None:
            abort(404)
        return render_template("detail.html", **data)

    # -------------------------------------------------------------- create

    @app.route("/recipe/new", methods=["GET", "POST"])
    def create():
        if request.method == "GET":
            return render_template("form.html", recipe=None, ingredients=[], directions=[])

        form = _read_form(request.form)
        error = _validate(form)
        if error:
            flash(error, "error")
            return render_template("form.html", recipe=form, **_echo(form)), 400

        recipe_id = database.create_recipe(
            form["name"], form["image_url"], form["servings"],
            form["ingredients"], form["directions"],
        )
        flash(f"Added “{form['name']}”.", "success")
        return redirect(url_for("detail", recipe_id=recipe_id))

    # -------------------------------------------------------------- update

    @app.route("/recipe/<int:recipe_id>/edit", methods=["GET", "POST"])
    def edit(recipe_id):
        data = database.get_recipe(recipe_id)
        if data is None:
            abort(404)

        if request.method == "GET":
            return render_template(
                "form.html",
                recipe=data["recipe"],
                ingredients=data["ingredients"],
                directions=[d["instruction"] for d in data["directions"]],
            )

        form = _read_form(request.form)
        error = _validate(form)
        if error:
            flash(error, "error")
            return render_template("form.html", recipe=form, **_echo(form)), 400

        database.update_recipe(
            recipe_id, form["name"], form["image_url"], form["servings"],
            form["ingredients"], form["directions"],
        )
        database.prune_orphan_ingredients()
        flash("Changes saved.", "success")
        return redirect(url_for("detail", recipe_id=recipe_id))

    # -------------------------------------------------------------- delete

    @app.route("/recipe/<int:recipe_id>/delete", methods=["POST"])
    def delete(recipe_id):
        if not database.delete_recipe(recipe_id):
            abort(404)
        database.prune_orphan_ingredients()
        flash("Recipe deleted.", "success")
        return redirect(url_for("index"))

    # --------------------------------------------------------------- error

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    # ----------------------------------------------------------- CLI setup

    @app.cli.command("init-db")
    def init_db_command():
        """Create the tables, then load the starter recipes."""
        database.init_db()
        seeder.seed()
        print(f"Initialized {app.config['DATABASE']}")

    return app


# -------------------------------------------------------------------------
# form helpers
# -------------------------------------------------------------------------

def _read_form(form):
    """Turn the posted form into the shape db.py expects.

    Ingredient rows arrive as parallel lists, so quantity[i] pairs with
    name[i]. Directions arrive as one textarea, one step per line.
    """
    quantities = form.getlist("quantity")
    names = form.getlist("ingredient")
    ingredients = [
        {"quantity": q, "name": n}
        for q, n in zip(quantities, names)
        if n.strip()
    ]
    directions = [
        line.strip()
        for line in (form.get("directions") or "").splitlines()
        if line.strip()
    ]
    return {
        "name": (form.get("name") or "").strip(),
        "image_url": (form.get("image_url") or "").strip(),
        "servings": (form.get("servings") or "").strip(),
        "ingredients": ingredients,
        "directions": directions,
    }


def _validate(form):
    """Return an error message, or None if the form is usable."""
    if not form["name"]:
        return "A recipe needs a name."
    if not form["ingredients"]:
        return "A recipe needs at least one ingredient."
    if not form["directions"]:
        return "A recipe needs at least one direction."
    return None


def _echo(form):
    """Re-render the form with what the user typed, so a validation error
    does not throw away their work."""
    return {"ingredients": form["ingredients"], "directions": form["directions"]}


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
