from prisma import Prisma
import asyncio

db = None

tests = {
    "Test 1": "Dry Day Discharge",
    "Test 2": "Rainfall Discharge",
    "Test 3": "Formula A & Consent"
}


async def preload():
    global db
    db = Prisma()
    await db.connect()

    for t in tests:
        # Check duplicates and skip if already present
        check = await db.tests.find_first(where={
            "name": t
        })
        if (check):
            continue
        await db.tests.create(data={
            "name": t,
            "description": tests[t]
        })

print("Database successfully preloaded")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(preload())
    finally:
        loop.close()
