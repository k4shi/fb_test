import json
from datetime import datetime

import pytest
from aiohttp import web

# from aiohttp.pytest_plugin import aiohttp_client
from app import visited_post, domains_get


@pytest.fixture
async def cli(loop, aiohttp_client):
    app = web.Application()
    app.router.add_post('/visited_links', visited_post)
    app.router.add_get('/visited_domains', domains_get)
    client = await aiohttp_client(app)
    return client


async def test_services(cli):
    data = {
        "links": [
            "https://ya.ru",
            "https://ya.ru?q=123",
            "funbox.ru",
            "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
        ]
    }
    resp = await cli.post('/visited_links', data=json.dumps(data))
    assert resp.status == 200

    # Invalid date

    invalide_date_from = int(datetime.now().timestamp())
    invalide_date_to = int(datetime.now().timestamp()) + 15
    resp = await cli.get('/visited_domains?from={}&to={}'.format(invalide_date_to, invalide_date_from))
    assert resp.status == 200
    msg_body = json.loads(await resp.text())
    assert msg_body == {"status": "ok"}

    # Valid date
    correct_date_from = int(datetime.now().timestamp()) - 15
    correct_date_to = int(datetime.now().timestamp())
    resp = await cli.get('/visited_domains?from={}&to={}'.format(correct_date_to, correct_date_to))
    assert resp.status == 200
    msg_body = json.loads(await resp.text())

    assert 'domains' in msg_body
