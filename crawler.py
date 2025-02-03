from datetime import datetime
import json
import requests
import time
import random


URL = "https://tienda.mercadona.es/api/categories/"
REPEAT_TRIES = 3


def getProducts(category, repeatTries=REPEAT_TRIES):
    # 3rd order category -> products
    r = requests.get(URL + category)

    if r.status_code == 429:
        if repeatTries == 0:
            print("Request denied due to too many consecutive requests")
            return

        # Request denied due to too many consecutive requests
        time.sleep(
            60 * (REPEAT_TRIES - repeatTries)
        )  # delay proportional to the retries
        # try one more time
        return getProducts(category, repeatTries=repeatTries - 1)

    data = r.json()

    results = []

    for cat in data["categories"]:
        results.append(
            {
                "id": cat["id"],
                "name": cat["name"],
                "products": [
                    {
                        "id": item["id"],
                        "name": item["display_name"],
                        "iva": item["price_instructions"]["iva"],
                        "unit_size": item["price_instructions"]["unit_size"],
                        "bulk_price": item["price_instructions"]["bulk_price"],
                        "unit_price": item["price_instructions"]["unit_price"],
                        "size_format": item["price_instructions"]["size_format"],
                    }
                    for item in cat["products"]
                ],
            }
        )
        time.sleep(random.random() * 4)
        return results


# Get 1st and 2nd order categories
r = requests.get(URL)
baseCats = r.json()["results"]
products = [
    {
        "id": bc["id"],
        "name": bc["name"],
        "categories": [  # 2nd order
            {
                "id": c["id"],
                "name": c["name"],
                "categories": getProducts(str(c["id"])),
            }  # 3rd order
            for c in bc["categories"]
        ],
    }
    for bc in baseCats
]


# Update data.json


def compound_dicts(dicts: list[dict]):
    return {k: v for d in dicts for k, v in d.items()}


def diff_dict(d1, d2):
    result = {}
    for key in d2:
        if key not in d1 or d1[key] != d2[key]:
            result[key] = d2[key]

    return result


def update_json(input_data):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    def walk_data(input_data, date):
        for item in input_data:
            # Walk categories recursively
            if "categories" in item:
                walk_data(item["categories"], date)
                continue
            if "products" in item:
                walk_data(item["products"], date)
                continue
            if (
                "content" in item
            ):  # old API uses "content" instead of "categories" and "products"
                walk_data(item["content"], date)
                continue

            # Product
            id = str(item["id"])

            values = {
                "iva": item["iva"],
                "unit_size": item["unit_size"],
                "bulk_price": item["bulk_price"],
                "unit_price": item["unit_price"],
                "size_format": item["size_format"],
            }

            if data.get(id):
                last_values = compound_dicts(data[id]["data"].values())
                diff = diff_dict(last_values, values)  # values that have changed

                if diff:
                    data[id]["data"][date] = diff

            else:
                data[id] = {"name": item["name"], "data": {date: values}}

    walk_data(input_data, datetime.now().strftime("%y-%m-%d"))
    with open(
        "data.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent="\t",  # more readable
            ensure_ascii=False,  # to display accents correctly
        )


update_json(products)
