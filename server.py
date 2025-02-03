from flask import Flask
import json
from urllib.parse import unquote

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)


@app.route("/product/<int:product_id>")
def get_product(product_id):
    if item := data.get(str(product_id)):
        return item

    return {"error": "Product not found"}


@app.route("/query/<string:product_name>")
def query_product(product_name):
    # handle double codification
    decoded_name = unquote(unquote(product_name))

    for item in data.values():
        if item["name"] == decoded_name:
            return item

    return {"error": "Product not found"}
