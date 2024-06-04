#!/usr/bin/env python

import os
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from loguru import logger
from fastapi.templating import Jinja2Templates
import nltk

# Download the required packages to clean user input text
nltk.download("stopwords")  # stopwords
nltk.download("wordnet")  # lemmatizer data
nltk.download("punkt")  # punkt data

# Static vars
DEBUG = False
if "DEBUG" in os.environ:
    DEBUG = True
# Change to false to run production mode
BASE_DIR = (
    Path(__file__).resolve().parent
)  # Build paths inside the project like: BASE_DIR / 'subdir'
logger.info("DEBUG mode: " + str(DEBUG))

# Open API schema definition
app = FastAPI(
    title="App 4 auctions API",
    description="Services and endpoints for APP4AUCTIONS project.",
    version="0.0.0",
    docs_url="/",  # Serve the docs on the '/' url
    openapi_url="/api/v1",
)


templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

if DEBUG:
    logger.warning(f"{__name__} - Running under DEBUG mode.")
    from utils.load_conf import LocalConfig

    LocalConfig.load(BASE_DIR=BASE_DIR)

    if not os.getenv("POSTGRES_PASSWORD"):
        raise Exception("Postgres password not present, cannot start debug server.")


# CORS
origins = [
    # "*",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origin_regex="https?:\\/\\/(localhost|127\\.0\\.0\\.1)(:\\d{1,5})?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Project routers
from app_system.router import router as sys_router
from app_auth.router import router as auth_router
from app_marketplace.router import router as market_router
from app_wallet.router import router as wallet_router
from app_ws.marketplace_ws import router as ws_marketplace

app.include_router(sys_router, prefix="/system", tags=["API status"])
app.include_router(auth_router, prefix="/auth/user", tags=["User routes"])
app.include_router(market_router, prefix="/market", tags=["Market, Auctions, Bids"])
app.include_router(wallet_router, prefix="/wallet", tags=["Virtural wallet"])
app.include_router(ws_marketplace, prefix="", tags=["Marketplace websocket"])
