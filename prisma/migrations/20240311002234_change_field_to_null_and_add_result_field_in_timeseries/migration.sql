/*
  Warnings:

  - Added the required column `result` to the `TimeSeries` table without a default value. This is not possible if the table is not empty.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_TimeSeries" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "dateTime" DATETIME NOT NULL,
    "intensity" REAL NOT NULL,
    "depth" REAL NOT NULL,
    "rollingDepth" REAL NOT NULL,
    "classification" TEXT NOT NULL,
    "spillAllowed" TEXT,
    "dayType" TEXT NOT NULL,
    "result" TEXT NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "TimeSeries_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_TimeSeries" ("classification", "dateTime", "dayType", "depth", "id", "intensity", "rollingDepth", "runTestID", "spillAllowed") SELECT "classification", "dateTime", "dayType", "depth", "id", "intensity", "rollingDepth", "runTestID", "spillAllowed" FROM "TimeSeries";
DROP TABLE "TimeSeries";
ALTER TABLE "new_TimeSeries" RENAME TO "TimeSeries";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
