from backend.database.botodb import BotoTable
from typing import List
from datetime import date, datetime, timedelta
from backend.models.models import RepairInDB, Repair
from uuid import uuid4
from base64 import urlsafe_b64encode

table = BotoTable()


def get_repairs(owner: str, groups: List[str] = ["nonprivileged", ], date_from: date = None, date_to: date = None, limit: int = 100) -> List[RepairInDB]:
    """
    Get all relevant repairs within a timeframe, limited to limit

    :param owner: The owner group of  the repair
    :param groups: The viewer's list of allowed groups
    :param date_from: The start date to look for repairs. Defaults to 30 days ago
    :param date_to: The end date to look for repairs. Defaults to now
    :param limit: max number of repairs to get
    :return: A list of repairs within the timeframe
    """

    if not date_from:
        date_from = (date.today() - timedelta(days=7)).isoformat()

    repairs = table.query_repairs(f"REPAIR#{owner}", date_from, groups, end_date=date_to, limit=limit)

    return repairs


def put_repair(repair: Repair) -> RepairInDB:
    """
    Create a repair ticket

    :param repair: A repair model
    :return: The repair as it stands in the database
    """
    uuid = str(uuid4())
    now = datetime.utcnow().isoformat()
    repair = RepairInDB(**{**repair.dict(), "range_key": now, "uuid": uuid, "token": urlsafe_b64encode(f"{uuid}:{now}".encode("utf-8"))})
    repair_in_db = table.put(repair)
    print(repair_in_db)
    if repair_in_db.get("ResponseMetadata").get("HTTPStatusCode") == 200:
        return repair


def patch_repair(repair: RepairInDB) -> RepairInDB:
    """
    Update a repair ticket

    :param repair: A repair model
    :return: The repair as it stands in the database
    """
    return table.put(repair)


def get_repair(uuid: str, ticket_owner: str) -> RepairInDB:
    """
    Get an individual repair ticket

    :param uuid: the UUID of a ticket
    :param ticket_owner: the owner of the ticket
    :return: The ticket
    """
    print(f"uuid {uuid} owner {ticket_owner}")
    repair = table.get_repair(uuid, ticket_owner)
    return RepairInDB(**repair)
