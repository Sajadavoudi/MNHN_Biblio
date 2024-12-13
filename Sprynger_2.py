# In this version I used both the API and the full text scraping to get more paragraphs

import sprynger
from sprynger import OpenAccess, init
import json
import requests
from bs4 import BeautifulSoup
import os


# Springer API Key
API_KEY = '8c3e7b22f27abe96a693af900ab4e965'

def fetch_and_store_articles(query, datefrom, dateto, nb, json_file, folder_name):
    init(api_key=API_KEY)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Construct the full path for the JSON file
    json_file_path = os.path.join(folder_name, json_file)

    # Fetch results from Springer API
    results = OpenAccess(query, datefrom=datefrom, dateto=dateto, type='Journal Article', nr_results=nb, cache=False)

    print("Number of articles found:", len(results))

    data_store = []

    # Loop through the results
    for document in results:
        if hasattr(document, 'doi'):
            doi = getattr(document, 'doi')
            article_url = f"https://link.springer.com/article/{doi}"

        document_data = {
            "title": document.title,
            "paragraphs": [],
            "url": article_url,
            "tags": ["Springer"],
            "type": document.article_type,
            "date": document.date_epub,
            "doi": document.doi,
            "language": document.language,
            "journal_title": document.journal_title,
            "ISSN": document.issn_print,
            }

            # Process paragraphs from API
        for paragraph in document.paragraphs:
            if any(keyword in paragraph.text for keyword in keywords):
                if paragraph.text not in document_data["paragraphs"]:
                    document_data["paragraphs"].append(paragraph.text)

        # Attempt to scrape full text and add additional paragraphs
        try:
            response = requests.get(article_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                for paragraph in paragraphs:
                    text = paragraph.get_text()
                    if any(keyword.lower() in text.lower() for keyword in keywords):
                        if text not in document_data["paragraphs"]:
                            document_data["paragraphs"].append(text)
        except Exception as e:
            print(f"Error fetching {article_url}: {e}")

        # Add document data to the store if paragraphs are found
        if document_data["paragraphs"]:
            data_store.append(document_data)
            print(f"Stored {len(document_data['paragraphs'])} Paragraphs from {document_data['title']}.")


    # Save all results to JSON
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(data_store, file, ensure_ascii=False, indent=4)

    print(f"Stored {len(data_store)} articles in {json_file}.")
    

# Example Usage
####################
###################
###################

keywords = ["Muséum National d’Histoire Naturelle", "MNHN"]
query = " OR ".join(keywords)  # Combine keywords into a single query
'''
fetch_and_store_articles(
    query=query,
    datefrom='2023-01-01',
    dateto='2023-01-30',
    nb=1,
    json_file="janvier.json",
    folder_name="output_folder"
)
'''

