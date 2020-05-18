from datetime import datetime
from urllib.parse import urlparse

from aiohttp import web

from services.connection import redis_connection as client


async def domains_get(request):
    try:
        timestamp_from = int(request.query.get('from'))
        timestamp_to = int(request.query.get('to'))
    except Exception as e:
        return web.json_response({"status": "ok"})

    if timestamp_from > timestamp_to or timestamp_to > datetime.now().timestamp():
        return web.json_response({"status": "ok"})

    # Формируем списоr всех ключей пользователя
    try:
        time_range = [int(i.decode('utf-8').split(":")[1]) for i in client().keys("user:*")]
    except Exception as e:
        return web.json_response({"status": "ok"})
    valid_value = []
    # Фильтруем валидный диапозон
    for i in time_range:
        if i >= int(timestamp_from) and i <= int(timestamp_to):
            valid_value.append(i)

    urls = []
    for i in valid_value:
        try:
            _user_key = client().hgetall("user:{}".format(i))
        except Exception as e:
            return web.json_response({"status": "ok"})
        for key, val in _user_key.items():
            parsed_url = urlparse(val.decode('utf-8'))

            url = '{uri}'.format(uri=parsed_url.netloc) if parsed_url.netloc else parsed_url.path
            if url not in urls:
                urls.append(url)

    return web.json_response({"domains": urls, "status": "ok"})


async def visited_post(request):
    data = await request.json()
    if 'links' in data:
        data['timestamp'] = int(datetime.now().timestamp())
        k = 0
        try:
            for i in data['links']:
                client().hset("user:{}".format(data['timestamp']), k, i)
                k += 1
        except Exception as e:
            return web.json_response({"status": "ok"})
        return web.json_response({"status": "ok"})
    return web.json_response({"status": "ok"})


app = web.Application()

app.add_routes([web.post('/visited_links', visited_post),
                web.get('/visited_domains', domains_get)])

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8000)
