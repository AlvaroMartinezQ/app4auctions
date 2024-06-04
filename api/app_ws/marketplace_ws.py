import uuid
import json
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from utils.database_context import Session
from app_marketplace.models import Auction, Bid
from app_marketplace.schemas import AuctionGet, BidGet


router = APIRouter()


# Generic conneciton class
class Connection:
    def __init__(self, ws_client: WebSocket, uuid: uuid.UUID) -> None:
        self.ws_client: WebSocket = ws_client
        self.uuid = uuid


# Manager and ws for marketplace
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[Connection] = []

    async def connect(self, client: Connection) -> None:
        await client.ws_client.accept()
        self.active_connections.append(client)

    def disconnect(self, client: Connection) -> None:
        self.active_connections.remove(client)


# In-memory list of active connections
market_manager = ConnectionManager()


@router.websocket("/marketplace/ws/")
async def marketplace_ws(websocket: WebSocket):
    connection = Connection(websocket, uuid.uuid4())
    await market_manager.connect(connection)

    try:
        while True:
            txt = await connection.ws_client.receive_text()
            if txt == "close":
                market_manager.disconnect(connection)
                await connection.ws_client.close()
                break
    except (
        WebSocketDisconnect,
        ConnectionClosedError,
        ConnectionClosedOK,
        RuntimeError,
    ) as _:
        market_manager.disconnect(connection)


async def new_auction(auction_id: uuid.UUID) -> None:
    if len(market_manager.active_connections) > 0:
        with Session() as db:
            auction: Auction = (
                db.query(Auction).filter(Auction.id == auction_id).first()
            )
            if auction:
                parsed_auction = AuctionGet(**auction.__dict__)
                for connection in market_manager.active_connections:
                    await connection.ws_client.send_json(
                        data=json.loads(parsed_auction.json())
                    )


# Manager and ws for specific auction
class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict = {}

    async def connect(self, auction_id: uuid.UUID, client: Connection) -> None:
        await client.ws_client.accept()
        if auction_id in self.rooms:
            # Room exists, append to it
            active_connections: list[Connection] = self.rooms.get(auction_id)
            active_connections.append(client)
        else:
            # Create room
            active_connections = [client]
        self.rooms[auction_id] = active_connections

    def disconnect(self, auction_id: uuid.UUID, client: Connection) -> None:
        if auction_id in self.rooms:
            active_connections: list[Connection] = self.rooms.get(auction_id)
            active_connections.remove(client)
            if active_connections == []:
                # Delete the room from memory if no more clients are connected
                self.rooms.pop(auction_id)
            else:
                # Maintain the existing active connections
                self.rooms[auction_id] = active_connections


# In-memory list of active connections
room_manager = RoomManager()


@router.websocket("/marketplace/room/{auction_id}/")
async def room_ws(websocket: WebSocket, auction_id: uuid.UUID):
    auction = True
    with Session() as db:
        if not (db.query(Auction).filter(Auction.id == auction_id).first()):
            auction = False

    connection = Connection(websocket, uuid.uuid4())
    await room_manager.connect(auction_id, connection)

    if not auction:
        await connection.ws_client.send_json(
            {
                "error": f"Auction {auction_id} is not active or does not exist. Closing your connection..."
            }
        )
        await connection.ws_client.close()
        return

    try:
        while True:
            txt = await connection.ws_client.receive_text()
            if txt == "close":
                room_manager.disconnect(auction_id, connection)
                await connection.ws_client.close()
                break
    except (
        WebSocketDisconnect,
        ConnectionClosedError,
        ConnectionClosedOK,
        RuntimeError,
    ) as _:
        room_manager.disconnect(auction_id, connection)


async def new_bid(auction_id: uuid.UUID, bid_id: uuid.UUID) -> None:
    if auction_id in room_manager.rooms:
        with Session() as db:
            bid: Bid = db.query(Bid).filter(Bid.id == bid_id).first()
            if bid:
                parsed_bid = BidGet(**bid.__dict__)
                conns: list[Connection] = room_manager.rooms.get(auction_id)
                for connection in conns:
                    await connection.ws_client.send_json(
                        data=json.loads(parsed_bid.json())
                    )
