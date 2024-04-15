/*
  Warnings:

  - You are about to drop the `TimeSeriesResult` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `result` to the `TimeSeries` table without a default value. This is not possible if the table is not empty.

*/
-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "TimeSeriesResult";
PRAGMA foreign_keys=on;

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
    "runID" INTEGER NOT NULL,
    CONSTRAINT "TimeSeries_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_TimeSeries" ("classification", "dateTime", "dayType", "depth", "id", "intensity", "rollingDepth", "runID", "spillAllowed") SELECT "classification", "dateTime", "dayType", "depth", "id", "intensity", "rollingDepth", "runID", "spillAllowed" FROM "TimeSeries";
DROP TABLE "TimeSeries";
ALTER TABLE "new_TimeSeries" RENAME TO "TimeSeries";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
