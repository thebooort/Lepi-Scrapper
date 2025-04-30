from typing import Literal
import requests
from bs4 import BeautifulSoup

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



def process_by_family(family_name: str) -> None:
    """
    Process data at the family taxonomic level.

    Args:
        name (str): Name of the family (e.g. 'Formicidae').
    """
    print(f"Processing FAMILY: {family_name}")
    description = fetch_butterflies_and_moths_description(family_name)
    if description:
        print(f"\n--- Description of {family_name} ---\n")
        print(description)
    else:
        print("No description found.")


    pass


def process_by_species(name: str) -> None:
    """
    Process data at the species taxonomic level.

    Args:
        name (str): Name of the species (e.g. 'Apis mellifera').
    """
    print(f"Processing SPECIES: {name}")
    # TODO: Implement species-level processing logic here
    pass


def process_taxonomic_level(level: TaxonomicLevel, name: str) -> None:
    """
    Routes processing depending on the selected taxonomic level.

    Args:
        level (str): Either 'family' or 'species'.
        name (str): Name of the taxonomic group.
    """
    if level == "family":
        process_by_family(name)
    elif level == "species":
        process_by_species(name)
    else:
        raise ValueError(f"Unsupported taxonomic level: '{level}'")


def main() -> None:
    """
    Main entry point for the script. Prompts user to select taxonomic level and name.
    """
    level_input = 'family'  # input("Enter the taxonomic level (family/species): ").strip().lower()
    name_input = 'Hesperiidae'

    try:
        process_taxonomic_level(level_input, name_input)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
