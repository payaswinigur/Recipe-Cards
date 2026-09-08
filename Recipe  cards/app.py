

from flask import Flask, render_template


app = Flask(__name__)


recipe = {
    "name": "Classic Spaghetti Carbonara",
    "image_url": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800",
    "ingredients": [
        {"quantity": "200g", "name": "spaghetti"},
        {"quantity": "100g", "name": "pancetta, diced"},
        {"quantity": "2", "name": "large eggs"},
        {"quantity": "50g", "name": "pecorino cheese, grated"},
        {"quantity": "to taste", "name": "freshly cracked black pepper"},
    ],
    "directions": [
        "Bring a large pot of salted water to a boil and cook the spaghetti until al dente.",
        "While the pasta cooks, fry the pancetta in a pan over medium heat until crisp.",
        "In a bowl, whisk the eggs and grated pecorino together.",
        "Drain the pasta, then combine it with the pancetta off the heat.",
        "Quickly stir in the egg mixture so it turns silky, not scrambled. Season with black pepper.",
    ],
}


@app.route("/")
def home():
    return render_template("index.html", recipe=recipe)


if __name__ == "__main__":
    app.run(debug=True)
