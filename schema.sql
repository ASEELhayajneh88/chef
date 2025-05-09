DROP TABLE IF EXISTS recipes;

/*CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    ingredients TEXT NOT NULL, 
    steps TEXT NOT NULL
);*/
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    steps TEXT NOT NULL,
    confidence REAL DEFAULT 1.0
);

