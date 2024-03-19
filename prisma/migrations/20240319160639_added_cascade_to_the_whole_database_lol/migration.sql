-- RedefineTables
PRAGMA foreign_keys=OFF;
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
    CONSTRAINT "SpillEvent_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_SpillEvent" ("classification", "end", "id", "maxDepthInHour", "maxIntensity", "runName", "runTestID", "start", "test1", "test2", "totalDepth", "volume") SELECT "classification", "end", "id", "maxDepthInHour", "maxIntensity", "runName", "runTestID", "start", "test1", "test2", "totalDepth", "volume" FROM "SpillEvent";
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
    "result" TEXT,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "TimeSeries_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_TimeSeries" ("classification", "dateTime", "dayType", "depth", "id", "intensity", "result", "rollingDepth", "runTestID", "spillAllowed") SELECT "classification", "dateTime", "dayType", "depth", "id", "intensity", "result", "rollingDepth", "runTestID", "spillAllowed" FROM "TimeSeries";
DROP TABLE "TimeSeries";
ALTER TABLE "new_TimeSeries" RENAME TO "TimeSeries";
CREATE TABLE "new_TestThree" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" TEXT NOT NULL,
    "formulaAInput" REAL,
    "consentFPFInput" REAL,
    "complianceStatus" TEXT NOT NULL,
    "formulaAStatus" TEXT NOT NULL,
    "consentFPFStatus" TEXT NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "TestThree_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_TestThree" ("complianceStatus", "consentFPFInput", "consentFPFStatus", "formulaAInput", "formulaAStatus", "id", "runTestID", "year") SELECT "complianceStatus", "consentFPFInput", "consentFPFStatus", "formulaAInput", "formulaAStatus", "id", "runTestID", "year" FROM "TestThree";
DROP TABLE "TestThree";
ALTER TABLE "new_TestThree" RENAME TO "TestThree";
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
    CONSTRAINT "Summary_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_Summary" ("dryPerc", "heavyPerc", "id", "runTestID", "satisfactorySpills", "spillPerc", "substandardSpills", "unsatisfactorySpills", "year") SELECT "dryPerc", "heavyPerc", "id", "runTestID", "satisfactorySpills", "spillPerc", "substandardSpills", "unsatisfactorySpills", "year" FROM "Summary";
DROP TABLE "Summary";
ALTER TABLE "new_Summary" RENAME TO "Summary";
CREATE TABLE "new_RunTests" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "runID" INTEGER NOT NULL,
    "testID" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    CONSTRAINT "RunTests_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "RunTests_testID_fkey" FOREIGN KEY ("testID") REFERENCES "Tests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_RunTests" ("id", "runID", "status", "testID") SELECT "id", "runID", "status", "testID" FROM "RunTests";
DROP TABLE "RunTests";
ALTER TABLE "new_RunTests" RENAME TO "RunTests";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
