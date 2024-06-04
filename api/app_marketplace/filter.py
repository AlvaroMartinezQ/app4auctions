import string
from datetime import datetime
from typing import Any

import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import cosine_similarity

from utils.database_context import Session as db
from app_marketplace.models import Auction
from app_marketplace.controller import InitController
from app_marketplace.schemas import (
    AuctionGetListFilterTFIDF,
    FilterMethods,
    AuctionGetListFiltersvm,
    AuctionGetListFilterlsi,
)


class TFIDFAuction:
    def __init__(self, auction: Auction, similarity: float) -> None:
        self.auction = auction
        self.similarity = similarity


class AuctionFilter(InitController):
    def __init__(self, session: "db", method: str) -> None:
        self.method = method
        super().__init__(session=session)

    def exp_one(self):
        """Comparing:
        1: "Pokemon Charizard old gold card"
        2: "Gold necklace eighteen karat gold"
        3: "Ferrari Gold car"
        """

        txt = "Pokemon Charizard old gold card"
        tfidf_data = self.tfidf_filter(txt)
        lsi_data = self.lsi_filter(txt)

        tfidf_df = pd.DataFrame()
        lsi_df = pd.DataFrame()
        for entry in tfidf_data.auctions:
            df_dict = pd.DataFrame([entry.auction.__dict__])
            tfidf_df = pd.concat([tfidf_df, df_dict], ignore_index=True)
        for entry in lsi_data.auctions:
            df_dict = pd.DataFrame([entry.__dict__])
            lsi_df = pd.concat([lsi_df, df_dict], ignore_index=True)
        print(len(tfidf_df.index), len(lsi_df.index))
        low = len(tfidf_df.index)
        if len(lsi_df.index) < low:
            low = len(lsi_df.index)

        tfidf_count = {}
        lsi_count = {}
        for i in range(low):
            if tfidf_df.iloc[i]["tags"] not in tfidf_count:
                tfidf_count[tfidf_df.iloc[i]["tags"]] = 1
            else:
                tfidf_count[tfidf_df.iloc[i]["tags"]] += 1

            if lsi_df.iloc[i]["tags"] not in lsi_count:
                lsi_count[lsi_df.iloc[i]["tags"]] = 1
            else:
                lsi_count[lsi_df.iloc[i]["tags"]] += 1
        print(len(tfidf_count), tfidf_count)
        print()
        print(len(lsi_count), lsi_count)

    def exp_two(self):
        """Comparing:
        1: "Pokemon Charizard old gold card"
        2: "Gold necklace eighteen karat gold"
        3: "Ferrari Gold car"
        --> Next sentence is expected to be bad classificated
        4: "Greek old silver bracelet"
        """

        txt = "bon jovi concert poster"
        self.bayes_filter(txt)
        self.svm_filter(txt)

    def filter(self, user_search: str, get_report=False) -> Any:
        match self.method:
            case FilterMethods.tfidf:
                return self.tfidf_filter(user_search)
            case FilterMethods.svm:
                return self.svm_filter(user_search, get_report)
            case FilterMethods.lsi:
                return self.lsi_filter(user_search)
            case FilterMethods.bayes:
                return self.bayes_filter(user_search, get_report)
            case _:
                pass

    def tfidf_filter(self, user_txt: str) -> list[TFIDFAuction]:
        """
        Filter auctions comparing the user search input string with
        auction descriptions (only active auctions will be parsed),
        using the Tfidf method from `sklearn->TfidfVectorizer`.

        The algorithm is made comparing one by one each hactive auction
        with the user search. This way we get how relevant is the user
        search related only with that specific auction.
        """

        auctions = self.get_active_auctions()

        tfidf_results: list[TFIDFAuction] = []
        user_txt_clean = self.clean_text(user_txt)
        for auction in auctions:
            # Cleaned texts
            texts = [
                user_txt_clean,
                self.clean_text(auction.description),
            ]
            # Non cleaned texts
            # texts = [
            #     user_txt,
            #     auction.description,
            # ]

            tfidf = TfidfVectorizer().fit_transform(texts)
            pairwise_similarity = tfidf * tfidf.T
            # We take the first row out of the array since it has
            # the results we want
            # The result of comparison with the user text will be
            # position number 1 of that array, starting from 0
            similarity_vector = pairwise_similarity.toarray()[0]
            if similarity_vector[1] != 0:
                data = TFIDFAuction(auction, similarity_vector[1])
                tfidf_results.append(data)

        # Order based on the similarity with the user search - limited to 100 auctions
        # return AuctionGetListFilterTFIDF(
        #     auctions=sorted(tfidf_results, key=lambda x: x.similarity, reverse=True)[
        #         :100
        #     ]
        # )
        return AuctionGetListFilterTFIDF(
            auctions=sorted(tfidf_results, key=lambda x: x.similarity, reverse=True)
        )

    def svm_filter(self, user_txt: str, get_report=False):
        """
        Get all the auctions that most fit to a user search using a SVM approach

        For this method to work a database with already validated data is requried.
        This is, auction descriptions and labels have to match (be related) otherwise
        the prediction will be wrong. The bigger the dataset to predict, the better
        the results will be
        """

        auctions = (
            self.get_all_auctions()
        )  # Classification is based on all existing auctions
        auctions_df = pd.DataFrame.from_records(
            [auction.__dict__ for auction in auctions]
        )
        auctions_df = auctions_df.sample(frac=1)  # Shuffle dataframe

        # Create a new entry in the dataframe with the auction descriptions cleaned
        auctions_df["lemmanized_description"] = auctions_df.apply(
            lambda row: self.clean_text(row["description"]), axis=1
        )

        # Split the dataset - the bigger the test set the better the results
        # This requires having a large dataframe
        X_train, X_test, y_train, y_test = train_test_split(
            auctions_df["lemmanized_description"],
            auctions_df["tags"],
            test_size=0.25,
        )

        # Convert text data to numerical vectors
        vectorizer = TfidfVectorizer(stop_words="english")
        X_train_vectorized = vectorizer.fit_transform(X_train)

        # Train an SVM classifier on the training set
        svm_classifier = SVC(kernel="linear")
        svm_classifier.fit(X_train_vectorized, y_train)

        # We can also get the accuracy of the trained data
        X_test_vectorized = vectorizer.transform(X_test)
        y_pred = svm_classifier.predict(X_test_vectorized)
        svm_score = accuracy_score(y_test, y_pred)
        # logger.info(f"SVM accuracy score: {svm_score}")
        svm_report = classification_report(
            y_test, y_pred, output_dict=True, zero_division=0
        )
        precision = svm_report["accuracy"]
        recall = svm_report["macro avg"]["recall"]
        f1_score = svm_report["macro avg"]["f1-score"]
        # logger.info(f"P: {precision} - R: {recall} - F1: {f1_score}")

        # Clean the user input
        user_text = self.clean_text(user_txt)
        user_text_vectorized = vectorizer.transform([user_text])

        # Predict among all the categories in the auctions dataframe the one
        # that fits more the user input
        predicted_label = svm_classifier.predict(user_text_vectorized)[0]
        # logger.info(f"SVM predicted category: {predicted_label}")

        if get_report:
            return {
                "phrase": user_txt,
                "precision": precision,
                "recall": recall,
                "f1-score": f1_score,
            }

        # With the predicted label we now are able to retreive the database info
        predicted_auctions: list["Auction"] = []
        predicted_auctions.extend(
            self.session.query(Auction).filter(Auction.tags == predicted_label).all()
        )
        auction_ids = [auction.id for auction in predicted_auctions]
        # Since tags can be = "electronics computer" we not only want to query those auctions
        # whose description equal to that specific tags. The user could also be interested in
        # an auction with the tags = "electronics keyboard"
        if len(predicted_label.split(" ")) > 1:
            for label in predicted_label.split(" "):
                extra_auctions: list["Auction"] = (
                    self.session.query(Auction).filter(Auction.tags.like(label)).all()
                )
                for e_auction in extra_auctions:
                    if e_auction.id not in auction_ids:
                        predicted_auctions.append(e_auction)
                        auction_ids.append(e_auction.id)

        # Return the list of auctions limited to 100 entries
        return AuctionGetListFiltersvm(auctions=predicted_auctions[:500])

    def bayes_filter(self, user_txt: str, get_report=False):
        """
        Get all the auctions that most fit to a user search using a BAYES approach

        For this method to work a database with already validated data is requried.
        This is, auction descriptions and labels have to match (be related) otherwise
        the prediction will be wrong. As in SVM, The bigger the dataset to predict,
        the better the results will be
        """

        auctions = (
            self.get_all_auctions()
        )  # Classification is based on all existing auctions
        auctions_df = pd.DataFrame.from_records(
            [auction.__dict__ for auction in auctions]
        )
        auctions_df = auctions_df.sample(frac=1)
        # Create a new entry in the dataframe with the auction descriptions cleaned
        auctions_df["lemmanized_description"] = auctions_df.apply(
            lambda row: self.clean_text(row["description"]), axis=1
        )

        bayes_X_train, bayes_X_test, bayes_y_train, bayes_y_test = train_test_split(
            auctions_df["lemmanized_description"],
            auctions_df["tags"],
            test_size=0.25,
        )

        # Extract the features
        vectorizer = CountVectorizer()
        train_features = vectorizer.fit_transform(bayes_X_train)

        # Trainning of the model with the vectorized features and train auction labels
        classifier = MultinomialNB()
        classifier.fit(train_features, bayes_y_train)

        # Vectorization of the test auctions descriptions
        bayes_X_test_vectorized = vectorizer.transform(bayes_X_test)
        # Prediction of labels for the previous vectorization
        bayes_y_predict = classifier.predict(bayes_X_test_vectorized)
        # Calculate the accuracy score and print it
        bayes_score = accuracy_score(bayes_y_test, bayes_y_predict)
        # logger.info(f"BAYES accuracy score: {bayes_score}")
        bayes_report = classification_report(
            bayes_y_test, bayes_y_predict, output_dict=True, zero_division=0
        )
        precision = bayes_report["accuracy"]
        recall = bayes_report["macro avg"]["recall"]
        f1_score = bayes_report["macro avg"]["f1-score"]
        # logger.info(f"P: {precision} - R: {recall} - F1: {f1_score}")

        # Clean the user text and vectorize it
        user_vectorized = vectorizer.transform([self.clean_text(user_txt)])
        # Predict on the classifier the labels for the user search and print it
        predicted_labels = classifier.predict(user_vectorized)
        # logger.info(f"BAYES predicted category: {predicted_labels[0]}")

        if get_report:
            return {
                "phrase": user_txt,
                "precision": precision,
                "recall": recall,
                "f1-score": f1_score,
            }

        # With the predicted label we now are able to retreive the database info
        predicted_auctions: list["Auction"] = []
        auction_ids = []
        for label in predicted_labels:
            auctions_label: list["Auction"] = (
                self.session.query(Auction).filter(Auction.tags.like(label)).all()
            )
            for auction in auctions_label:
                if auction.id not in auction_ids:
                    predicted_auctions.append(auction)
                    auction_ids.append(auction.id)

        # Return the list of auctions limited to 100 entries
        return AuctionGetListFiltersvm(auctions=predicted_auctions[:100])

    def lsi_filter(self, user_txt: str):
        """
        Get all the auctions that most fit to a user search using a LSI approach
        """

        auctions = (
            self.get_all_auctions()
        )  # Classification is based on all existing auctions
        auctions_df = pd.DataFrame.from_records(
            [auction.__dict__ for auction in auctions]
        )

        # Needs a list to classify
        auction_txts = auctions_df["description"].tolist()

        # Term document matrix to classify auctions
        vectorizer = CountVectorizer(stop_words="english")
        term_doc_matrix = vectorizer.fit_transform(auction_txts)

        # The bigger the n_components value for `TruncatedSVD` the more it'll take to process!
        svd = TruncatedSVD(n_components=len(auction_txts))
        lsa = svd.fit_transform(term_doc_matrix)  # Contains the auctions texts

        # Vectorize the user search
        user_query = vectorizer.transform([self.clean_text(user_txt)])

        # Input the user query into the lsi space
        lsa_query = svd.transform(user_query)  # Contains the user text

        # Cosine similarities between all auction descriptions and the user search
        similarities: "np.ndarray" = cosine_similarity(lsa_query, lsa)[0]
        top_indices = similarities.argsort()

        # Store the indices of the top most similar auction texts | it's an array of ids in the list
        top_indices = similarities.argsort()  # [:-250:-1]  # Limited to 100 auctions

        # Based on the ids of the list in top_indices we return those ids from the auction list
        return AuctionGetListFilterlsi(
            auctions=[
                auctions[i] for i in top_indices if similarities[i] > 0.001
            ]  # A lower value than 0.001 is considered to be NOT related with the search
        )

    def clean_text(self, text: str) -> str:
        """Clean any input stop words as well as special characters"""

        text = text.lower()
        tokens = word_tokenize(text)

        stop_words = set(stopwords.words("english"))
        punctuations = set(string.punctuation)
        filtered_tokens = [
            token
            for token in tokens
            if (token not in stop_words and token not in punctuations)
        ]

        lemmatizer = WordNetLemmatizer()
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

        return " ".join(lemmatized_tokens)

    def get_active_auctions(self) -> list["Auction"]:
        now = datetime.now()
        auctions: list["Auction"] = (
            self.session.query(Auction)
            .filter(
                Auction.start_date <= now,
                Auction.finish_date > now,
            )
            .all()
        )
        return auctions

    def get_all_auctions(self) -> list["Auction"]:
        return self.session.query(Auction).all()
