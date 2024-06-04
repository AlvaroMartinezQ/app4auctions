import argparse
import uvicorn
from loguru import logger

from utils.database_context import Session
from app_auth.models import GenericUser
from sample_data.ingest_data import data_ingestion


TEST_EMAIL = "admin@app4auctions.com"

if __name__ == "__main__":
    """Do no run with this settings on production!

    Run this script with the -i flag to automatically prepopulate the database
    with some testing data. You can add more auctions if desired inside the
    `auctions.json` file. It will also create a user with email as `admin@app4auctions.com`
    and password `1` with a virtual wallet with 10K EUR.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", help="Ingest test data into the database", action="store_true"
    )
    args = parser.parse_args()

    if args.i:
        logger.warning("Ingesting dev data...")
        data_ingestion()

    with Session() as db:
        user: GenericUser = (
            db.query(GenericUser).filter(GenericUser.email == TEST_EMAIL).first()
        )
        if user:
            logger.info(
                f"{__name__} - Super admin user in database, email: {user.email}"
            )
        else:
            logger.warning("No user found on debug db. Did you ingest data?")

    if args.i:
        logger.info(
            "Data inserted into the database, please run again the command without the -i option"
        )
    else:
        # With no args start the sever
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=5000,
            reload=True,
            reload_excludes="executor.py",
        )
