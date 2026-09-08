"""Starter recipes, so a fresh database is not an empty page.

The overlap is deliberate: several recipes below share ingredients such as
olive oil and black pepper. Each of those names is stored once in the
`ingredients` table, which is the point of the join table.
"""

import db as database

RECIPES = [
    {
        "name": "Classic Spaghetti Carbonara",
        "image_url": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800",
        "servings": "Serves 2",
        "ingredients": [
            {"quantity": "200 g", "name": "spaghetti"},
            {"quantity": "100 g", "name": "pancetta"},
            {"quantity": "2", "name": "eggs"},
            {"quantity": "50 g", "name": "pecorino cheese"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "directions": [
            "Bring a large pot of salted water to a boil and cook the spaghetti until al dente.",
            "While the pasta cooks, fry the pancetta over medium heat until crisp.",
            "Whisk the eggs and grated pecorino together in a bowl.",
            "Drain the pasta and combine it with the pancetta off the heat.",
            "Stir in the egg mixture quickly so it turns silky, not scrambled.",
            "Season with black pepper and serve at once.",
        ],
    },
    {
        "name": "Sheet-Pan Lemon Chicken",
        "image_url": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=800",
        "servings": "Serves 4",
        "ingredients": [
            {"quantity": "4", "name": "chicken thighs"},
            {"quantity": "2 tbsp", "name": "olive oil"},
            {"quantity": "1", "name": "lemon"},
            {"quantity": "3 cloves", "name": "garlic"},
            {"quantity": "400 g", "name": "baby potatoes"},
            {"quantity": "to taste", "name": "black pepper"},
        ],
        "directions": [
            "Heat the oven to 220 C.",
            "Halve the potatoes and toss them with olive oil, crushed garlic, and black pepper.",
            "Nestle the chicken thighs among the potatoes on a sheet pan.",
            "Squeeze the lemon over everything and tuck the spent halves into the pan.",
            "Roast for 35 minutes, until the skin is browned and the potatoes are tender.",
        ],
    },
    {
        "name": "Chana Masala",
        "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=800",
        "servings": "Serves 4",
        "ingredients": [
            {"quantity": "2 cans", "name": "chickpeas"},
            {"quantity": "1", "name": "onion"},
            {"quantity": "3 cloves", "name": "garlic"},
            {"quantity": "1 tbsp", "name": "ginger"},
            {"quantity": "400 g", "name": "canned tomatoes"},
            {"quantity": "2 tsp", "name": "garam masala"},
            {"quantity": "2 tbsp", "name": "olive oil"},
        ],
        "directions": [
            "Heat the olive oil and cook the diced onion until it turns golden.",
            "Add the minced garlic and ginger and cook for one more minute.",
            "Stir in the garam masala and let it bloom for thirty seconds.",
            "Add the tomatoes and simmer for ten minutes, until the sauce thickens.",
            "Add the drained chickpeas and simmer for another ten minutes.",
        ],
    },
]


def seed():
    """Load the starter recipes. Assumes the tables already exist."""
    for recipe in RECIPES:
        database.create_recipe(
            recipe["name"],
            recipe["image_url"],
            recipe["servings"],
            recipe["ingredients"],
            recipe["directions"],
        )
    return len(RECIPES)
