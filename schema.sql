CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    name TEXT,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    status TEXT,
    trip_type TEXT,
    date_created TEXT,
    planned_date TEXT,
    rating INTEGER CHECK (rating >=1 AND rating <= 5),
    notes TEXT,
    confirmed_start_date TEXT,
    confirmed_end_date TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE buddies (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    trip_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);

CREATE TABLE experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    trip_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);

CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    trip_id INTEGER NOT NULL,
    filename TEXT,
    caption TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);