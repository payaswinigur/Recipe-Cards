# Recipe Cards — Phase 1

A single hardcoded recipe, rendered by a Flask web app. This is step one
of a bigger project — see the roadmap in our conversation for what's next.

## Project structure

```
recipe_cards/
├── app.py                 # Flask application — routes and data
├── templates/
│   └── index.html         # HTML page, using Jinja2 p90emplating
├── static/
│   └── style.css          # Styling for the recipe card
└── README.md
```

## Setup (do this once)

Open a terminal in this folder and run:

```bash
# Create a virtual environment — an isolated Python install just for
# this project, so its packages don't clash with other projects on
# your machine. (Java doesn't really need this because Maven/Gradle
# scope dependencies per-project automatically; Python leaves it to you.)
python3 -m venv venv

# Activate it. You'll need to run this every time you open a new
# terminal to work on the project.
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install Flask into the virtual environment
pip install flask
```

## Running the app

```bash
python3 app.py
```

Then open **http://127.0.0.1:5000** in your browser.

`debug=True` in `app.py` means the server auto-reloads whenever you
save a change to a file — no need to stop and restart it manually
while you're developing.

## What to try

- Change values in the `recipe` dict in `app.py` (add an ingredient,
  change the name) and refresh the browser — no restart needed.
- Open `templates/index.html` and try adding a new field, e.g. a
  "prep_time" key in the dict, and display it on the page.
- Open `static/style.css` and change `--accent` to a different color.
