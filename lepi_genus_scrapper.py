from typing import Literal
import requests
from bs4 import BeautifulSoup
from wikipedia import WikipediaPage
import pandas as pd


TaxonomicLevel = Literal["family", "genus"]

try:
    df_dyntaxa = pd.read_csv("../dyntaxa_DB/Taxon.csv", sep="	", encoding="utf-8")

except FileNotFoundError:
    print("File not found. Please check the path to the dataset for the taxon id generation.")
    df_dyntaxa = pd.DataFrame()

import json

try:
    with open("secrets.json") as f:
        secrets = json.load(f)
    api_key = secrets.get("artfakta_api_key")
except FileNotFoundError:
    print("secrets.json file not found. Please create it with your API key.")
    api_key = None

def get_artfakta_id_gen(family_name: str) -> str | None:
    """
    Given a scientific name, extract the numeric Artfakta taxon ID from the dataset.

    Args:
        genus_name (str): Scientific name (e.g., 'Elymus caninus')
        dataset_path (str): Path to CSV with column 'scientificName' and 'taxonId'

    Returns:
        str | None: Taxon ID number (e.g. '222441') or None if not found
    """
    df_dyntaxa["scientificName"] = df_dyntaxa["scientificName"].str.strip().str.lower()
    match = df_dyntaxa[
        (df_dyntaxa["scientificName"].str.strip().str.lower() == family_name.strip().lower()) &
        (df_dyntaxa["taxonRank"].str.strip().str.lower() == "genus")
]    
    if not match.empty:
        full_id = match.iloc[0]["acceptedNameUsageID"]
        if isinstance(full_id, str):
            return full_id.split(":")[-1]  # extract the number part
    return None



def fetch_artfakta_genus_description_api(gen_name: str) -> dict[str, str]:
    """
    Fetches the 'characteristic' field from the Artfakta API using a taxon ID.

    Args:
        taxon_id (str): The numeric taxon ID, e.g., '213903'.
        api_key (str): Your Artfakta API key.

    Returns:
        dict: { 'artfakta.se': genus description from 'characteristic' }
    """
    source_name = "artfakta.se"
    taxon_id = get_artfakta_id_gen(gen_name)
    print(f"Taxon ID for {gen_name}: {taxon_id}")
    if taxon_id is None:   
        return {source_name: ""}

    
    url = f"https://api.artdatabanken.se/information/v1/speciesdataservice/v1/speciesdata/texts?taxa={taxon_id}"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Cache-Control": "no-cache"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(data)
        if not data or not isinstance(data, list) or "speciesData" not in data[0]:
            print(f"[{source_name}] Unexpected API response structure.")
            return {source_name: ""}
        if data[0]["speciesData"].get("characteristic", "") == None:
            print(f"[{source_name}] 'characteristic' field not found in API response.")
            return {source_name: ""}
        else:
            characteristic = data[0]["speciesData"].get("characteristic", "").strip()

        return {source_name: characteristic}

    except requests.RequestException as e:
        print(f"[{source_name}] API request failed: {e}")
        return {source_name: ""}


def fetch_butterflies_and_moths_genus_description(family_name: str) -> dict[str, str]:
    """
    Fetches the family description from butterfliesandmoths.org and returns it in a dictionary.

    Args:
        family_name (str): Name of the family (e.g. 'Hesperiidae').

    Returns:
        dict: Dictionary with the source name as key and extracted description as value.
    """
    source_name = "butterfliesandmoths.org"
    base_url = "https://www.butterfliesandmoths.org/taxonomy/"
    url = f"{base_url}{family_name}"
    result = {}
    #print(url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        description_div = soup.find(
            "div",
            class_="field field-name-body field-type-text-with-summary field-label-hidden"
        )

        if description_div:
            text = description_div.get_text(separator=" ", strip=True)
            result[source_name] = text
        else:
            print(f"[{source_name}] Description not found on page: {url}")
            result[source_name] = ""

    except requests.RequestException as e:
        print(f"[{source_name}] Failed to fetch {url}: {e}")
        result[source_name] = ""

    return result

def fetch_wikipedia_genus_description(family_name: str) -> dict[str, str]:
    """
    Fetches the full Wikipedia content for a given taxonomic family.

    Args:
        family_name (str): Name of the family (e.g. 'Hesperiidae').

    Returns:
        dict: { 'wikipedia.org': description_text }
    """
    source_name = "wikipedia.org"
    try:
        page = WikipediaPage(family_name)
        content = page.content

        # Try to extract only the "Description" section if available
        sections = content.split("\n==")
        for section in sections:
            if "description" in section.lower() and len(section) > 20:
                # Remove the heading line
                lines = section.split("\n")
                return {source_name: "\n".join(lines[1:]).strip()}

        # Fallback: return beginning of full content
        return {source_name: content.strip()}

    except Exception as e:
        print(f"[{source_name}] Failed to fetch page for {family_name}: {e}")
        return {source_name: ""}




def process_by_genus(family_name: str) -> None:
    """
    Process data at the family taxonomic level.

    Args:
        name (str): Name of the family (e.g. 'Formicidae').
    """
    print(f"Processing GENUS: {family_name}")
    all_descriptions = {}
    all_descriptions.update(fetch_butterflies_and_moths_genus_description(family_name))
    all_descriptions.update(fetch_wikipedia_genus_description(family_name))
    all_descriptions.update(fetch_artfakta_genus_description_api(family_name))


    # for source, desc in all_descriptions.items():
    #     print(f"\n--- {source} ---\n{desc[:100]} \ndesc_len:{len(desc)}\n")

    return all_descriptions



def process_taxonomic_level(level: TaxonomicLevel, name: str) -> None:
    """
    Routes processing depending on the selected taxonomic level.

    Args:
        level (str): Either 'family' or 'genus'.
        name (str): Name of the taxonomic group.
    """
    if level == "genus":
        all_descriptions=process_by_genus(name)
    else:
        raise ValueError(f"Unsupported taxonomic level: '{level}'")
    return all_descriptions


if __name__ == "__main__":
    level_input = 'genus'
    name_input = 'Melitaea'
    all_descriptions = process_taxonomic_level(level_input, name_input)
    print(all_descriptions)