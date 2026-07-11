"""
app.py — the entry point of our web app.

WHAT IS FLASK?
Flask is a "micro" web framework for Python. "Micro" doesn't mean
"toy" — it means Flask gives you the bare minimum to handle web
requests and leaves the rest up to you. That's actually great for
learning, because you'll see every moving part instead of it being
hidden inside a big framework (this is the opposite of Django, which
bundles in a lot more out of the box).

Coming from Java: there's no equivalent of a servlet container or
Spring Boot config here. You `pip install flask`, write this file,
and run it. That's the whole setup.
"""

from flask import Flask, render_template

# Every Flask app starts by creating an instance of the Flask class.
# `__name__` is a built-in Python variable that holds the name of the
# current module — Flask uses it to figure out where this file lives,
# so it knows where to look for the templates/ and static/ folders.
app = Flask(__name__)


# --- Python concept: the dictionary (dict) ---
# A dict maps keys to values. It's Python's equivalent of Java's
# HashMap<String, Object> but without declaring types, and with much
# lighter syntax: {} instead of `new HashMap<>()`.
#
# Notice `ingredients` and `directions` are lists (Python's equivalent
# of ArrayList) *nested inside* the dict. Structures like this — dicts
# containing lists containing strings — are extremely common in Python,
# and this exact shape is what JSON looks like too (that becomes
# relevant in Phase 2).
recipe = {
    "name": "Classic Spaghetti Carbonara",
    "image_url": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800",
    "ingredients": [
        "200g spaghetti",
        "100g pancetta, diced",
        "2 large eggs",
        "50g pecorino cheese, grated",
        "Freshly cracked black pepper",
    ],
    "directions": [
        "Bring a large pot of salted water to a boil and cook the spaghetti until al dente.",
        "While the pasta cooks, fry the pancetta in a pan over medium heat until crisp.",
        "In a bowl, whisk the eggs and grated pecorino together.",
        "Drain the pasta, then combine it with the pancetta off the heat.",
        "Quickly stir in the egg mixture so it turns silky, not scrambled. Season with black pepper.",
    ],
}


# --- Python concept: decorators ---
# The line `@app.route("/")` is a *decorator*. It takes the function
# defined right below it and wraps extra behavior around it — in this
# case, "register this function to run whenever someone visits the
# '/' URL." Decorators are a Python feature Java doesn't really have
# an equivalent for; annotations like @Override are the closest
# comparison, but Python decorators actually execute code.
@app.route("/")
def home():
    # `render_template` looks inside the templates/ folder by
    # convention and renders index.html, passing our `recipe` dict
    # in so the HTML can use it. This keeps HTML out of our Python
    # code — a separation of concerns you already know from MVC-style
    # thinking in Java web frameworks.
    return render_template("index.html", recipe=recipe)


# --- Python concept: the __main__ guard ---
# This block only runs when you execute this file *directly*
# (e.g. `python app.py`), not when it's imported by something else.
# It's Python's loose equivalent of Java's `public static void main`,
# except every .py file can have one, and it's opt-in rather than
# required.
if __name__ == "__main__":
    app.run(debug=True)
