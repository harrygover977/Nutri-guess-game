import json
from collections import Counter

# Load your JSON file
with open("data/foods.json", "r", encoding="utf-8") as file:
    foods = json.load(file)

# Extract all food names (assuming each food item has a 'name' key)
food_names = [food["name"] for food in foods]

# Count occurrences of each food name
name_counts = Counter(food_names)

# Find duplicates (names with count > 1)
duplicates = [name for name, count in name_counts.items() if count > 1]

if duplicates:
    print("Duplicate food names found:")
    for name in duplicates:
        print(name)
else:
    print("No duplicates found.")
