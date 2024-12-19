import openai
import json

# OpenAI API key
openai_api_key = ""
openai.api_key = openai_api_key

# OpenAI Prompt Template
PROMPT_TEMPLATE = """
You are an expert in biology and museum collections. Given the specimen name below, classify it into one of these categories and subcategories:

1. Géologie:
    - Minéralogie
    - Météorites
    - Roches océaniques

2. Paléontologie

3. Botanique

4. Invertébrés non arthropodes terrestres:
    - Mollusques
    - Crustacés
    - Cnidaires
    - Briozoaires/Brachiopodes
    - Porifera
    - Echinodermes
    - Vers
    - Polychètes
    - Meiofaune
    - Protistes

5. Arthropodes terrestres:
    - Coléoptères
    - Lépidoptères
    - Arachnides
    - Hémiptères
    - Hyménoptères
    - Diptères
    - Odonates

6. Vertébrés:
    - Mammifères
    - Oiseaux
    - Reptiles et amphibiens
    - Ichtyologie

7. Préhistoire

8. Ressources biologiques:
    - Cyanobactéries et microalgues eucaryotes
    - Souches fongiques
    - Eucaryotes unicellulaires
    - Tissus et cellules de vertébrés
    - Chimiothèque

9. Animaux vivants:
    - PZP
    - Ménagerie

10. Végétaux vivants

11. Anthropologie

Task:
- If the input is a valid specimen name, return the best-matching category and subcategory (if applicable) in the format: "Category, Subcategory".
- If the input is not a valid specimen name, return "None".
- Do not provide explanations or additional text.

Specimen: {specimen}
"""

def classify_specimen(specimen_name):
    """
    Sends a specimen name to OpenAI GPT for classification into predefined categories and subcategories.
    """
    try:
        prompt = PROMPT_TEMPLATE.format(specimen=specimen_name)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result = response.choices[0].message['content'].strip()
        return result
    except Exception as e:
        print(f"Error during OpenAI classification: {e}")
        return None

def process_second_layer(input_json, output_json):
    """
    Processes a JSON file of documents to classify specimen names into categories and subcategories.

    Parameters:
    - input_json: Path to the input JSON file containing documents with specimen names.
    - output_json: Path to save the processed JSON file with classified specimens.
    """
    try:
        # Load the input JSON file
        with open(input_json, "r", encoding="utf-8") as infile:
            data = json.load(infile)

        # Prepare the processed data list
        processed_data = []

        for article in data:
            specimen_names = article.get("specimen_names", [])
            specimen_categories = []

            for specimen in specimen_names:
                category_subcategory = classify_specimen(specimen)
                if category_subcategory and category_subcategory != "None":
                    specimen_categories.append(category_subcategory)

            # Only store articles with valid classifications
            if specimen_categories:
                article["First_category"] = specimen_categories
                processed_data.append(article)

        # Save the results to the output JSON file
        with open(output_json, "w", encoding="utf-8") as outfile:
            json.dump(processed_data, outfile, ensure_ascii=False, indent=4)

        print(f"Processed data saved to '{output_json}'.")
    except Exception as e:
        print(f"Error processing specimens: {e}")

'''
# Example Usage
input_json = "first_Layer_janvier.json"  # Input JSON file
output_json = "second_layer_janvier.json"  # Output JSON file
process_second_layer(input_json, output_json)
'''
