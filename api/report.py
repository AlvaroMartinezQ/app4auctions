import json

DATA = [
    "report_tfidf.json",
    "report_lsi.json",
    "report_bayes.json",
    "report_svm.json",
]

for file in DATA:
    print(file)
    with open(file, "r") as f:
        json_data: dict = json.load(f)
    p_avg = 0
    r_avg = 0
    f1_avg = 0
    items = 0
    for key, value in json_data.items():
        p_avg += value["precision"]
        r_avg += value["recall"]
        f1_avg += value["f1-score"]
        items += 1
    p_avg = p_avg / items
    r_avg = r_avg / items
    f1_avg = f1_avg / items
    print(f"Averages - Precision: {p_avg} - Recall: {r_avg} - F1-score: {f1_avg}")
