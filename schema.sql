CREATE TABLE stocks
             (date text, trans text, symbol text, qty real, price real);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE "source" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL,
    "url" TEXT NOT NULL
);
CREATE TABLE data (
    "id" INTEGER PRIMARY KEY,
    "title" TEXT,
    "body" TEXT,
    "date" TEXT,
    "source_id" INTEGER,
    FOREIGN KEY (source_id) REFERENCES source(id)
);
