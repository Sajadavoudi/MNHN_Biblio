import json
import ollama

# Define a short reminder instruction for the model
MODEL_INSTRUCTION = """
Analyze the provided paragraph to identify specimens explicitly mentioned as part of the MNHN of Paris (Muséum National d’Histoire Naturelle of Paris) collections.
Return only and only the specific scientific name(s) of the specimens if mentioned and not its refferal code. If no valid specimens are found, return "None".
"""

# Define function to query the MNHN model
def query_mnhn_model(paragraph):
    """
    Sends a paragraph to the MNHN model using the Ollama library and returns the response.
    """
    try:
        # Combine the instruction with the paragraph for clarity
        prompt = f"{MODEL_INSTRUCTION}\n\nParagraph: {paragraph}"
        print(f"Querying model with prompt:\n{prompt}")  # Debug log
        
        response = ollama.generate(model="MNHN:latest", prompt=prompt)
        print(f"Raw response from model: {response}")  # Debug log

        # Check if response is of the expected type and extract the text
        if hasattr(response, 'response'):  # Adjust this based on the actual response object structure
            resp = response.response.strip()
            print(f"Processed Response: {resp}")  # Debug log
            return resp
        else:
            print(f"Unexpected response type: {type(response)}")
            return None
    except Exception as e:
        print(f"Exception while querying model: {e}")
        return None


# Process JSON file
def process_json_file(input_file, output_file):
    """
    Reads paragraphs from a JSON file, queries the MNHN model, and stores results in a new JSON file.
    Excludes documents where no specimen is mentioned.
    """
    try:
        print(f"Reading input file: {input_file}")  # Debug log
        with open(input_file, "r", encoding="utf-8") as infile:
            data = json.load(infile)
        
        # Validate input JSON structure
        if not isinstance(data, list):
            print("Error: Input JSON should be a list of documents.")
            return

        # List to store results for the new JSON file
        filtered_data = []

        # Iterate over each document and query the model
        for document in data:
            print(f"Processing document: {document}")  # Debug log
            paragraphs = document.get("paragraphs", [])
            if not isinstance(paragraphs, list):
                print("Warning: 'paragraphs' should be a list. Skipping document.")
                continue
            
            specimen_names = []

            for paragraph in paragraphs:
                response = query_mnhn_model(paragraph)
                if response and response != "None":
                    print(f"Valid Response Found: {response}")  # Debug log
                    if isinstance(response, str):
                        specimen_names.append(response)  # Store the whole response directly

            if specimen_names:
                print(f"Adding specimen names to document: {specimen_names}")  # Debug log
                document["specimen_names"] = specimen_names
                filtered_data.append(document)

        # Save filtered results to a new JSON file
        if not filtered_data:
            print("No valid data to write to the output file.")  # Debug log
        else:
            print(f"Writing filtered data to {output_file}")  # Debug log
            with open(output_file, "w", encoding="utf-8") as outfile:
                json.dump(filtered_data, outfile, ensure_ascii=False, indent=4)
                print(f"Filtered data has been saved to {output_file}.")
    except json.JSONDecodeError as jde:
        print(f"JSON decoding error: {jde}")
    except FileNotFoundError as fnfe:
        print(f"File not found: {fnfe}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example Usage
input_json = "results5.json"  # Input JSON file with original data
output_json = "filtered_results1.json"  # Output JSON file with filtered results
process_json_file(input_json, output_json)
