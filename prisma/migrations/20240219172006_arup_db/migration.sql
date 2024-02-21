-- CreateTable
CREATE TABLE "Location" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "Runs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "locationID" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "date" DATETIME NOT NULL,
    CONSTRAINT "Runs_locationID_fkey" FOREIGN KEY ("locationID") REFERENCES "Location" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Tests" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "RunTests" (
    "runID" INTEGER NOT NULL,
    "testID" INTEGER NOT NULL,

    PRIMARY KEY ("runID", "testID"),
    CONSTRAINT "RunTests_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "RunTests_testID_fkey" FOREIGN KEY ("testID") REFERENCES "Tests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "ImportSpills" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "runID" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    "startTime" DATETIME NOT NULL,
    "endTime" DATETIME NOT NULL,
    "volume" REAL NOT NULL,
    CONSTRAINT "ImportSpills_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "ImportRainfall" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "runID" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    "datetime" DATETIME NOT NULL,
    "depth" REAL NOT NULL,
    "intensity" REAL NOT NULL,
    CONSTRAINT "ImportRainfall_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "ProcessedResult" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "summaryId" INTEGER NOT NULL,
    "timeSeriesId" INTEGER NOT NULL,
    "spillEventId" INTEGER NOT NULL,
    CONSTRAINT "ProcessedResult_summaryId_fkey" FOREIGN KEY ("summaryId") REFERENCES "Summary" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "ProcessedResult_timeSeriesId_fkey" FOREIGN KEY ("timeSeriesId") REFERENCES "TimeSeries" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "ProcessedResult_spillEventId_fkey" FOREIGN KEY ("spillEventId") REFERENCES "SpillEvent" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Summary" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" TEXT NOT NULL,
    "dryPerc" REAL NOT NULL,
    "heavyPerc" REAL NOT NULL,
    "spillPerc" REAL NOT NULL,
    "unsatisfactorySpills" INTEGER NOT NULL,
    "substandardSpills" INTEGER NOT NULL,
    "satisfactorySpills" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "TimeSeries" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "dateTime" DATETIME NOT NULL,
    "intensity" REAL NOT NULL,
    "depth" REAL NOT NULL,
    "rollingDepth" REAL NOT NULL,
    "classification" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "SpillEvent" (
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
    "classification" TEXT NOT NULL
);
