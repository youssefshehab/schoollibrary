CREATE TABLE class_rooms (
        id INTEGER NOT NULL, 
        name VARCHAR, 
        year INTEGER NOT NULL, 
        PRIMARY KEY (id), 
        UNIQUE (name), 
        UNIQUE (username)
);
CREATE TABLE categories (
        id INTEGER NOT NULL, 
        name VARCHAR NOT NULL, 
        description VARCHAR, 
        PRIMARY KEY (id)
);
CREATE TABLE authors (
        id INTEGER NOT NULL, 
        name VARCHAR NOT NULL, 
        biography VARCHAR, 
        PRIMARY KEY (id)
);
CREATE TABLE pupils (
        id INTEGER NOT NULL, 
        name VARCHAR NOT NULL, 
        class_room_id INTEGER, 
        PRIMARY KEY (id), 
        FOREIGN KEY(class_room_id) REFERENCES class_rooms (id)
);
CREATE TABLE books (
        id INTEGER NOT NULL, 
        isbn10 VARCHAR, 
        isbn13 VARCHAR, 
        title VARCHAR, 
        description VARCHAR, 
        thumbnail_url VARCHAR, 
        preview_url VARCHAR, 
        availability VARCHAR, 
        PRIMARY KEY (id), 
        UNIQUE (isbn10), 
        UNIQUE (isbn13)
);
CREATE TABLE users (
    id INTEGER NOT NULL,
    username VARCHAR,
    password VARCHAR,
    is_admin INTEGER
)
CREATE TABLE loans (
    id INTEGER NOT NULL,
    book_id INTEGER, 
    pupil_id INTEGER, 
    start_date DATE,
    due_date DATE,
    FOREIGN KEY(book_id) REFERENCES books (id), 
    FOREIGN KEY(pupil_id) REFERENCES pupils (id)
);
CREATE TABLE book_author_association (
        book_id INTEGER, 
        author_id INTEGER, 
        FOREIGN KEY(book_id) REFERENCES books (id), 
        FOREIGN KEY(author_id) REFERENCES authors (id)
);
CREATE TABLE book_category_association (
        book_id INTEGER, 
        category_id INTEGER, 
        FOREIGN KEY(book_id) REFERENCES books (id), 
        FOREIGN KEY(category_id) REFERENCES categories (id)
);
