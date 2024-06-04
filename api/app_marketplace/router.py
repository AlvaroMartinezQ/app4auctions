import os
import uuid

from fastapi import (
    APIRouter,
    status,
    BackgroundTasks,
    HTTPException,
    Query,
    Depends,
    File,
    UploadFile,
    Response,
)
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import APIKeyHeader
from loguru import logger

from app_auth.encrypt import get_current_active_user
from utils.database_context import Session
from app_auth.schemas import UserGet
from app_marketplace.controller import AuctionController, BidController
from app_marketplace.controller_buyprocess import BuyProcessController
from app_marketplace.filter import AuctionFilter
from app_marketplace.schemas import (
    AuctionGet,
    AuctionGetList,
    AuctionPost,
    BidPost,
    BidGetList,
    FilterMethods,
    ProcessList,
)
from app_marketplace.measurements import measure


router = APIRouter()


@router.get(
    "/measurements/",
    status_code=status.HTTP_200_OK,
    summary="Run measurement tests on aucitons",
)
async def measurements():
    with Session() as db:
        measure(db=db)


# Market routes - Auction
@router.get(
    "/auction/",
    response_model=AuctionGetList,
    status_code=status.HTTP_200_OK,
    summary="Get active auctions",
)
async def get_auctions(
    page: int = Query(1, description="The page to query, from 1 to infinite", ge=1),
    limit: int = Query(20, description="The number of auctions to return", ge=3, le=25),
):
    with Session() as db:
        return AuctionController(session=db).get(page=page, limit=limit)


@router.get(
    "/auction/test/",
)
async def test():
    with Session() as db:
        # return AuctionFilter(db, "").exp_one()
        return AuctionFilter(db, "").exp_two()


@router.get(
    "/auction/search/",
    status_code=status.HTTP_200_OK,
    summary="Get active auctions ordered based on a filter criteria and available filtering methods",
)
async def get_filter_auctions(
    filter_text: str, method: "FilterMethods" = FilterMethods.tfidf
):
    with Session() as db:
        return AuctionFilter(session=db, method=method).filter(user_search=filter_text)


@router.post(
    "/auction/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new auction",
)
async def post_auction(
    auction_data: "AuctionPost",
    current_user: "UserGet" = Depends(get_current_active_user),
):
    with Session() as db:
        if AuctionController(session=db).post(
            auction_data=auction_data,
            user=current_user,
        ):
            return {"status": "Created new auction"}


@router.get(
    "/auction/image/{auction_id}/",
    status_code=status.HTTP_200_OK,
    summary="Get an image for an existing auction",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}}},
)
def get_image(
    auction_id: uuid.UUID,
):
    path = f"./pics/{auction_id}.png"
    if os.path.exists(path):
        return FileResponse(path=path, media_type="image/png")
    else:
        pass


@router.post(
    "/auction/image/{auction_id}/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an image for an existing auction",
)
def upload_image(
    auction_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: "UserGet" = Depends(get_current_active_user),
):
    with Session() as db:
        if (
            AuctionController(session=db).user_can_edit(
                auction_id=auction_id, user=current_user
            )
            == False
        ):
            return {"error": "You cannot update this content!"}
    if not file.filename.endswith("png"):
        return {"error": "Only png files are accepted!"}
    try:
        contents = file.file.read()
        file_location = f"./pics/{auction_id}.{file.filename.split('.')[-1]}"
        with open(file_location, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(str(e))
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded the image"}


@router.get(
    "/auction/{auction_id}/",
    response_model=AuctionGet,
    status_code=status.HTTP_200_OK,
    summary="Get an auction by its UUID",
)
async def get_auction(
    auction_id: uuid.UUID,
):
    with Session() as db:
        return AuctionController(session=db).get_auction(auction_id=auction_id)


@router.put(
    "/auction/{auction_id}/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update an existing auction",
)
async def put_auction(
    auction_id: uuid.UUID,
    auction_data: "AuctionPost",
    current_user: "UserGet" = Depends(get_current_active_user),
):
    with Session() as db:
        if AuctionController(session=db).put(
            auction_id=auction_id, auction_data=auction_data, user=current_user
        ):
            return {"status": "Updated auction"}


@router.delete(
    "/auction/{auction_id}/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete an existing auction",
)
async def delete_auction(
    auction_id: uuid.UUID,
    current_user: "UserGet" = Depends(get_current_active_user),
):
    with Session() as db:
        if AuctionController(session=db).delete(
            auction_id=auction_id, user=current_user
        ):
            return {"status": "Deleted auction"}


# Market routes - Bids
@router.get(
    "/bid/{bid_id}/",
    response_model=AuctionGet,
    status_code=status.HTTP_200_OK,
    summary="Get an auction based on a bid UUID reference",
)
async def get_auction_bid_ref(
    bid_id: uuid.UUID,
    current_user: "UserGet" = Depends(get_current_active_user),
):
    with Session() as db:
        return BidController(db).get_auction(bid_id)


@router.post(
    "/bid/{auction_id}/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bid for a given auction",
)
async def post_bid(
    auction_id: uuid.UUID,
    bid_data: "BidPost",
    background_tasks: BackgroundTasks,
    current_user: "UserGet" = Depends(get_current_active_user),
):
    with Session() as db:
        if BidController(session=db).post(
            bid_data=bid_data,
            auction_id=auction_id,
            background_tasks=background_tasks,
            user=current_user,
        ):
            return {"status": "Bid created successfully"}


@router.put(
    "/bid/{auction_id}/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update a bid for a given auction",
)
async def put_bid(
    auction_id: uuid.UUID,
    bid_data: "BidPost",
    background_tasks: BackgroundTasks,
    current_user: "UserGet" = Depends(get_current_active_user),
):
    with Session() as db:
        if BidController(session=db).put(
            bid_data=bid_data,
            auction_id=auction_id,
            user=current_user,
            background_tasks=background_tasks,
        ):
            return {"status": "Bid updated successfully"}


# Market routes - user
@router.get(
    "/auctions/user/",
    response_model=AuctionGetList,
    status_code=status.HTTP_200_OK,
    summary="Get your auctions",
)
async def get_user_auctions(current_user: UserGet = Depends(get_current_active_user)):
    with Session() as db:
        return AuctionController(session=db).get_user_auctions(user=current_user)


@router.get(
    "/auction/user/owned/{auction_id}/",
    status_code=status.HTTP_200_OK,
    summary="Check if user can edit the requested auction",
)
async def get_user_auctions(
    auction_id: uuid.UUID, current_user: UserGet = Depends(get_current_active_user)
):
    with Session() as db:
        res = AuctionController(session=db).user_can_edit(
            auction_id=auction_id, user=current_user
        )

        if res:
            return JSONResponse({"status": "Edit enabled"}, status.HTTP_200_OK)
        # Log if False is returned - could be someone trying to bypass the api security
        logger.warning(
            f"User {current_user.email} tried to edit auction {auction_id} without ownership"
        )
        return JSONResponse(
            {"status": "Edit not enabled"}, status.HTTP_401_UNAUTHORIZED
        )


@router.get(
    "/bids/user/",
    response_model=BidGetList,
    status_code=status.HTTP_200_OK,
    summary="Get your bids",
)
async def get_user_bids(current_user: UserGet = Depends(get_current_active_user)):
    with Session() as db:
        return BidController(session=db).get_user_bids(user=current_user)


@router.get(
    "/process/buy/user/",
    response_model=ProcessList,
    status_code=status.HTTP_200_OK,
    summary="Get your buy processes",
)
async def get_user_buys(current_user: UserGet = Depends(get_current_active_user)):
    with Session() as db:
        return BuyProcessController(db).get_buyprocess(current_user)


@router.get(
    "/process/sell/user/",
    response_model=ProcessList,
    status_code=status.HTTP_200_OK,
    summary="Get your sell processes",
)
async def get_user_sells(current_user: UserGet = Depends(get_current_active_user)):
    with Session() as db:
        return BuyProcessController(db).get_sellprocess(current_user)


# Endpoints used by Celery
CELERY_KEY = APIKeyHeader(name=os.getenv("CELERY_TOKEN_NAME"), auto_error=False)


def check_key(celery_key: str = Depends(CELERY_KEY)) -> bool:
    if celery_key == os.getenv("CELERY_TOKEN_VALUE"):
        return True
    raise HTTPException(status_code=401, detail="Invalid API key")


@router.post(
    "/auction-start/{auction_id}/",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def update_clients(
    auction_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    auth: bool = Depends(check_key),
):
    with Session() as db:
        AuctionController(session=db).update_active_clients(
            auction_id=auction_id, background_tasks=background_tasks
        )
