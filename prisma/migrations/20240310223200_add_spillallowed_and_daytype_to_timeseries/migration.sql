/*
  Warnings:

  - Added the required column `dayType` to the `TimeSeries` table without a default value. This is not possible if the table is not empty.
  - Added the required column `spillAllowed` to the `TimeSeries` table without a default value. This is not possible if the table is not empty.

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
    "spillAllowed" TEXT NOT NULL,
    "dayType" TEXT NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "TimeSeries_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_TimeSeries" ("classification", "dateTime", "depth", "id", "intensity", "rollingDepth", "runTestID") SELECT "classification", "dateTime", "depth", "id", "intensity", "rollingDepth", "runTestID" FROM "TimeSeries";
DROP TABLE "TimeSeries";
ALTER TABLE "new_TimeSeries" RENAME TO "TimeSeries";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
