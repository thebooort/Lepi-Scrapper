from typing import Literal
import requests
from bs4 import BeautifulSoup,Tag
from wikipedia import WikipediaPage
import pandas as pd


TaxonomicLevel = Literal["family", "species"]

try:
    df_dyntaxa = pd.read_csv("../dyntaxa_DB/Taxon.csv", sep="	", encoding="utf-8")

except FileNotFoundError:
    print("File not found. Please check the path to the dataset.")
    df_dyntaxa = pd.DataFrame()

import json

with open("secrets.json") as f:
    secrets = json.load(f)
api_key = secrets.get("artfakta_api_key")



def get_artfakta_id(species_name: str) -> str | None:
    """
    Given a scientific name, extract the numeric Artfakta taxon ID from the dataset.

    Args:
        species_name (str): Scientific name (e.g., 'Elymus caninus')
        dataset_path (str): Path to CSV with column 'scientificName' and 'taxonId'

    Returns:
        str | None: Taxon ID number (e.g. '222441') or None if not found
    """
    df_dyntaxa["scientificName"] = df_dyntaxa["scientificName"].str.strip().str.lower()
    match = df_dyntaxa[df_dyntaxa["scientificName"] == species_name.strip().lower()]
    if not match.empty:
        full_id = match.iloc[0]["acceptedNameUsageID"]
        if isinstance(full_id, str):
            return full_id.split(":")[-1]  # extract the number part
    return None



def fetch_butterflies_and_moths_description(family_name: str) -> dict[str, str]:
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
    print(url)
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

def fetch_vilkenart_description(family_name: str) -> dict[str, str]:
    """
    Fetches the family description from vilkenart.se and returns it in a dictionary.

    Args:
        family_name (str): Name of the family (e.g. 'Hesperiidae').

    Returns:
        dict: Dictionary with the source name as key and extracted description as value.
    """
    source_name = "vilkenart.se"
    base_url = "https://www.vilkenart.se/HogreTaxa.aspx?Namn="
    url = f"{base_url}{family_name}"
    result = {}
    print(url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        description_div = soup.find("div", id="ctl00_ContentPlaceHolder1_pnlTaxonText")
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

def fetch_wikipedia_description(family_name: str) -> dict[str, str]:
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




def process_by_family(family_name: str) -> None:
    """
    Process data at the family taxonomic level.

    Args:
        name (str): Name of the family (e.g. 'Formicidae').
    """
    print(f"Processing FAMILY: {family_name}")
    all_descriptions = {}
    all_descriptions.update(fetch_butterflies_and_moths_description(family_name))
    all_descriptions.update(fetch_vilkenart_description(family_name))
    all_descriptions.update(fetch_wikipedia_description(family_name))

    for source, desc in all_descriptions.items():
        print(f"\n--- {source} ---\n{desc[:100]} desc_len:{len(desc)}\n")

    pass


def fetch_wikipedia_species_description(species_name: str) -> dict[str, str]:
    """
    Fetches the 'Description' section or full Wikipedia content for a given species.

    Args:
        species_name (str): Full scientific name of the species (e.g. 'Papilio machaon').

    Returns:
        dict: { 'wikipedia.org': extracted_text }
    """
    source_name = "wikipedia.org"

    try:
        page = WikipediaPage(species_name)
        content = page.content

        # Try to extract a "Description"-related section
        sections = content.split("\n==")
        for section in sections:
            if "description" in section.lower() and len(section) > 20:
                print(section)
                lines = section.split("\n")
                return {source_name: "\n".join(lines[1:]).strip()}
            elif "imago" in section.lower() and len(section) > 20:
                lines = section.split("\n")
                return {source_name: "\n".join(lines[1:]).strip()}
            

        # Fallback: return full content
        return {source_name: content.strip()}

    except Exception as e:
        print(f"[{source_name}] Failed to fetch page for {species_name}: {e}")
        return {source_name: ""}




def fetch_ukmoths_species_description(species_name: str) -> dict[str, str]:
    """
    Fetches the species description from UKMoths.

    Args:
        species_name (str): Scientific name (e.g., 'Archiearis parthenias').

    Returns:
        dict: { 'ukmoths.org.uk': description_text }
    """
    source_name = "ukmoths.org.uk"
    base_url = "https://ukmoths.org.uk/species/"
    species_slug = species_name.strip().lower().replace(" ", "-")
    url = f"{base_url}{species_slug}/"
    result = {}

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        content_div = soup.find("div", class_="span7 speciestext")
        if not content_div:
            print(f"[{source_name}] Content div not found at {url}")
            return {source_name: ""}

        # Prefer <p> tags if present
        paragraphs = content_div.find_all("p")
        if paragraphs:
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            # If no <p>, extract all text, replacing <br> with newlines
            for br in content_div.find_all("br"):
                br.replace_with("\n")
            text = content_div.get_text(separator="", strip=True)

        full_text = text
        # Slice after first ')'
        if ")" in full_text:
            idx = full_text.find(")") + 1
            trimmed_text = full_text[idx:].lstrip()
        else:
            trimmed_text = full_text

        result[source_name] = trimmed_text
        return result


    except requests.RequestException as e:
        print(f"[{source_name}] Failed to fetch {url}: {e}")
        return {source_name: ""}


def fetch_bamona_species_description(species_name: str) -> dict[str, str]:
    """
    Fetches detailed species information from Butterflies and Moths of North America (BAMONA).

    Args:
        species_name (str): Scientific name of the species (e.g., 'Korscheltellus lupulina').

    Returns:
        dict: { 'butterfliesandmoths.org': multiline description with labeled fields }
    """
    source_name = "butterfliesandmoths.org"
    base_url = "https://www.butterfliesandmoths.org/species/"
    species_slug = species_name.strip().replace(" ", "-")
    url = f"{base_url}{species_slug}"
    result = {}
    print(url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        description_block = soup.find("div", class_="pane-content")
        if not description_block:
            print(f"[{source_name}] Description block not found at {url}")
            return {source_name: ""}

        # Extract all field pairs: label and content
        data = []
        fields = description_block.find_all("div", class_="views-field")
        for field in fields:
            label_tag = field.find("strong", class_="views-label")
            content_tag = field.find("span", class_="field-content")

            if label_tag and content_tag:
                label = label_tag.get_text(strip=True).rstrip(":")
                content = content_tag.get_text(strip=True)
                if content:
                    data.append(f"{label}: {content}")

        if data:
            result[source_name] = "\n".join(data)
        else:
            result[source_name] = ""

        return result

    except requests.RequestException as e:
        print(f"[{source_name}] Failed to fetch {url}: {e}")
        return {source_name: ""}


import requests
from bs4 import BeautifulSoup


def fetch_nrm_species_description(species_name: str, debug: bool = False) -> dict[str, str]:
    """
    Fetches the descriptive text from NRM Svenska Fjärilar for a given species.
    - If the page includes 'Kännetecken:' and 'Utbredning:', extracts that section.
    - Otherwise, returns all text after images and before external links.

    Args:
        species_name (str): Scientific name (e.g., 'Archiearis parthenias').
        debug (bool): If True, prints debug info.

    Returns:
        dict: { 'nrm.se': cleaned_description }
    """
    source_name = "nrm.se"
    base_url = "http://www2.nrm.se/en/svenska_fjarilar/"
    species_slug = species_name.lower().replace(" ", "_")
    first_letter = species_slug[0]
    url = f"{base_url}{first_letter}/{species_slug}.html"
    result = {}

    if debug:
        print(f"[DEBUG] Fetching: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        td = soup.find("td", valign="TOP", align="LEFT")
        if not td:
            print(f"[{source_name}] No matching <td> found at {url}")
            return {source_name: ""}

        # Replace <br> with newlines
        for br in td.find_all("br"):
            br.replace_with("\n")

        full_text = td.get_text(separator="\n", strip=True)

        # Try structured extraction
        start_key = "Kännetecken:"
        end_key = "Utbredning:"
        start_idx = full_text.find(start_key)
        end_idx = full_text.find(end_key)

        if start_idx != -1 and (end_idx == -1 or end_idx > start_idx):
            cleaned_text = full_text[start_idx:end_idx].strip() if end_idx != -1 else full_text[start_idx:].strip()
        else:
            # Fallback: remove anything before the first scientific name line
            lines = full_text.split("\n")
            content_lines = []
            found_scientific_name = False
            for line in lines:
                if not found_scientific_name and "(" in line and ")" in line:
                    found_scientific_name = True
                if found_scientific_name:
                    if "Mer om denna art på" in line:
                        break
                    content_lines.append(line)
            cleaned_text = "\n".join(content_lines).strip()

        result[source_name] = cleaned_text
        return result

    except requests.RequestException as e:
        print(f"[{source_name}] Failed to fetch {url}: {e}")
        return {source_name: ""}




def fetch_adw_species_description(species_name: str) -> dict[str, str]:
    """
    Fetches the 'Physical Description' section from Animal Diversity Web for a given species.

    Args:
        species_name (str): Scientific name (e.g., 'Attacus atlas').

    Returns:
        dict: { 'animaldiversity.org': extracted_description }
    """
    source_name = "animaldiversity.org"
    base_url = "https://animaldiversity.org/accounts/"
    species_slug = species_name.strip().replace(" ", "_")
    url = f"{base_url}{species_slug}/"
    result = {}
    print(url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        section_header = soup.find("h3", id="physical_description")
        if not section_header:
            print(f"[{source_name}] Section 'Physical Description' not found at {url}")
            return {source_name: ""}

        # Collect all paragraphs until the next <h3>
        paragraphs = []
        next_node = section_header.find_next_sibling()
        while next_node:
            if next_node.name == "h3":
                break
            if next_node.name == "p":
                text = next_node.get_text(strip=True)
                if text:
                    paragraphs.append(text)
            next_node = next_node.find_next_sibling()

        description_text = "\n\n".join(paragraphs)
        result[source_name] = description_text

        return result

    except requests.RequestException as e:
        print(f"[{source_name}] Failed to fetch {url}: {e}")
        return {source_name: ""}




def fetch_artfakta_species_description_api(species_name: str) -> dict[str, str]:
    """
    Fetches the 'characteristic' field from the Artfakta API using a taxon ID.

    Args:
        taxon_id (str): The numeric taxon ID, e.g., '213903'.
        api_key (str): Your Artfakta API key.

    Returns:
        dict: { 'artfakta.se': species description from 'characteristic' }
    """
    source_name = "artfakta.se"
    taxon_id = get_artfakta_id(species_name)
    print(f"Taxon ID for {species_name}: {taxon_id}")
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




def process_by_species(spe_name: str) -> dict[str, str]:
    """
    Process data at the species taxonomic level.

    Args:
        name (str): Name of the species (e.g. 'Attacus atlas').
    """
    print(f"Processing species: {spe_name}")
    all_descriptions = {}
    print("Fetching descriptions...")
    # print("wikipedia.org")
    # all_descriptions.update(fetch_wikipedia_species_description(spe_name))
    # print("ukmoths.org.uk")
    # all_descriptions.update(fetch_ukmoths_species_description(spe_name))
    # print("butterfliesandmoths.org")
    # all_descriptions.update(fetch_bamona_species_description(spe_name))
    # print("animaldiversity.org")
    # all_descriptions.update(fetch_nrm_species_description(spe_name))
    # print("nrm.se")
    # all_descriptions.update(fetch_adw_species_description(spe_name))
    print("artfakta.se")
    all_descriptions.update(fetch_artfakta_species_description_api(spe_name))
    for source, desc in all_descriptions.items():
        print(f"\n--- {source} ---\n{desc[:100]} \ndesc_len:{len(desc)}\n")

    return all_descriptions


def process_taxonomic_level(level: TaxonomicLevel, name: str) -> None:
    """
    Routes processing depending on the selected taxonomic level.

    Args:
        level (str): Either 'family' or 'species'.
        name (str): Name of the taxonomic group.
    """
    if level == "family":
        all_descriptions=process_by_family(name)
    elif level == "species":
        all_descriptions=process_by_species(name)
    else:
        raise ValueError(f"Unsupported taxonomic level: '{level}'")
    return all_descriptions


def main() -> None:
    """
    Main entry point for the script. Prompts user to select taxonomic level and name.
    """
    # level_input = 'family'  # input("Enter the taxonomic level (family/species): ").strip().lower()
    # name_input = 'Hesperiidae'
    # process_taxonomic_level(level_input, name_input)

    level_input = 'species'  # input("Enter the taxonomic level (family/species): ").strip().lower()
    name_input = 'Korscheltellus lupulina'
    all_descriptions = process_taxonomic_level(level_input, name_input)
    print(all_descriptions)

if __name__ == "__main__":
    main()
