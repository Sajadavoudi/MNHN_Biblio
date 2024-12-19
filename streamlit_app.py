import streamlit as st
from datetime import date
import os
import json
from Sprynger_2 import fetch_and_store_articles
from OpenAI_FirsLayer import process_json_file as process_first_layer
from OpenAI_SecondLayer import process_second_layer
from OpenAI_ThirdLayer import process_specimen_validation
from pyzotero import zotero

table = False

# App title
st.title("Muséum National d'Histoire Naturelle - Bibliométrie")

# Editor selection
editor = st.selectbox("Select Editor", ["Springer"])

# API keys and configuration
default_openai_api_key = "sk-proj-MqTgp-VLJYzAY2jHjCF6u9o9k28mrU5Ia2onDinZnC6J84Y5ttjCJtogE93ivrLNqL_C7Kd2rjT3BlbkFJYwdD80FdBxF8EtjRcpp4H_iqdMMdoEw79RvbDUDybYDRd30vZC_tGNDTyTckakVnobRR8IPRc"
default_springer_api_key = "8c3e7b22f27abe96a693af900ab4e965"
default_zotero_library_id = "15818985"
default_zotero_api_key = "AJ7jW0HWRUufShR3FeO2717h"
######################################SPRINGER####################################
######################################SPRINGER####################################
######################################SPRINGER####################################
######################################SPRINGER####################################
if editor == "Springer":
    st.header("Springer Article Fetcher")

    # Springer parameters
    springer_api_key = st.text_input("Springer API Key", value=default_springer_api_key, type="password")
    date_from = st.date_input("Start Date", value=date(2023, 1, 1))
    date_to = st.date_input("End Date", value=date(2023, 1, 30))
    keywords_input = st.text_area("Keywords (comma-separated)", value="Muséum National d’Histoire Naturelle, MNHN, Museum National d’Histoire Naturelle, National Museum of Natural History")
    num_results = st.number_input("Number of Results", min_value=1, value=100)
    output_folder = st.text_input("Output Folder Name", value="output_folder")
    output_file = st.text_input("Output JSON File Name", value="articles.json")

    # Convert user inputs into proper formats
    keywords = [keyword.strip() for keyword in keywords_input.split(",")]
    query = " OR ".join(keywords)

    # Fetch articles
    if st.button("Fetch Articles"):
        if not springer_api_key:
            st.error("Springer API Key is required.")
        elif not output_folder:
            st.error("Output folder name is required.")
        else:
            st.info("Fetching articles... Please wait.")
            try:
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                fetch_and_store_articles(
                    query=query,
                    datefrom=date_from.strftime("%Y-%m-%d"),
                    dateto=date_to.strftime("%Y-%m-%d"),
                    nb=num_results,
                    json_file=output_file,
                    folder_name=output_folder
                )
                # Provide download access for the JSON file
                if os.path.exists(os.path.join(output_folder, output_file)):
                    with open(os.path.join(output_folder, output_file), "rb") as json_file:
                        st.download_button(
                            label="Download JSON File",
                            data=json_file,
                            file_name=output_file,
                            mime="application/json"
                            )

                # Provide download access for the JSON file
                st.success(f"Articles fetched and stored in '{os.path.join(output_folder, output_file)}'.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

######################################OPENAI####################################
######################################OPENAI####################################
######################################OPENAI####################################
######################################OPENAI####################################
# OpenAI layers processing
st.header("OpenAI Layered Processing")

# OpenAI parameters
openai_api_key = st.text_input("OpenAI API Key (Add an A)", value=default_openai_api_key, type="password")

if st.button("Process OpenAI Layers"):
    if not openai_api_key:
        st.error("OpenAI API Key is required.")
    else:
        try:
            # Define paths
            first_layer_file = os.path.join(output_folder, "first_layer_" + output_file)
            second_layer_file = os.path.join(output_folder, "second_layer_" + output_file)
            third_layer_file = os.path.join(output_folder, "third_layer_" + output_file)

            # Process layers
            process_first_layer(input_file=os.path.join(output_folder, output_file), output_file=first_layer_file)
            st.success(f"First layer processing completed. Output: {first_layer_file}")
            # Provide download access for the JSON file
            if os.path.exists(os.path.join(output_folder, output_file)):
                with open(os.path.join(output_folder, output_file), "rb") as json_file:
                    st.download_button(
                        label="Download JSON File",
                        data=json_file,
                        file_name=first_layer_file,
                        mime="application/json"
                        )
            process_second_layer(input_json=first_layer_file, output_json=second_layer_file)
            st.success(f"Second layer processing completed. Output: {second_layer_file}")
            # Provide download access for the JSON file
            if os.path.exists(os.path.join(output_folder, output_file)):
                with open(os.path.join(output_folder, output_file), "rb") as json_file:
                    st.download_button(
                        label="Download JSON File",
                        data=json_file,
                        file_name=second_layer_file,
                        mime="application/json"
                        )
            process_specimen_validation(input_file=second_layer_file, output_file=third_layer_file)
            # Provide download access for the JSON file
            if os.path.exists(os.path.join(output_folder, output_file)):
                with open(os.path.join(output_folder, output_file), "rb") as json_file:
                    st.download_button(
                        label="Download JSON File",
                        data=json_file,
                        file_name=third_layer_file,
                        mime="application/json"
                        )
            #table = True
            st.success(f"Third layer processing completed. Output: {third_layer_file}")

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")

######################################TABLE####################################
######################################TABLE####################################
######################################TABLE####################################
######################################TABLE####################################

# Table Navigation and Editing
if table:
    with open(third_layer_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    current_index = st.session_state.current_index
    if data:
        # Display current article data in editable form
        article = data[current_index]
        st.subheader(f"Article {current_index + 1} of {len(data)}")
        
        # Editable fields
        title = st.text_input("Title", value=article.get("title", ""))
        paragraphs = st.text_area("Paragraphs (one per line)", value="\n".join(article.get("paragraphs", [])))
        # url = st.text_input("URL", value=article.get("url", ""))
        # tags = st.text_input("Tags (comma-separated)", value=", ".join(article.get("tags", [])))
        # specimen_names = st.text_input("Specimen Names (comma-separated)", value=", ".join(article.get("specimen_names", [])))

        # Validated specimens table
        st.write("Validated Specimens:")
        validated_specimens = article.get("validated_specimens", [])
        edited_validated_specimens = []

        for i, specimen in enumerate(validated_specimens):
            st.write(f"Specimen {i + 1}")
            name = st.text_input(f"Name (Specimen {i + 1})", value=specimen.get("name", ""))
            category = st.text_input(f"Category (Specimen {i + 1})", value=specimen.get("category", ""))
            subcategory = st.text_input(f"Subcategory (Specimen {i + 1})", value=specimen.get("subcategory", ""))
            edited_validated_specimens.append({"name": name, "category": category, "subcategory": subcategory})

        # Save updates
        if st.button("Save Changes"):
            article["title"] = title
            article["paragraphs"] = paragraphs.split("\n")
            # article["url"] = url
            # article["tags"] = [tag.strip() for tag in tags.split(",")]
            # article["specimen_names"] = [name.strip() for name in specimen_names.split(",")]
            article["validated_specimens"] = edited_validated_specimens

            data[current_index] = article
            with open(third_layer_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            st.success("Changes saved!")

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous", key="prev") and current_index > 0:
                st.session_state.current_index -= 1
        with col2:
            if st.button("Next", key="next") and current_index < len(data) - 1:
                st.session_state.current_index += 1

        # Show a warning message if at the start or end of the data
        if current_index == 0:
            st.warning("You are at the first article.")
        elif current_index == len(data) - 1:
            st.warning("You are at the last article.")

    else:
        st.info("No articles to display. Please process the data first.")


######################################ZOTERO####################################
######################################zOTERO####################################
######################################ZOTERO####################################
######################################ZOTERO####################################

# Zotero Integration
st.header("Zotero Integration")
zotero_library_id = st.text_input("Zotero Library ID", value=default_zotero_library_id)
zotero_api_key = st.text_input("Zotero API Key", value=default_zotero_api_key, type="password")

if st.button("Transfer All to Zotero"):
    try:
        # Ensure third_layer_file exists
        third_layer_file = os.path.join(output_folder, "third_layer_" + output_file)
        if not os.path.exists(third_layer_file):
            st.error("No processed file available. Please run OpenAI Layers first.")
            raise FileNotFoundError("Processed file not found.")

        # Validate Zotero credentials
        try:
            zot = zotero.Zotero(zotero_library_id, "user", zotero_api_key)
            zot.collections()  # Simple call to validate credentials
        except Exception as e:
            st.error("Zotero API validation failed. Please check your credentials.")
            raise e

        # Load final JSON file
        with open(third_layer_file, "r", encoding="utf-8") as file:
            final_data = json.load(file)

        with st.spinner("Transferring data to Zotero..."):
            for article in final_data:
                tags = []  # Reset tags for each article
                title = article.get("title", "No Title")
                url = article.get("url", "No URL")
                validated_specimens = article.get("validated_specimens", [])

                # Extract validated specimens into tags
                for specimen in validated_specimens:
                    name = specimen.get("name", "")
                    category = specimen.get("category", "")
                    subcategory = specimen.get("subcategory", "")

                    # Clean and append tags
                    for element in [name, category, subcategory]:
                        if element:
                            element = element.replace("Correct", "").replace("Valid", "").replace("Confirmation", "").replace("\n", "").replace("Confirmed", "").replace("None", "").strip()
                            if element:
                                tags.append(element)
                                tags.append(editor)

                # Prepare Zotero item
                item = {
                    "itemType": "journalArticle",
                    "title": title,
                    "url": url,
                    "tags": [{"tag": tag} for tag in tags],
                    "date": "-".join(map(str, article.get("date", []))) if article.get("date") else None,
                    "DOI": article.get("doi", ""),
                    "language": article.get("language", ""),
                    "publicationTitle": article.get("journal_title", ""),
                    "ISSN": article.get("ISSN", ""),
                }

                # Add item to Zotero
                response = zot.create_items([item])
                if "successful" in response and response["successful"]:
                    st.success(f"Added '{title}' to Zotero successfully!")
                else:
                    st.warning(f"Failed to add '{title}'. Response: {response}")

    except Exception as e:
        st.error(f"Error transferring articles to Zotero: {e}")
