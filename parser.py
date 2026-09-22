import csv
import json
from pathlib import Path

CATEGORY_MAP = {
    "rent": "Rent",
    "sale": "Sale",
    "dobry": "Good",
    "novostavba": "New Building",
    "velmi_dobry": "Very Good",
    "vybavena": "Furnished",
    "nevybavena": "Unfurnished",
    "castecne_vybavena": "Partially Furnished",
    "spatny": "Bad",
    "cihla": "Brick",
    "panel": "Panel"
}

def save_estates_to_file(writer, list_of_parameters):
    writer.writerow(list_of_parameters)

def get_estates_info(dataset, filename="estates_info.csv"):
    base_path = Path(dataset)
    success_counter = 0
    duplicate_counter = 0

    with open(filename, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if base_path.name == "pronajem":
            writer.writerow(["Estate Type", "City Part", "District", "Area", "State", "Furnished", "Price"])
        elif base_path.name == "prodej":
            writer.writerow(["Estate Type", "City Part", "District", "Area", "State", "Material", "Price"])

        for state_dir in base_path.iterdir():
            if not state_dir.is_dir(): continue
            flat_state = state_dir.name

            for extra_dir in state_dir.iterdir():
                if not extra_dir.is_dir(): continue
                flat_extra = extra_dir.name

                processed_estates = set()

                for estates_file in extra_dir.iterdir():
                    if not estates_file.is_file() or estates_file.suffix != ".json": continue

                    with open(estates_file, "r", encoding="utf-8") as file:
                        data = json.load(file)

                    try:
                        estates_list = data.get('pageProps', {}).get('dehydratedState', {}).get('queries', [])[1].get("state", {}).get("data", {}).get("results", [])
                    except (IndexError, TypeError) as e:
                        print(f"Error occurred while accessing estates_list: {e}")

                    for estate in estates_list:
                        estate_type = estate.get("categorySubCb", ()).get("name", "")

                        estate_locality = estate.get("locality", "").get("cityPart", "")
                        estate_district = estate.get("locality", "").get("district", "")

                        estate_area = int(estate.get("name", "").split()[-2])

                        estate_price = estate.get("priceCzk", 0)

                        signature = (estate_type, estate_locality, estate_district, estate_area, estate_price)

                        if signature not in processed_estates:
                            if estate_price < 1000: continue
                            save_estates_to_file(writer, [estate_type, estate_locality, estate_district, estate_area, CATEGORY_MAP.get(flat_state, flat_state), CATEGORY_MAP.get(flat_extra, flat_extra), estate_price])
                            processed_estates.add(signature)
                            # print(f"New estate added: {signature}")
                            success_counter += 1
                        else:
                            # print(f"Duplicate estate found: {signature}")
                            duplicate_counter += 1

    print(f"Success: {success_counter}, Duplicates: {duplicate_counter}")