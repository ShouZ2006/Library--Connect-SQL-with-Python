# Library Database Setup

## Important Setup Requirements

1. **Database Tool Required**: You need to use a tool that supports SQLite (e.g., DB Browser for SQLite, SQLiteStudio)
2. **File Location**: You must keep both the database file and your Python script in the same directory for proper functionality

## Database Overview

This SQL script creates a complete library database that works with your Python CLI application.

### What this script does:
- Creates three tables (Authors, Books, Borrows)
- Adds sample data for immediate testing
- Sets up proper relationships between tables

## Database Schema

### Tables Structure

#### Authors Table
Stores information about book authors
- `AuthorID` - Unique ID for each author (auto-generated)
- `AuthorName` - Author's full name (required)
- `BirthYear` - Author's birth year (optional)

#### Books Table
Stores information about all books in the library
- `BookID` - Unique ID for each book (auto-generated)
- `Title` - Book title (required)
- `PublicationYear` - Year the book was published (optional)
- `AuthorID` - Links to Authors table (optional)

#### Borrows Table
Tracks who borrowed which books and when
- `BorrowID` - Unique ID for each borrow record (auto-generated)
- `BookID` - Which book was borrowed (required)
- `BorrowerName` - Name of person who borrowed the book (required)
- `DateBorrowed` - Date when book was borrowed (required)
- `ReturnDate` - Date when book was returned (NULL = still borrowed)

## Database SQL Script

```sql
-- =====================================================
-- LIBRARY DATABASE SETUP FOR SQLITE
-- =====================================================

-- Create the Authors table
CREATE TABLE Authors (
    AuthorID INTEGER PRIMARY KEY AUTOINCREMENT,
    AuthorName TEXT NOT NULL,
    BirthYear INTEGER
);

-- Create the Books table
CREATE TABLE Books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    PublicationYear INTEGER,
    AuthorID INTEGER,
    FOREIGN KEY (AuthorID) REFERENCES Authors(AuthorID)
);

-- Create the Borrows table
CREATE TABLE Borrows (
    BorrowID INTEGER PRIMARY KEY AUTOINCREMENT,
    BookID INTEGER NOT NULL,
    BorrowerName TEXT NOT NULL,
    DateBorrowed TEXT NOT NULL,
    ReturnDate TEXT,
    FOREIGN KEY (BookID) REFERENCES Books(BookID) ON DELETE CASCADE
);

-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- Add sample authors
INSERT INTO Authors (AuthorName, BirthYear) VALUES 
    ('J.K. Rowling', 1965),
    ('George Orwell', 1903),
    ('Jane Austen', 1775),
    ('Stephen King', 1947),
    ('Agatha Christie', 1890);

-- Add sample books
INSERT INTO Books (Title, PublicationYear, AuthorID) VALUES 
    ('Harry Potter and the Philosopher''s Stone', 1997, 1),
    ('Harry Potter and the Chamber of Secrets', 1998, 1),
    ('1984', 1949, 2),
    ('Animal Farm', 1945, 2),
    ('Pride and Prejudice', 1813, 3),
    ('The Shining', 1977, 4),
    ('Murder on the Orient Express', 1934, 5),
    ('And Then There Were None', 1939, 5);

-- Add sample borrow records
INSERT INTO Borrows (BookID, BorrowerName, DateBorrowed, ReturnDate) VALUES 
    (1, 'Alice Johnson', '2024-01-15', '2024-02-01'),
    (3, 'Bob Smith', '2024-02-10', NULL),
    (5, 'Carol Davis', '2024-02-20', '2024-03-05'),
    (7, 'David Wilson', '2024-03-01', NULL),
    (2, 'Eve Brown', '2024-03-10', NULL);
```

## Setup Instructions

### Step 1: Create the Database
1. Open your SQLite database tool (DB Browser for SQLite, SQLiteStudio, etc.)
2. Create a new database called `libraryDB.sqlite`
3. Copy the entire SQL script above
4. Paste and execute the script in your database tool
5. Save the database

### Step 2: File Organization
- Place the `libraryDB.sqlite` file in the same directory as your Python script
- Ensure both files are in the same folder for proper connectivity

### Step 3: Test the Setup
Run your Python script - it should work immediately with the sample data

## What You'll Get

After running this script, you'll have:

- **5 Authors** in the database
- **8 Books** with proper author relationships
- **5 Borrow Records** (3 currently borrowed, 2 returned)
- A fully functional database ready for your Python CLI application

## Sample Data Overview

### Authors Included:
- J.K. Rowling (1965)
- George Orwell (1903)
- Jane Austen (1775)
- Stephen King (1947)
- Agatha Christie (1890)

### Books Available:
- Harry Potter series (2 books)
- George Orwell classics (1984, Animal Farm)
- Pride and Prejudice
- The Shining
- Agatha Christie mysteries (2 books)

### Current Borrowing Status:
- **Currently Borrowed**: 1984, Murder on the Orient Express, Chamber of Secrets
- **Returned**: Harry Potter (Philosopher's Stone), Pride and Prejudice

## Testing Your Application

Once set up, you can immediately test:
- ✅ View all authors
- ✅ View all books
- ✅ View currently borrowed books
- ✅ Borrow/return functionality
- ✅ Add/update/delete operations

## Troubleshooting

**Common Issues:**
- **"Database not found"**: Ensure `libraryDB.sqlite` is in the same directory as your Python script
- **"No such table"**: Make sure you've executed the complete SQL script
- **Connection errors**: Verify your SQLite tool supports the database version

## Requirements

- SQLite-compatible database tool
- Python environment with SQLite3 support
- Both database and Python files in the same directory
