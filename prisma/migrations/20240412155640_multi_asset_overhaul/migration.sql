/*
  Warnings:

  - You are about to drop the `RunTests` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the column `runTestID` on the `TestThree` table. All the data in the column will be lost.
  - You are about to drop the column `runTestID` on the `TimeSeries` table. All the data in the column will be lost.
  - You are about to drop the column `runTestID` on the `SpillEvent` table. All the data in the column will be lost.
  - You are about to drop the column `runTestID` on the `Summary` table. All the data in the column will be lost.
  - Added the required column `assetTestID` to the `TestThree` table without a default value. This is not possible if the table is not empty.
  - Added the required column `assetTestID` to the `TimeSeries` table without a default value. This is not possible if the table is not empty.
  - Added the required column `assetTestID` to the `SpillEvent` table without a default value. This is not possible if the table is not empty.
  - Added the required column `assetTestID` to the `Summary` table without a default value. This is not possible if the table is not empty.

*/
-- DropTable
PRAGMA foreign_keys=off;
DROP TABLE "RunTests";
PRAGMA foreign_keys=on;

-- CreateTable
CREATE TABLE "Assets" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "runID" INTEGER NOT NULL,
    CONSTRAINT "Assets_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "AssetTests" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "assetID" INTEGER NOT NULL,
    "testID" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    CONSTRAINT "AssetTests_assetID_fkey" FOREIGN KEY ("assetID") REFERENCES "Assets" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "AssetTests_testID_fkey" FOREIGN KEY ("testID") REFERENCES "Tests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_TestThree" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" TEXT NOT NULL,
    "formulaAInput" REAL,
    "consentFPFInput" REAL,
    "complianceStatus" TEXT NOT NULL,
    "formulaAStatus" TEXT NOT NULL,
    "consentFPFStatus" TEXT NOT NULL,
    "assetTestID" INTEGER NOT NULL,
    CONSTRAINT "TestThree_assetTestID_fkey" FOREIGN KEY ("assetTestID") REFERENCES "AssetTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_TestThree" ("complianceStatus", "consentFPFInput", "consentFPFStatus", "formulaAInput", "formulaAStatus", "id", "year") SELECT "complianceStatus", "consentFPFInput", "consentFPFStatus", "formulaAInput", "formulaAStatus", "id", "year" FROM "TestThree";
DROP TABLE "TestThree";
ALTER TABLE "new_TestThree" RENAME TO "TestThree";
CREATE TABLE "new_TimeSeries" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "dateTime" DATETIME NOT NULL,
    "intensity" REAL NOT NULL,
    "depth" REAL NOT NULL,
    "rollingDepth" REAL NOT NULL,
    "classification" TEXT NOT NULL,
    "spillAllowed" TEXT,
    "dayType" TEXT NOT NULL,
    "result" TEXT,
    "assetTestID" INTEGER NOT NULL,
    CONSTRAINT "TimeSeries_assetTestID_fkey" FOREIGN KEY ("assetTestID") REFERENCES "AssetTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_TimeSeries" ("classification", "dateTime", "dayType", "depth", "id", "intensity", "result", "rollingDepth", "spillAllowed") SELECT "classification", "dateTime", "dayType", "depth", "id", "intensity", "result", "rollingDepth", "spillAllowed" FROM "TimeSeries";
DROP TABLE "TimeSeries";
ALTER TABLE "new_TimeSeries" RENAME TO "TimeSeries";
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
    "assetTestID" INTEGER NOT NULL,
    CONSTRAINT "SpillEvent_assetTestID_fkey" FOREIGN KEY ("assetTestID") REFERENCES "AssetTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_SpillEvent" ("classification", "end", "id", "maxDepthInHour", "maxIntensity", "runName", "start", "test1", "test2", "totalDepth", "volume") SELECT "classification", "end", "id", "maxDepthInHour", "maxIntensity", "runName", "start", "test1", "test2", "totalDepth", "volume" FROM "SpillEvent";
DROP TABLE "SpillEvent";
ALTER TABLE "new_SpillEvent" RENAME TO "SpillEvent";
CREATE TABLE "new_Summary" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" TEXT NOT NULL,
    "dryPerc" REAL NOT NULL,
    "heavyPerc" REAL NOT NULL,
    "spillPerc" REAL NOT NULL,
    "unsatisfactorySpills" INTEGER NOT NULL,
    "substandardSpills" INTEGER NOT NULL,
    "satisfactorySpills" INTEGER NOT NULL,
    "totalIntensity" REAL NOT NULL,
    "assetTestID" INTEGER NOT NULL,
    CONSTRAINT "Summary_assetTestID_fkey" FOREIGN KEY ("assetTestID") REFERENCES "AssetTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_Summary" ("dryPerc", "heavyPerc", "id", "satisfactorySpills", "spillPerc", "substandardSpills", "totalIntensity", "unsatisfactorySpills", "year") SELECT "dryPerc", "heavyPerc", "id", "satisfactorySpills", "spillPerc", "substandardSpills", "totalIntensity", "unsatisfactorySpills", "year" FROM "Summary";
DROP TABLE "Summary";
ALTER TABLE "new_Summary" RENAME TO "Summary";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
