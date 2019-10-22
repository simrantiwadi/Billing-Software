BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "p_dimensions" (
	"id"	INTEGER NOT NULL,
	"pid"	INTEGER,
	"length"	INTEGER,
	"width"	INTEGER,
	FOREIGN KEY("pid") REFERENCES "product"("id"),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "product" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(50) NOT NULL,
	"price"	INTEGER NOT NULL,
	"weight"	INTEGER,
	"date_created"	DATETIME,
	PRIMARY KEY("id")
);
INSERT INTO "p_dimensions" VALUES (1,1,10,20);
INSERT INTO "p_dimensions" VALUES (2,2,5,10);
INSERT INTO "product" VALUES (1,'Parle Large',10,20,'');
INSERT INTO "product" VALUES (2,'Parle Small',5,10,'');
COMMIT;
