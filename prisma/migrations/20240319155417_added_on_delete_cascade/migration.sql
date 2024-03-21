-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Runs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "locationID" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    CONSTRAINT "Runs_locationID_fkey" FOREIGN KEY ("locationID") REFERENCES "Location" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_Runs" ("date", "description", "id", "locationID", "name") SELECT "date", "description", "id", "locationID", "name" FROM "Runs";
DROP TABLE "Runs";
ALTER TABLE "new_Runs" RENAME TO "Runs";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
