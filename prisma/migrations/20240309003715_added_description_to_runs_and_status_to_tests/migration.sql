/*
  Warnings:

  - Added the required column `description` to the `Runs` table without a default value. This is not possible if the table is not empty.
  - Added the required column `status` to the `RunTests` table without a default value. This is not possible if the table is not empty.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Runs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "locationID" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    CONSTRAINT "Runs_locationID_fkey" FOREIGN KEY ("locationID") REFERENCES "Location" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_Runs" ("date", "id", "locationID", "name") SELECT "date", "id", "locationID", "name" FROM "Runs";
DROP TABLE "Runs";
ALTER TABLE "new_Runs" RENAME TO "Runs";
CREATE TABLE "new_RunTests" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "runID" INTEGER NOT NULL,
    "testID" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    CONSTRAINT "RunTests_runID_fkey" FOREIGN KEY ("runID") REFERENCES "Runs" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "RunTests_testID_fkey" FOREIGN KEY ("testID") REFERENCES "Tests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_RunTests" ("id", "runID", "testID") SELECT "id", "runID", "testID" FROM "RunTests";
DROP TABLE "RunTests";
ALTER TABLE "new_RunTests" RENAME TO "RunTests";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
