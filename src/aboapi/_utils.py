
import json
import httpx
import gzip
import base64


async def _send_request(path, data) -> dict:
	url = f"http://174.138.116.133:8443/api/{path}"

	data_bytes = json.dumps(data).encode("utf-8")

	data_compressed = gzip.compress(data_bytes)

	put_data = base64.b64encode(data_compressed).decode("utf-8")

	async with httpx.AsyncClient() as client:
		try:
			r = await client.put(url, data=put_data)
		except httpx.ReadTimeout as e:
			print(e)

	if r.status_code == httpx.codes.ok:
		resp = base64.b64decode(r.content)

		resp_uncompressed = gzip.decompress(resp)

		return json.loads(resp_uncompressed.decode("utf-8"))

	return None
