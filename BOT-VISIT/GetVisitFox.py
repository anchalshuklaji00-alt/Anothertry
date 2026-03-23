import httpx
import asyncio
uid = input("ENTER UID: ")
async def send_request(client, url, request_id):
    try:
        response = await client.get(url)
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                json_data = response.json()
                print(f"Request {request_id}: Response JSON = {json_data}")
                return json_data
            except Exception as e:
                print(f"Request {request_id}: Invalid JSON = {e}")
                return {"error": "Invalid JSON"}
        else:
            print(f"Request {request_id}: Raw Response = {response.text}")
            return {"response": response.text}
    except Exception as e:
        print(f"Request {request_id}: Error = {str(e)}")
        return {"error": str(e)}
async def main():
    url = f"https://foxvisit.vercel.app/visit?uid={uid}"
    tasks = []
    async with httpx.AsyncClient() as client:
        for i in range(500):
            task = asyncio.create_task(send_request(client, url, i + 1))
            tasks.append(task)
            await asyncio.sleep(0.1)
        results = await asyncio.gather(*tasks)
    for result in results:
        print(result)
if __name__ == "__main__":
    asyncio.run(main())