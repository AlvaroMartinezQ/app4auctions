"""Scrap data for auctions from www.liveauctioneers.com"""

# Data obtained by this script is and will only be used for educational purposes

import json

from requests_html import HTMLSession


LIMIT = "This site is protected by reCAPTCHA and the Google Terms of Service and Privacy Policy apply"


class ScrapIt:
    def __init__(self, file_name: str) -> None:
        self._sources = file_name

    def scrape(self) -> None:
        # Optional to clean the file at initialization
        # with open("./data.json", "a+", encoding="utf-8") as f_data:
        #     f_data.truncate(0)
        #     d = {"schemas": []}
        #     json.dump(
        #         d,
        #         f_data,
        #         ensure_ascii=False,
        #         indent=4,
        #     )
        with open(self._sources, "r") as s:
            s_lines = s.readlines()

            for entry in s_lines:
                if not entry.startswith("#") and entry != "":
                    print(f"\nQuery to: {entry}")
                    all_data = []  # Data as json
                    # Get the date from source
                    with HTMLSession() as session:
                        r = session.get(entry)
                        print(f"Response code: {r.status_code}")
                        with open("response-raw.html", "w") as f:
                            f.write(r.html.text)
                    # Split the wanted raw data into an smaller file
                    limit_f = False
                    with open("response-raw.html", "r") as f:
                        line = f.readline()
                        while line != "":
                            if LIMIT in line:
                                limit_f = True
                                with open("aux.html", "w") as f2:
                                    f2.writelines(f.readlines())
                            line = f.readline()
                    # Generate objects for App4Auctions
                    # If the limit is found on the response - otherwise the server blocked
                    # communication from the script
                    if limit_f:
                        try:
                            with open("aux.html", "r") as f:
                                f.readline()  # First one not wanted
                                l: str = (
                                    f.readline()
                                )  # Data is stored in a long line as json
                                l = (
                                    l.replace("window.__data=", "")
                                    .replace("undefined", '""')
                                    .replace(";", "", 1)
                                )
                                length = len(l)
                                aux_l = ""
                                for i in range(length):
                                    if l[i] == ";":
                                        aux_l = l[0:i]
                                jsonized_data = json.loads(aux_l)
                                for auction_id in jsonized_data["itemSummary"]["byId"]:
                                    auction_data = jsonized_data["itemSummary"]["byId"][
                                        auction_id
                                    ]
                                    # Data:
                                    # - title: `title`
                                    # - description: `shortDescription`
                                    # - init_price: `startPrice`
                                    app4auctions_data = {
                                        "finish_date": "2025-01-01 00:00:00",
                                        "tags": "",
                                        "price_currency": "euro",
                                    }
                                    app4auctions_data["title"] = auction_data["title"]
                                    app4auctions_data["description"] = auction_data[
                                        "shortDescription"
                                    ]
                                    app4auctions_data["init_price"] = auction_data[
                                        "startPrice"
                                    ]
                                    all_data.append(app4auctions_data)
                        except Exception as e:
                            print()
                            print("error on treatment of aux.html!")
                            print(str(e))
                            print()
                        # Get the existing data and clear the file to
                        # input data with the new obtained auctions
                        existing_data = {}
                        with open("./data.json", "r+") as f_data:
                            existing_data = json.loads(f_data.read())
                            f_data.truncate(0)
                        for e in all_data:
                            existing_data["schemas"].append(e)
                        print(f"Found {len(all_data)} entities to add")
                        print(f"Data count now is: {len(existing_data['schemas'])}")
                        print()
                        with open("./data.json", "w") as f_data:
                            json.dump(
                                existing_data, f_data, ensure_ascii=False, indent=2
                            )
                    else:
                        print()
                        print(
                            "Limit was not found on response - cannot get data out of it"
                        )
                        print()


if __name__ == "__main__":
    ScrapIt("./links.txt").scrape()
