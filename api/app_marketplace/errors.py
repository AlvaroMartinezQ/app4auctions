from fastapi import Request
from fastapi.responses import JSONResponse

from main import app


class NotFoudnAuction(Exception):
    def __init__(self, auction_id) -> None:
        self.msg = f"Auction identified with {auction_id} not found"
        super().__init__()


@app.exception_handler(NotFoudnAuction)
async def not_found_auction(request: Request, exc: NotFoudnAuction):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.msg},
    )


class NotFoudnBid(Exception):
    def __init__(self, bid_id) -> None:
        self.msg = f"Bid identified with {bid_id} not found"
        super().__init__()


@app.exception_handler(NotFoudnBid)
async def not_found_auction(request: Request, exc: NotFoudnBid):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.msg},
    )


class NotOwnedAuction(Exception):
    def __init__(self) -> None:
        self.msg = "This auction doesn't exist or you cannot modify it."
        super().__init__()


@app.exception_handler(NotOwnedAuction)
async def auction_not_owned_by_user(request: Request, exc: NotOwnedAuction):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class AuctionStarted(Exception):
    """Indicate the user that the auction has already started and cannot delete or update it"""

    def __init__(self) -> None:
        self.msg = "This auction has already started, you cannot delete/update it."
        super().__init__()


@app.exception_handler(AuctionStarted)
async def auction_started(request: Request, exc: AuctionStarted):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class AuctionNotStarted(Exception):
    """Indicate the user that the auction has not started"""

    def __init__(self) -> None:
        self.msg = "This auction has not yet started!"
        super().__init__()


@app.exception_handler(AuctionNotStarted)
async def auction_not_started(request: Request, exc: AuctionNotStarted):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class AuctionFinished(Exception):
    def __init__(self) -> None:
        self.msg = (
            "This auction has already finished, you cannot create/update a bid for it."
        )
        super().__init__()


@app.exception_handler(AuctionFinished)
async def auction_started(request: Request, exc: AuctionFinished):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class BadDates(Exception):
    def __init__(self) -> None:
        self.msg = "The auction cannot finish before starting!"
        super().__init__()


@app.exception_handler(BadDates)
async def bad_dates(request: Request, exc: BadDates):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class BadAmmount(Exception):
    def __init__(self, auction_price, offer_price) -> None:
        self.msg = f"Offered ammount: {offer_price} has to be bigger than the auction price: {auction_price}"
        super().__init__()


@app.exception_handler(BadAmmount)
async def bad_dates(request: Request, exc: BadAmmount):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class AuctionTimeInvalid(Exception):
    def __init__(self) -> None:
        self.msg = f"Time passed for the auction is invalid."
        super().__init__()


@app.exception_handler(AuctionTimeInvalid)
async def bad_dates(request: Request, exc: AuctionTimeInvalid):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )


class WalletNotFound(Exception):
    def __init__(self) -> None:
        self.msg = (
            "You don't have a wallet created for this operation, please create one"
        )
        super().__init__()


@app.exception_handler(WalletNotFound)
async def wallet_not_found(request: Request, exc: WalletNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.msg},
    )


class MoneyNotEnoguh(Exception):
    def __init__(self) -> None:
        self.msg = "You don't have enough money in your wallet"
        super().__init__()


@app.exception_handler(MoneyNotEnoguh)
async def wallet_not_found(request: Request, exc: MoneyNotEnoguh):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.msg},
    )
