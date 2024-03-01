from prisma import Prisma

db = None

async def initDB():
    global db
    if (db != None): 
        return db
    print("Initialized Prisma")
    db = Prisma()
    await db.connect()
    return db