/*
  Warnings:

  - You are about to drop the `ProcessedResult` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `runTestID` to the `Summary` table without a default value. This is not possible if the table is not empty.
  - Added the required column `runTestID` to the `SpillEvent` table without a default value. This is not possible if the table is not empty.
  - Added the required column `runTestID` to the `TimeSeries` table without a default value. This is not possible if the table is not empty.

*/
-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "ProcessedResult";
PRAGMA foreign_keys=on;

-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Summary" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" TEXT NOT NULL,
    "dryPerc" REAL NOT NULL,
    "heavyPerc" REAL NOT NULL,
    "spillPerc" REAL NOT NULL,
    "unsatisfactorySpills" INTEGER NOT NULL,
    "substandardSpills" INTEGER NOT NULL,
    "satisfactorySpills" INTEGER NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "Summary_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_Summary" ("dryPerc", "heavyPerc", "id", "satisfactorySpills", "spillPerc", "substandardSpills", "unsatisfactorySpills", "year") SELECT "dryPerc", "heavyPerc", "id", "satisfactorySpills", "spillPerc", "substandardSpills", "unsatisfactorySpills", "year" FROM "Summary";
DROP TABLE "Summary";
ALTER TABLE "new_Summary" RENAME TO "Summary";
CREATE UNIQUE INDEX "Summary_runTestID_key" ON "Summary"("runTestID");
CREATE TABLE "new_SpillEvent" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "start" DATETIME NOT NULL,
    "end" DATETIME NOT NULL,
    "volume" REAL NOT NULL,
    "runName" TEXT NOT NULL,
    "maxIntensity" REAL NOT NULL,
    "maxDepthInHour" REAL NOT NULL,
    "totalDepth" REAL NOT NULL,
    "test1" TEXT NOT NULL,
    "test2" TEXT NOT NULL,
    "classification" TEXT NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "SpillEvent_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_SpillEvent" ("classification", "end", "id", "maxDepthInHour", "maxIntensity", "runName", "start", "test1", "test2", "totalDepth", "volume") SELECT "classification", "end", "id", "maxDepthInHour", "maxIntensity", "runName", "start", "test1", "test2", "totalDepth", "volume" FROM "SpillEvent";
DROP TABLE "SpillEvent";
ALTER TABLE "new_SpillEvent" RENAME TO "SpillEvent";
CREATE TABLE "new_TimeSeries" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "dateTime" DATETIME NOT NULL,
    "intensity" REAL NOT NULL,
    "depth" REAL NOT NULL,
    "rollingDepth" REAL NOT NULL,
    "classification" TEXT NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "TimeSeries_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_TimeSeries" ("classification", "dateTime", "depth", "id", "intensity", "rollingDepth") SELECT "classification", "dateTime", "depth", "id", "intensity", "rollingDepth" FROM "TimeSeries";
DROP TABLE "TimeSeries";
ALTER TABLE "new_TimeSeries" RENAME TO "TimeSeries";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
