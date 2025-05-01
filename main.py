import pandas as pd
from dotenv import load_dotenv
import os
from lepi_scrapper import get_artfakta_id, process_taxonomic_level



def process_species_list_with_routing(file_path: str, level: str) -> pd.DataFrame:
    """
    Procesa una lista de taxones (especies o familias), usando process_taxonomic_level.

    Args:
        file_path (str): Ruta al archivo de texto con nombres (uno por línea).
        level (TaxonomicLevel): 'species' o 'family'.

    Returns:
        pd.DataFrame: DataFrame con columnas [species, source, description, desc_len]
    """
    with open(file_path) as f:
        taxon_names = [line.strip() for line in f if line.strip()]

    all_rows = []
    for name in taxon_names:
        print(f"\n=== Processing {level}: {name} ===")
        descriptions = process_taxonomic_level(level, name)
        for source, desc in descriptions.items():
            all_rows.append({
                "taxon": name,
                "level": level,
                "source": source,
                "description": desc,
                "desc_len": len(desc)
            })

    df = pd.DataFrame(all_rows)
    return df

if __name__ == "__main__":
    level = 'family'
    df = process_species_list_with_routing("../family_list.txt", level)
    df.to_csv("families_descriptions.csv", index=False)
    print("\nSaved to 'families_descriptions.csv'")
