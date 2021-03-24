from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class User(BaseModel):
    email: str
    name: Optional[str]
    main_group: Optional[str]
    sub_groups: Optional[List[str]]


class UserInDB(User):
    hashed_password: str


class Repair(BaseModel):
    hash_key: str
    customer_name: str
    customer_email: Optional[str]
    customer_phone: str
    extra_details: str
    group: str


class RepairInDB(Repair):
    range_key: str
    uuid: str
    token: str
