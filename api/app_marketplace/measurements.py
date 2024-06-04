import typing
import json

import pandas as pd
from loguru import logger

from app_marketplace.filter import AuctionFilter
from app_marketplace.schemas import FilterMethods

if typing.TYPE_CHECKING:
    from utils.database_context import Session

FILTER_TEXTS = [
    "Pokemon Charizard old gold card",
    "Gold necklace eighteen karat gold",
    "Ferrari Gold car",
    "Gold medieval sword",
    "Old painting",
    "Porcelain decorative car",
    "Basketball sticker card",
    "Military style rolex watch",
    "Porsche",
    "Collector cards",
    "Military badge",
    "Vietnam propaganda poster",
    "Luke Skywalker",
]
EXPECTED_TAG_PER_TEXT = [
    "pokemon",
    "jewelry collar",
    "ferrari cars",
    "sword",
    "painting",
    "car",
    "card",
    "rolex",
    "porshce cars",
    "card",
    "world-war-2",
    "vietnam",
    "star-wars",
]


# TF-IDF
def tfidf(db: "Session"):
    filter = AuctionFilter(db, FilterMethods.tfidf.value)
    final_data = {}

    for i in range(len(FILTER_TEXTS)):
        logger.info(f"Processing '{FILTER_TEXTS[i]}'")
        tfidf_data = filter.filter(FILTER_TEXTS[i])
        tfidf_df = pd.DataFrame()
        for entry in tfidf_data.auctions:
            df_dict = pd.DataFrame([entry.auction.__dict__])
            tfidf_df = pd.concat([tfidf_df, df_dict], ignore_index=True)

        auctions_retrieved = len(tfidf_df.index)
        relevant = len(tfidf_df.loc[tfidf_df["tags"] == EXPECTED_TAG_PER_TEXT[i]].index)
        logger.info(
            f"Auctions retrieved: {auctions_retrieved} - Relevant ones: {relevant}"
        )
        auction_tag_count: int = len(
            db.execute(
                f"SELECT * FROM market_auction WHERE tags = '{EXPECTED_TAG_PER_TEXT[i]}'"
            ).all()
        )

        # precision = not_relevant / auctions_retrieved
        precision = relevant / auctions_retrieved
        # recall = relevant / auctions_retrieved
        recall = relevant / auction_tag_count
        f1score = 2 * ((precision * recall) / (precision + recall))
        data = {
            "phrase": FILTER_TEXTS[i],
            "precision": precision,
            "recall": recall,
            "f1-score": f1score,
        }
        final_data[i] = data
        logger.info("")
    with open("report_tfidf.json", "w") as f:
        json.dump(final_data, f)


# LSI
def lsi(db: "Session"):
    filter = AuctionFilter(db, FilterMethods.lsi.value)
    final_data = {}

    for i in range(len(FILTER_TEXTS)):
        logger.info(f"Processing '{FILTER_TEXTS[i]}'")
        lsi_data = filter.filter(FILTER_TEXTS[i])
        lsi_df = pd.DataFrame()
        for entry in lsi_data.auctions:
            df_dict = pd.DataFrame([entry.__dict__])
            lsi_df = pd.concat([lsi_df, df_dict], ignore_index=True)

        auctions_retrieved = len(lsi_df.index)
        relevant = len(lsi_df.loc[lsi_df["tags"] == EXPECTED_TAG_PER_TEXT[i]].index)
        logger.info(
            f"Auctions retrieved: {auctions_retrieved} - Relevant ones: {relevant}"
        )
        auction_tag_count: int = len(
            db.execute(
                f"SELECT * FROM market_auction WHERE tags = '{EXPECTED_TAG_PER_TEXT[i]}'"
            ).all()
        )

        # precision = not_relevant / auctions_retrieved
        precision = relevant / auctions_retrieved
        # recall = relevant / auctions_retrieved
        recall = relevant / auction_tag_count
        f1score = 2 * ((precision * recall) / (precision + recall))
        data = {
            "phrase": FILTER_TEXTS[i],
            "precision": precision,
            "recall": recall,
            "f1-score": f1score,
        }
        final_data[i] = data
        logger.info("")
    with open("report_lsi.json", "w") as f:
        json.dump(final_data, f)


# Naive Bayes
def naive_bayes(db: "Session"):
    filter = AuctionFilter(db, FilterMethods.bayes.value)
    final_data = {}

    for i in range(len(FILTER_TEXTS)):
        data = filter.filter(FILTER_TEXTS[i], get_report=True)
        final_data[i] = data
    with open("report_bayes.json", "w") as f:
        json.dump(final_data, f)


# SVM
def svm(db: "Session"):
    filter = AuctionFilter(db, FilterMethods.svm.value)
    final_data = {}

    for i in range(len(FILTER_TEXTS)):
        logger.info(f"Processing '{FILTER_TEXTS[i]}'")
        data = filter.filter(FILTER_TEXTS[i], get_report=True)
        final_data[i] = data
        logger.info("")
    with open("report_svm.json", "w") as f:
        json.dump(final_data, f)


def measure(db: "Session") -> None:
    logger.info("Starting measurements...")
    # tfidf(db)
    # lsi(db)
    naive_bayes(db)
    svm(db)
