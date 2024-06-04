# os
from datetime import datetime

# Third party
from fastapi import APIRouter, status

# Local


router = APIRouter()


@router.get(
    "/status/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Check if the service api is online",
)
def system_status():
    return {
        "status": f"{datetime.now().strftime('%B %d, %Y @ %H:%M:%S')} - API service is online"
    }
