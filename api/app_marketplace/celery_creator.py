import typing
import datetime

from celery.result import AsyncResult

from utils.database_context import Session as db
from app_marketplace.models import Auction, CeleryTask
from executor import app as celery_app

if typing.TYPE_CHECKING:
    from sqlalchemy.orm.session import Session as SQLSession


class CeleryCreator:
    """Task, can be of type:
    -> end_task
    -> send_task
    """

    def __init__(self) -> None:
        pass

    def add_tasks(
        self, session: "SQLSession", auction: "Auction", update: bool = False
    ) -> None:
        if update:
            celery_tasks: list["CeleryTask"] = (
                session.query(CeleryTask)
                .filter(CeleryTask.auction_id == auction.id)
                .all()
            )
            if len(celery_tasks) > 0:
                for task in celery_tasks:
                    self.__revoke_task__(task.task_uuid)
                    session.delete(task)
                    session.commit()

        for task_type in ["end_auction", "send_auction"]:
            task_id = self.__send_task__(auction, task_type)
            c_data = {
                "task_type": task_type,
                "task_uuid": task_id,
                "auction_id": auction.id,
            }
            c_obj = CeleryTask(**c_data)
            session.add(c_obj)
            session.commit()

    def __revoke_task__(self, task_id: str) -> None:
        celery_app.control.revoke(task_id, terminate=True)

    def __send_task__(self, auction: "Auction", t_type: str):
        if t_type == "end_auction":
            time = auction.finish_date - datetime.timedelta(
                hours=2
            )  # Depends on summer time
        elif t_type == "send_auction":
            time = auction.start_date - datetime.timedelta(
                hours=2
            )  # Depends on summer time
        celery_id: AsyncResult = celery_app.send_task(
            "executor." + t_type,
            args=[auction.id],
            eta=time,
        )
        return celery_id.id
