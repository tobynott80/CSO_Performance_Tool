from prisma import Prisma

db = None


async def initDB():
    """
    Initializes the database connection and returns the database instance.

    If the database instance is already initialized, it returns the existing instance.

    Returns:
        The database instance.
    """
    global db
    if db != None:
        return db
    print("Initialized Prisma")
    db = Prisma()
    await db.connect()
    return db
