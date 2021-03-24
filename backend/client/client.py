from fastapi import APIRouter
from backend.models.models import Repair, RepairInDB
import backend.database.operations as operations
from base64 import urlsafe_b64decode
from datetime import date, datetime
from typing import List

router = APIRouter()


@router.get("/repairs/{owner}", response_model=List[RepairInDB])
def client_index(owner: str):
    valid_groups = ["privileged", "nonprivileged"]
    return operations.get_repairs(owner, groups=valid_groups)


@router.post("/add_repair", response_model=RepairInDB)
def add_repair(repair: Repair):
    repair.hash_key = f"REPAIR#{repair.hash_key}"
    return operations.put_repair(repair)  # TODO redirect to get_repair?


@router.patch("/add_repair", response_model=RepairInDB)
def update_repair(repair: RepairInDB):
    return operations.patch_repair(repair)


@router.get("/repair/{repair_token}", response_model=RepairInDB)
def get_repair(repair_token):
    token = urlsafe_b64decode(repair_token).decode("utf-8").split(':')
    uuid = token[0]
    owner = token[1]
    print(f"token: {token} uuid: {uuid} owner: {owner}")
    return operations.get_repair(uuid, owner)
