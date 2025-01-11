import logging
import pytest
from app.clients.db_client import DBClient, Person, Chore, Frequency, Complexity

log = logging.getLogger(__name__)


@pytest.fixture
def db_client():
    db_url = 'sqlite:///:memory:'
    return DBClient(db_url=db_url)


def test_add_person(db_client):
    tg_user_id = '123'
    tg_group_id = 'group1'

    db_client.add_person(Person(tg_user_id=tg_user_id, tg_group_id=tg_group_id))
    result = db_client.get_person_by_tg_user_id(tg_user_id)
    log.info(f'{result.tg_group_id} == {tg_group_id}')
    assert result.tg_group_id == tg_group_id
    assert result.tg_user_id == tg_user_id
