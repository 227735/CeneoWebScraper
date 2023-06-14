from app import app
from flask import render_template, request, redirect, url_for
import requests
import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from app.utilis import get_element, selectors

@app.route("/")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/product/<code>")
def product(code):
    opinions = pd.read_json(f"./app/data/opinions/{code}.json")
    opinions = pd.read_json(f"./opinions/{product_code}.json")
    opinions.stars = opinions.stars.map(lambda x: float(x.split("/")[0].replace(",",".")))
    stats = {    
        "opinions_count" : opinions.opinion_id.count(),
        "pros_count" : opinions.pros.map(bool).sum(),
        "cons_count" : opinions.cons.map(bool).sum(),
        "stars_avg" : opinions.stars.mean().round(2)
    }

    if not os.path.exists("./plots"):
        os.mkdir("./plots")

    stars = opinions.stars.value_counts().reindex(list(np.arange(0,5.5,0.5)), fill_value=0)
    print(stars)
    stars.plot.bar()
    plt.title("Histogram gwiazdek")
    plt.savefig(f"./plots/{product_code}_stars.png")
    plt.close()
    # plt.show()

    # udział poszczeególnych rekomendacji w ogólnej liczbie opinii
    recommendations = opinions.recommendation.value_counts(dropna=False)
    recommendations.plot.pie(label="", autopct="%1.1f%%")
    plt.savefig(f"./plots/{product_code}_recommendations.png")
    plt.close()

    return render_template("product.html", product_code=code,  opinions = opinions.to_html(header="true", table_ide="opinions",classes="table table-striped table-info"))

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/extract", methods=['POST', 'GET'])
def extract():
    if request.method == 'POST':
        product_code = request.form.get("product_code")
        url = f"https://www.ceneo.pl/{product_code}#tab=reviews"
        all_opinions = []
        while(url):
            print(url)
            response = requests.get(url)
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions = page_dom.select("div.js_product-review")
            for opinion in opinions:
                single_opinion = {}
                for key, value in selectors.items():
                    single_opinion[key] = get_element(opinion, *value)
                all_opinions.append(single_opinion)
            try:    
                url = "https://www.ceneo.pl"+get_element(page_dom,"a.pagination__next","href")
            except TypeError:
                url = None
        if not os.path.exists("./app/data/opinions"):
            os.mkdir("./app/data/opinions")
        with open(f"./app/data/opinions/{product_code}.json", "w", encoding="UTF-8") as jf:
            json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
            return redirect(url_for("product", code=product_code))
    return render_template("extract.html")

@app.route("/author")
def author():
    return render_template("author.html")
