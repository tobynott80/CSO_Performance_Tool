/*
  Warnings:

  - Added the required column `totalIntensity` to the `Summary` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Runs" ADD COLUMN "baselineStatsFile" TEXT;
ALTER TABLE "Runs" ADD COLUMN "rainfallStatsFile" TEXT;
ALTER TABLE "Runs" ADD COLUMN "spillStatsFile" TEXT;

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
    "totalIntensity" REAL NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "Summary_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO "new_Summary" ("dryPerc", "heavyPerc", "id", "runTestID", "satisfactorySpills", "spillPerc", "substandardSpills", "unsatisfactorySpills", "year") SELECT "dryPerc", "heavyPerc", "id", "runTestID", "satisfactorySpills", "spillPerc", "substandardSpills", "unsatisfactorySpills", "year" FROM "Summary";
DROP TABLE "Summary";
ALTER TABLE "new_Summary" RENAME TO "Summary";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
