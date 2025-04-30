from typing import Literal
import requests
from bs4 import BeautifulSoup,Tag
from wikipedia import WikipediaPage
TaxonomicLevel = Literal["family", "species"]



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
            if "description" in section.lower():
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
            if "description" in section.lower():
                lines = section.split("\n")
                return {source_name: "\n".join(lines[1:]).strip()}

        # Fallback: return full content
        return {source_name: content.strip()}

    except Exception as e:
        print(f"[{source_name}] Failed to fetch page for {species_name}: {e}")
        return {source_name: ""}




def fetch_ukmoths_species_description(species_name: str) -> dict[str, str]:
    """
    Fetches the species description from UKMoths based on scientific name.

    Args:
        species_name (str): Scientific name of the species (e.g., 'Korscheltellus lupulina').

    Returns:
        dict: { 'ukmoths.org.uk': description_text }
    """
    source_name = "ukmoths.org.uk"
    base_url = "https://ukmoths.org.uk/species/"
    species_slug = species_name.lower().replace(" ", "-")
    url = f"{base_url}{species_slug}/"
    result = {}

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", class_="span7 speciestext")
        if not content_div:
            print(f"[{source_name}] Description block not found at {url}")
            return {source_name: ""}

        # Collect all non-empty paragraphs
        paragraphs = content_div.find_all("p")
        description = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        result[source_name] = description.strip() if description else ""
        return result

    except requests.RequestException as e:
        print(f"[{source_name}] Failed to fetch {url}: {e}")
        return {source_name: ""}

import requests
from bs4 import BeautifulSoup


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


def fetch_nrm_species_description(species_name: str) -> dict[str, str]:
    """
    Fetches the descriptive text from NRM Svenska Fjärilar for a given species.
    Extracts only the section between 'Kännetecken:' and 'Utbredning:'.

    Args:
        species_name (str): Scientific name (e.g., 'Korscheltellus lupulina').

    Returns:
        dict: { 'nrm.se': cleaned_description }
    """
    source_name = "nrm.se"
    base_url = "http://www2.nrm.se/en/svenska_fjarilar/"
    species_slug = species_name.lower().replace(" ", "_")
    first_letter = species_slug[0]
    url = f"{base_url}{first_letter}/{species_slug}.html"
    result = {}

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        td = soup.find("td", valign="TOP", align="LEFT")
        if not td:
            print(f"[{source_name}] No matching <td> found at {url}")
            return {source_name: ""}

        full_text = td.get_text(separator="\n", strip=True)

        start_key = "Kännetecken:"
        end_key = "Utbredning:"
        start_idx = full_text.find(start_key)
        end_idx = full_text.find(end_key)

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned_text = full_text[start_idx:end_idx].strip()
        elif start_idx != -1:
            cleaned_text = full_text[start_idx:].strip()
        else:
            cleaned_text = ""

        result[source_name] = cleaned_text
        return result

    except requests.RequestException as e:
        print(f"[{source_name}] Failed to fetch {url}: {e}")
        return {source_name: ""}



def fetch_adw_species_description(species_name: str) -> dict[str, str]:
    """
    Obtiene la descripción de la especie desde Animal Diversity Web (ADW).

    Args:
        species_name (str): Nombre científico de la especie (por ejemplo, 'Attacus atlas').

    Returns:
        dict: {'animaldiversity.org': texto_descripción}
    """
    source_name = "animaldiversity.org"
    base_url = "https://animaldiversity.org/accounts/"
    species_slug = species_name.strip().replace(" ", "_")
    url = f"{base_url}{species_slug}/"
    result = {}

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Buscar la sección de descripción física
        description_section = soup.find("h2", string="Physical Description")
        if description_section:
            paragraphs = []
            for sibling in description_section.find_next_siblings():
                if sibling.name == "h2":
                    break
                if sibling.name == "p":
                    paragraphs.append(sibling.get_text(strip=True))
            description_text = "\n\n".join(paragraphs)
            result[source_name] = description_text
        else:
            print(f"[{source_name}] Sección 'Physical Description' no encontrada en {url}")
            result[source_name] = ""

        return result

    except requests.RequestException as e:
        print(f"[{source_name}] Error al acceder a {url}: {e}")
        return {source_name: ""}



def process_by_species(spe_name: str) -> None:
    """
    Process data at the species taxonomic level.

    Args:
        name (str): Name of the species (e.g. 'Attacus atlas').
    """
    print(f"Processing FAMILY: {spe_name}")
    all_descriptions = {}
    # all_descriptions.update(fetch_wikipedia_species_description(spe_name))
    # all_descriptions.update(fetch_ukmoths_species_description(spe_name))
    # all_descriptions.update(fetch_bamona_species_description(spe_name))
    all_descriptions.update(fetch_nrm_species_description(spe_name))

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
