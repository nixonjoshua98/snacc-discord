
import json
import httpx
import gzip
import asyncio
import base64

import datetime as dt


class Server:
	REQUEST_DELAY = (1.0 / 5)

	__last_request = dt.datetime.utcnow()

	@classmethod
	async def send_request(cls, path, data) -> dict:
		now = dt.datetime.utcnow()

		url = f"http://174.138.116.133:8443/api/{path}"

		data_bytes = json.dumps(data).encode("utf-8")

		data_compressed = gzip.compress(data_bytes)

		put_data = base64.b64encode(data_compressed).decode("utf-8")

		secs_since_request = (now - cls.__last_request).total_seconds()

		# - Impose a rate limit
		if secs_since_request <= cls.REQUEST_DELAY:
			await asyncio.sleep(cls.REQUEST_DELAY - secs_since_request)

		async with httpx.AsyncClient() as client:
			try:
				r = await client.put(url, data=put_data, timeout=10.0)
			except httpx.ReadTimeout:
				return None

		cls.__last_request = now

		if r.status_code == httpx.codes.ok:
			resp = base64.b64decode(r.content)

			resp_uncompressed = gzip.decompress(resp)

			return json.loads(resp_uncompressed.decode("utf-8"))

		return None
