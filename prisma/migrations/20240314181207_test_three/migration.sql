-- CreateTable
CREATE TABLE "TestThree" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" TEXT NOT NULL,
    "formulaAInput" TEXT NOT NULL,
    "consentFPFInput" TEXT NOT NULL,
    "complianceStatus" TEXT NOT NULL,
    "formulaAStatus" TEXT NOT NULL,
    "consentFPFStatus" TEXT NOT NULL,
    "runTestID" INTEGER NOT NULL,
    CONSTRAINT "TestThree_runTestID_fkey" FOREIGN KEY ("runTestID") REFERENCES "RunTests" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
