import pandas as pd
from dotenv import load_dotenv
import os
from lepi_scrapper import get_artfakta_id, process_taxonomic_level


def load_species_list(file_path: str) -> list[str]:
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    level_input = "species"
    species_list = load_species_list("species_list.txt")
    print(f"🔍 Loaded {len(species_list)} species")


    records = []
    for species in species_list:
        print(f"📄 Processing: {species}")
        all_descriptions = process_taxonomic_level(level_input, species)
    print(all_descriptions)


if __name__ == "__main__":
    main()
