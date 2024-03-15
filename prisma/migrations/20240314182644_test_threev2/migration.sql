/*
  Warnings:

  - You are about to alter the column `consentFPFInput` on the `TestThree` table. The data in that column could be lost. The data in that column will be cast from `String` to `Float`.
  - You are about to alter the column `formulaAInput` on the `TestThree` table. The data in that column could be lost. The data in that column will be cast from `String` to `Float`.

*/
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
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "TestThree_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_TestThree" ("complianceStatus", "consentFPFInput", "consentFPFStatus", "formulaAInput", "formulaAStatus", "id", "runTestID", "year") SELECT "complianceStatus", "consentFPFInput", "consentFPFStatus", "formulaAInput", "formulaAStatus", "id", "runTestID", "year" FROM "TestThree";
DROP TABLE "TestThree";
ALTER TABLE "new_TestThree" RENAME TO "TestThree";
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
