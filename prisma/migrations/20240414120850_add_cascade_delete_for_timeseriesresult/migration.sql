/*
  Warnings:

  - You are about to drop the column `runName` on the `SpillEvent` table. All the data in the column will be lost.
  - You are about to drop the column `assetTestID` on the `TimeSeries` table. All the data in the column will be lost.
  - You are about to drop the column `result` on the `TimeSeries` table. All the data in the column will be lost.
  - Added the required column `runID` to the `TimeSeries` table without a default value. This is not possible if the table is not empty.

*/
-- CreateTable
CREATE TABLE "TimeSeriesResult" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "assetID" INTEGER NOT NULL,
    "timeSeriesID" INTEGER NOT NULL,
    "result" TEXT,
    CONSTRAINT "TimeSeriesResult_assetID_fkey" FOREIGN KEY ("assetID") REFERENCES "Assets" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "TimeSeriesResult_timeSeriesID_fkey" FOREIGN KEY ("timeSeriesID") REFERENCES "TimeSeries" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_SpillEvent" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "start" DATETIME NOT NULL,
    "end" DATETIME NOT NULL,
    "volume" REAL NOT NULL,
    "maxIntensity" REAL NOT NULL,
    "maxDepthInHour" REAL NOT NULL,
    "totalDepth" REAL NOT NULL,
    "test1" TEXT NOT NULL,
    "test2" TEXT NOT NULL,
    "classification" TEXT NOT NULL,
    "assetTestID" INTEGER NOT NULL,
    CONSTRAINT "SpillEvent_assetTestID_fkey" FOREIGN KEY ("assetTestID") REFERENCES "AssetTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_SpillEvent" ("assetTestID", "classification", "end", "id", "maxDepthInHour", "maxIntensity", "start", "test1", "test2", "totalDepth", "volume") SELECT "assetTestID", "classification", "end", "id", "maxDepthInHour", "maxIntensity", "start", "test1", "test2", "totalDepth", "volume" FROM "SpillEvent";
DROP TABLE "SpillEvent";
ALTER TABLE "new_SpillEvent" RENAME TO "SpillEvent";
CREATE TABLE "new_TimeSeries" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "dateTime" DATETIME NOT NULL,
    "intensity" REAL NOT NULL,
    "depth" REAL NOT NULL,
    "rollingDepth" REAL NOT NULL,
    "classification" TEXT NOT NULL,
    "spillAllowed" TEXT,
    "dayType" TEXT NOT NULL,
    "runID" INTEGER NOT NULL,
    CONSTRAINT "TimeSeries_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_TimeSeries" ("classification", "dateTime", "dayType", "depth", "id", "intensity", "rollingDepth", "spillAllowed") SELECT "classification", "dateTime", "dayType", "depth", "id", "intensity", "rollingDepth", "spillAllowed" FROM "TimeSeries";
DROP TABLE "TimeSeries";
ALTER TABLE "new_TimeSeries" RENAME TO "TimeSeries";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
