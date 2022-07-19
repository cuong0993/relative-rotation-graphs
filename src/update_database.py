from rrg_db import DatabaseManager
import requests
import time

db = DatabaseManager()
db.drop_table()
db.create_table()

config = db.get_config()
config["symbols"].append(config["compare_to"])

apikey = "LZ90ZS5VQG18GRXB"
dataKey = "Weekly Time Series"
valueKey = "4. close"


def buildUrl(symbol, apikey):
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol="
    url += symbol
    url += "&apikey="
    url += apikey
    url += "&outputsize=full"
    return url


for symbol in config["symbols"]:
    print("Inserting %s data from AlphaVantage into Database..." % symbol)

    response = requests.get(buildUrl(symbol, apikey))

    if dataKey not in response.json():
        # Error handling
        # "Note" => too many requests per minute
        # "Error Message" => invalid symbol

        if "Note" in response.json():
            print("Too many requests, waiting ", end="")

            while "Note" in response.json():
                time.sleep(10)
                print(".", end="")
                response = requests.get(buildUrl(symbol, apikey))

            print()

        if "Error Message" in response.json():
            print("Invalid symbol, next symbol...\n")
            continue

    wts = response.json()[dataKey]

    for key, value in wts.items():
        db.insert_value(symbol, key, value[valueKey])


db.commit()
