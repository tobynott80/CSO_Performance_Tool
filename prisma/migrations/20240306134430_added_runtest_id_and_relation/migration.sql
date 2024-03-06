/*
  Warnings:

  - You are about to drop the `ImportRainfall` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `ImportSpills` table. If the table is not empty, all the data it contains will be lost.
  - The primary key for the `RunTests` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - Added the required column `id` to the `RunTests` table without a default value. This is not possible if the table is not empty.
  - Added the required column `RunTestID` to the `ProcessedResult` table without a default value. This is not possible if the table is not empty.

*/
-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "ImportRainfall";
PRAGMA foreign_keys=on;

-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "ImportSpills";
PRAGMA foreign_keys=on;

-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_RunTests" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "runID" INTEGER NOT NULL,
    "testID" INTEGER NOT NULL,
    CONSTRAINT "RunTests_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "RunTests_testID_fkey" FOREIGN KEY ("testID") REFERENCES "Tests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_RunTests" ("runID", "testID") SELECT "runID", "testID" FROM "RunTests";
DROP TABLE "RunTests";
ALTER TABLE "new_RunTests" RENAME TO "RunTests";
CREATE TABLE "new_ProcessedResult" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "summaryId" INTEGER NOT NULL,
    "timeSeriesId" INTEGER NOT NULL,
    "spillEventId" INTEGER NOT NULL,
    "RunTestID" INTEGER NOT NULL,
    CONSTRAINT "ProcessedResult_summaryId_fkey" FOREIGN KEY ("summaryId") REFERENCES "Summary" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "ProcessedResult_timeSeriesId_fkey" FOREIGN KEY ("timeSeriesId") REFERENCES "TimeSeries" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "ProcessedResult_spillEventId_fkey" FOREIGN KEY ("spillEventId") REFERENCES "SpillEvent" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "ProcessedResult_RunTestID_fkey" FOREIGN KEY ("RunTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_ProcessedResult" ("id", "spillEventId", "summaryId", "timeSeriesId") SELECT "id", "spillEventId", "summaryId", "timeSeriesId" FROM "ProcessedResult";
DROP TABLE "ProcessedResult";
ALTER TABLE "new_ProcessedResult" RENAME TO "ProcessedResult";
CREATE TABLE "new_Runs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "locationID" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "date" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Runs_locationID_fkey" FOREIGN KEY ("locationID") REFERENCES "Location" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_Runs" ("date", "id", "locationID", "name") SELECT "date", "id", "locationID", "name" FROM "Runs";
DROP TABLE "Runs";
ALTER TABLE "new_Runs" RENAME TO "Runs";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
