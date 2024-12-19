import openai
import json

# OpenAI API key
#openai.api_key = "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"

# Predefined categories and subcategories
CATEGORY_SUBCATEGORY_MAPPING = {
    "Géologie": ["Minéralogie", "Météorites", "Roches océaniques"],
    "Paléontologie": [],
    "Botanique": [],
    "Invertébrés non arthropodes terrestres": [
        "Mollusques", "Crustacés", "Cnidaires", "Briozoaires/Brachiopodes", "Porifera",
        "Echinodermes", "Vers", "Polychètes", "Meiofaune", "Protistes"
    ],
    "Arthropodes terrestres": [
        "Coléoptères", "Lépidoptères", "Arachnides", "Hémiptères", "Hyménoptères", "Diptères", "Odonates"
    ],
    "Vertébrés": ["Mammifères", "Oiseaux", "Reptiles et amphibiens", "Ichtyologie"],
    "Préhistoire": [],
    "Ressources biologiques": [
        "Cyanobactéries et microalgues eucaryotes", "Souches fongiques", "Eucaryotes unicellulaires",
        "Tissus et cellules de vertébrés", "Chimiothèque"
    ],
    "Animaux vivants": ["PZP", "Ménagerie"],
    "Végétaux vivants": [],
    "Anthropologie": []
}

# OpenAI Prompt Template
PROMPT_TEMPLATE = """
You are a taxonomy and biology expert. Verify the provided specimen name, category, and subcategory. If the specimen aligns with the given category and subcategory, confirm it by giving the same thin out. If not, provide the corrected category and subcategory.

Categories and subcategories:
{categories}

Input:
Specimen Name: {name}
Category: {category}
Subcategory: {subcategory}

Output:
[Specimen Name], [Category], [Subcategory]
"""

# Function to validate specimen names and categories
def validate_specimen(specimen_name, category, subcategory):
    try:
        # Format categories and subcategories for the prompt
        formatted_categories = "\n".join(
            [f"- {cat}: {', '.join(subcats) if subcats else 'None'}" for cat, subcats in CATEGORY_SUBCATEGORY_MAPPING.items()]
        )

        # Prepare the prompt
        prompt = PROMPT_TEMPLATE.format(
            categories=formatted_categories,
            name=specimen_name,
            category=category,
            subcategory=subcategory or "None"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message['content'].strip()

        # Ensure only name, category, and subcategory are returned
        if result.count(",") == 2:
            return result.split(",")  # Return as separate strings
        return None
    except Exception as e:
        print(f"Error validating specimen: {e}")
        return None

# Process JSON file
def process_specimen_validation(input_file, output_file):
    try:
        # Load input JSON
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        validated_data = []

        for article in data:
            specimen_names = article.get("specimen_names", [])
            specimen_categories = article.get("First_category", [])

            clean_specimens = []

            for name, category in zip(specimen_names, specimen_categories):
                subcategory = category.split(",")[-1].strip() if "," in category else "None"
                main_category = category.split(",")[0].strip()

                validation_result = validate_specimen(name, main_category, subcategory)
                if validation_result:
                    clean_specimens.append({
                        "name": validation_result[0].strip(),
                        "category": validation_result[1].strip(),
                        "subcategory": validation_result[2].strip()
                    })

            if clean_specimens:
                article["validated_specimens"] = clean_specimens
                validated_data.append(article)

        # Save validated results to JSON
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(validated_data, file, ensure_ascii=False, indent=4)

        print(f"Validated data saved to '{output_file}'.")
    except Exception as e:
        print(f"Error processing validation: {e}")

'''
# Example usage
input_json = "second_layer_janvier.json"  # Input JSON with specimen names and categories
output_json = "l4411.json"  # Output JSON for validated specimens
process_specimen_validation(input_json, output_json)
'''
