import shelve

from test_task.databases.repository import Repository
from test_task.types import Result


class ShelveDB(Repository):
    db_name = "./db"

    def save(self, data: list[Result]):
        with shelve.open(self.db_name) as db:
            for item in data:
                db[item.name] = item

    def get(self, *, _filter: str, limit: int, offset: int) -> list[Result]:
        with shelve.open(self.db_name) as db:
            return [value.__dict__
                    for value in db.values()
                    if value.name.startswith(_filter)][offset: limit]
