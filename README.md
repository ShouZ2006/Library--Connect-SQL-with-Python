<em>Make sure you pay attention to these things<br></em>
<a4>1.You need to use something that supprot sqlite eg: DB Browser<br>
2. You must keep both of the files near each other to make this work<br>
This is the code of the Database<br></a4>
-- =====================================================
-- LIBRARY DATABASE SETUP FOR SQLITE
-- =====================================================
-- This SQL script creates a complete library database
-- that works with your Python CLI application.
-- 
-- What this script does:
-- 1. Creates three tables (Authors, Books, Borrows)
-- 2. Adds some sample data so you can test immediately
-- 3. Sets up proper relationships between tables
-- =====================================================

-- First, let's create the Authors table
-- This stores information about book authors
CREATE TABLE Authors (
    AuthorID INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each author (auto-generated)
    AuthorName TEXT NOT NULL,                    -- Author's full name (required)
    BirthYear INTEGER                            -- Author's birth year (optional)
);

-- Create the Books table
-- This stores information about all books in the library
CREATE TABLE Books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique ID for each book (auto-generated)
    Title TEXT NOT NULL,                        -- Book title (required)
    PublicationYear INTEGER,                    -- Year the book was published (optional)
    AuthorID INTEGER,                           -- Links to Authors table (optional)
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)  -- Ensures AuthorID exists in Authors table
);

-- Create the Borrows table
-- This tracks who borrowed which books and when
CREATE TABLE Borrows (
    BorrowID INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for each borrow record (auto-generated)
    BookID INTEGER NOT NULL,                    -- Which book was borrowed (required)
    BorrowerName TEXT NOT NULL,                 -- Name of person who borrowed it (required)
    DateBorrowed TEXT NOT NULL,                 -- Date when book was borrowed (required)
    ReturnDate TEXT,                            -- Date when book was returned (NULL = still borrowed)
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE  -- If book is deleted, delete borrow records too
);

-- =====================================================
-- SAMPLE DATA - Remove this section if you don't want sample data
-- =====================================================

-- Add some sample authors
INSERT INTO Authors (AuthorName, BirthYear) VALUES 
    ('J.K. Rowling', 1965),
    ('George Orwell', 1903),
    ('Jane Austen', 1775),
    ('Stephen King', 1947),
    ('Agatha Christie', 1890);

-- Add some sample books
INSERT INTO Books (Title, PublicationYear, AuthorID) VALUES 
    ('Harry Potter and the Philosopher''s Stone', 1997, 1),
    ('Harry Potter and the Chamber of Secrets', 1998, 1),
    ('1984', 1949, 2),
    ('Animal Farm', 1945, 2),
    ('Pride and Prejudice', 1813, 3),
    ('The Shining', 1977, 4),
    ('Murder on the Orient Express', 1934, 5),
    ('And Then There Were None', 1939, 5);

-- Add some sample borrow records
-- Some books are currently borrowed (no ReturnDate)
-- Some books have been returned (with ReturnDate)
INSERT INTO Borrows (BookID, BorrowerName, DateBorrowed, ReturnDate) VALUES 
    (1, 'Alice Johnson', '2024-01-15', '2024-02-01'),  -- Harry Potter book was borrowed and returned
    (3, 'Bob Smith', '2024-02-10', NULL),              -- 1984 is currently borrowed by Bob
    (5, 'Carol Davis', '2024-02-20', '2024-03-05'),    -- Pride and Prejudice was returned
    (7, 'David Wilson', '2024-03-01', NULL),           -- Murder on Orient Express currently borrowed
    (2, 'Eve Brown', '2024-03-10', NULL);              -- Chamber of Secrets currently borrowed

-- =====================================================
-- WHAT HAPPENS AFTER RUNNING THIS SCRIPT:
-- =====================================================
-- 
-- 1. You'll have a working database with 3 tables
-- 2. The database will have 5 authors and 8 books
-- 3. There will be 5 borrow records (3 currently borrowed, 2 returned)
-- 4. Your Python script will immediately work with this data
-- 5. You can test all CRUD operations right away
-- 
-- TO USE THIS:
-- 1. Copy this entire script
-- 2. Open SQLiteStudio (or any SQLite tool)
-- 3. Create a new database called "libraryDB.sqlite"
-- 4. Paste and execute this script
-- 5. Save the database
-- 6. Run your Python script - it should work perfectly!
-- 
-- WHAT YOU'LL SEE IN YOUR PYTHON APP:
-- - 5 authors when you choose "View all authors"
-- - 8 books when you choose "View all books"  
-- - 3 currently borrowed books when you choose "View currently borrowed books"
-- - You can immediately test borrowing, returning, adding, updating, deleting
-- =====================================================
