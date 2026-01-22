import asyncio

print(asyncio.__file__)


def get_feedings():
    result = asyncio.run(get_feedings_async())
    print(f"result: {result}")


async def get_feedings_async():
    await asyncio.sleep(0.01)
    return {"hello": "world"}


get_feedings())
