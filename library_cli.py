# A Simple Command-Line Library Management System
#
# This script connects to an existing SQLite library database and provides
# a command-line interface to interact with it.
# You can add authors, books, and manage borrowing records.
#

# We need the `sqlite3` library to work with SQLite databases.
# This library is built into Python, so you don't need to install anything extra.
import sqlite3
import os
from datetime import date

# This is the name of the database file we will use.
# Make sure this matches your existing database file name.
DATABASE_FILE = "libraryDB.sqlite"

def create_connection():
    """
    Creates a connection to the existing SQLite database.
    Returns the connection object.
    """
    try:
        # Check if the database file exists
        if not os.path.exists(DATABASE_FILE):
            print(f"Error: Database file '{DATABASE_FILE}' not found!")
            print("Please make sure your database file is in the same directory as this script.")
            print(f"Current directory: {os.getcwd()}")
            print(f"Files in current directory: {os.listdir('.')}")
            return None
            
        # Connect to the existing database file
        conn = sqlite3.connect(DATABASE_FILE)
        # Enable foreign key constraints for data integrity
        conn.execute("PRAGMA foreign_keys = ON")
        print(f"Successfully connected to database: {DATABASE_FILE}")
        
        # Test the connection with a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        print(f"Database contains {table_count} tables")
        
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def verify_database_structure(conn):
    """
    Verifies that the required tables exist in the database.
    """
    try:
        cursor = conn.cursor()
        
        # Check if all required tables exist
        required_tables = ['Authors', 'Books', 'Borrows']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"Found tables in database: {existing_tables}")
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"Warning: Missing tables in database: {missing_tables}")
            return False
        else:
            print("Database structure verified successfully.")
            
            # Show current data counts
            for table in required_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            
            return True
            
    except sqlite3.Error as e:
        print(f"Error verifying database structure: {e}")
        return False

# --- Book Operations ---

def add_book(conn):
    """(Create) Adds a new book to the Books table."""
    print("\n--- Add a New Book ---")
    title = input("Enter book title: ").strip()
    
    if not title:
        print("Error: Book title cannot be empty.")
        return False
    
    try:
        pub_year = input("Enter publication year (leave empty if unknown): ").strip()
        if pub_year:
            pub_year = int(pub_year)
            if pub_year < 0 or pub_year > date.today().year + 10:
                print("Error: Please enter a reasonable publication year.")
                return False
        else:
            pub_year = None

        # Show current authors and ask if they want to add a new one
        print("\nCurrent authors in the database:")
        view_authors(conn)
        
        choice = input("\nDo you want to:\n1. Use an existing author\n2. Add a new author\n3. Skip author (set to None)\nEnter choice (1-3): ").strip()
        
        author_id = None
        
        if choice == '1':
            author_id_input = input("Enter the AuthorID for the book's author: ").strip()
            if author_id_input:
                author_id = int(author_id_input)
                # Verify the author exists
                cursor = conn.cursor()
                cursor.execute("SELECT AuthorID FROM Authors WHERE AuthorID = ?", (author_id,))
                if not cursor.fetchone():
                    print("Error: Author ID not found.")
                    return False
        elif choice == '2':
            print("\nAdding new author first:")
            if add_author(conn):
                print("\nNow showing updated author list:")
                view_authors(conn)
                author_id_input = input("Enter the AuthorID for the newly added author: ").strip()
                if author_id_input:
                    author_id = int(author_id_input)
            else:
                print("Failed to add new author. Book will be added without author.")
        elif choice == '3':
            author_id = None
        else:
            print("Invalid choice. Book will be added without author.")
            author_id = None

        sql = "INSERT INTO Books (Title, PublicationYear, AuthorID) VALUES (?, ?, ?)"
        cursor = conn.cursor()
        cursor.execute(sql, (title, pub_year, author_id))
        conn.commit()  # CRITICAL: Make sure we commit the transaction
        
        # Verify the insert worked
        book_id = cursor.lastrowid
        cursor.execute("SELECT Title FROM Books WHERE BookID = ?", (book_id,))
        if cursor.fetchone():
            print(f"Success! Book '{title}' was added with ID: {book_id}")
            print("✓ Changes have been saved to the database.")
        else:
            print("Error: Book insertion failed!")
            return False
        
        return True
        
    except ValueError as e:
        print("Error: Please enter valid numbers for publication year and author ID.")
        return False
    except sqlite3.IntegrityError as e:
        print(f"Error adding book: {e}")
        print("Make sure the Author ID exists in the Authors table.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def view_all_books(conn):
    """(Read) Shows all books in the library with their authors."""
    print("\n--- All Books in the Library ---")
    sql = """
    SELECT b.BookID, b.Title, b.PublicationYear, a.AuthorName
    FROM Books b
    LEFT JOIN Authors a ON b.AuthorID = a.AuthorID
    ORDER BY b.Title
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        all_books = cursor.fetchall()
        if all_books:
            print(f"{'ID':<4} {'Title':<30} {'Year':<6} {'Author':<20}")
            print("-" * 65)
            for book in all_books:
                author_name = book[3] if book[3] else "Unknown Author"
                pub_year = str(book[2]) if book[2] else "Unknown"
                title = book[1][:27] + "..." if len(book[1]) > 30 else book[1]
                print(f"{book[0]:<4} {title:<30} {pub_year:<6} {author_name:<20}")
            print(f"\nTotal books: {len(all_books)}")
        else:
            print("No books found in the library.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def update_book_title(conn):
    """(Update) Updates the title of an existing book."""
    print("\n--- Update a Book's Title ---")
    view_all_books(conn)
    try:
        book_id = int(input("Enter the ID of the book you want to update: "))
        
        # Check if book exists first
        cursor = conn.cursor()
        cursor.execute("SELECT Title FROM Books WHERE BookID = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            print("Error: No book found with that ID.")
            return False
            
        print(f"Current title: '{book[0]}'")
        new_title = input("Enter the new title: ").strip()
        
        if not new_title:
            print("Error: Title cannot be empty.")
            return False

        sql = "UPDATE Books SET Title = ? WHERE BookID = ?"
        cursor.execute(sql, (new_title, book_id))
        conn.commit()  # CRITICAL: Commit the changes

        # Verify the update worked
        cursor.execute("SELECT Title FROM Books WHERE BookID = ?", (book_id,))
        updated_book = cursor.fetchone()
        if updated_book and updated_book[0] == new_title:
            print("✓ Book title updated successfully!")
            print("✓ Changes have been saved to the database.")
        else:
            print("Error: Update verification failed!")
            return False
            
        return True
        
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def delete_book(conn):
    """(Delete) Deletes a book from the Books table."""
    print("\n--- Delete a Book ---")
    view_all_books(conn) 
    try:
        book_id = int(input("Enter the ID of the book you want to delete: "))
        
        # Check if book exists and show details
        cursor = conn.cursor()
        cursor.execute("SELECT Title FROM Books WHERE BookID = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            print("Error: No book found with that ID.")
            return False
            
        confirm = input(f"Are you sure you want to delete '{book[0]}'? This will also delete its borrow records. (yes/no): ").lower().strip()

        if confirm == 'yes':
            sql = "DELETE FROM Books WHERE BookID = ?"
            cursor.execute(sql, (book_id,))
            conn.commit()  # CRITICAL: Commit the changes
            
            # Verify the deletion worked
            cursor.execute("SELECT Title FROM Books WHERE BookID = ?", (book_id,))
            if not cursor.fetchone():
                print("✓ Book deleted successfully!")
                print("✓ Changes have been saved to the database.")
            else:
                print("Error: Deletion verification failed!")
                return False
                
            return True
        else:
            print("Delete canceled.")
            return False
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

# --- Author Operations ---

def add_author(conn):
    """(Create) Adds a new author."""
    print("\n--- Add a New Author ---")
    name = input("Enter author's name: ").strip()
    
    if not name:
        print("Error: Author name cannot be empty.")
        return False
        
    try:
        birth_year = input("Enter author's birth year (leave empty if unknown): ").strip()
        if birth_year:
            birth_year = int(birth_year)
            current_year = date.today().year
            if birth_year < 0 or birth_year > current_year:
                print(f"Error: Please enter a reasonable birth year (0-{current_year}).")
                return False
        else:
            birth_year = None
            
        sql = "INSERT INTO Authors (AuthorName, BirthYear) VALUES (?, ?)"
        cursor = conn.cursor()
        cursor.execute(sql, (name, birth_year))
        conn.commit()  # CRITICAL: Commit the changes
        
        # Verify the insert worked
        author_id = cursor.lastrowid
        cursor.execute("SELECT AuthorName FROM Authors WHERE AuthorID = ?", (author_id,))
        if cursor.fetchone():
            print(f"Success! Author '{name}' was added with ID: {author_id}")
            print("✓ Changes have been saved to the database.")
        else:
            print("Error: Author insertion failed!")
            return False
            
        return True
    except ValueError:
        print("Error: Please enter a valid number for birth year.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def view_authors(conn):
    """(Read) Shows all authors."""
    print("\n--- All Authors ---")
    sql = "SELECT * FROM Authors ORDER BY AuthorName"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        all_authors = cursor.fetchall()
        if all_authors:
            print(f"{'ID':<4} {'Name':<30} {'Birth Year':<10}")
            print("-" * 45)
            for author in all_authors:
                birth_year = str(author[2]) if author[2] else "Unknown"
                name = author[1][:27] + "..." if len(author[1]) > 30 else author[1]
                print(f"{author[0]:<4} {name:<30} {birth_year:<10}")
            print(f"\nTotal authors: {len(all_authors)}")
        else:
            print("No authors found.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def update_author(conn):
    """(Update) Updates an author's information."""
    print("\n--- Update Author Information ---")
    view_authors(conn)
    try:
        author_id = int(input("Enter the ID of the author you want to update: "))
        
        # Check if author exists first
        cursor = conn.cursor()
        cursor.execute("SELECT AuthorName, BirthYear FROM Authors WHERE AuthorID = ?", (author_id,))
        author = cursor.fetchone()
        if not author:
            print("Error: No author found with that ID.")
            return False
            
        print(f"Current name: '{author[0]}'")
        print(f"Current birth year: {author[1] if author[1] else 'Unknown'}")
        
        new_name = input("Enter the new name (press Enter to keep current): ").strip()
        if not new_name:
            new_name = author[0]
            
        new_birth_year_input = input("Enter the new birth year (press Enter to keep current): ").strip()
        if new_birth_year_input:
            new_birth_year = int(new_birth_year_input)
            current_year = date.today().year
            if new_birth_year < 0 or new_birth_year > current_year:
                print(f"Error: Please enter a reasonable birth year (0-{current_year}).")
                return False
        else:
            new_birth_year = author[1]

        sql = "UPDATE Authors SET AuthorName = ?, BirthYear = ? WHERE AuthorID = ?"
        cursor.execute(sql, (new_name, new_birth_year, author_id))
        conn.commit()  # CRITICAL: Commit the changes

        # Verify the update worked
        cursor.execute("SELECT AuthorName, BirthYear FROM Authors WHERE AuthorID = ?", (author_id,))
        updated_author = cursor.fetchone()
        if updated_author and updated_author[0] == new_name:
            print("✓ Author information updated successfully!")
            print("✓ Changes have been saved to the database.")
        else:
            print("Error: Update verification failed!")
            return False

        return True
        
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def delete_author(conn):
    """(Delete) Deletes an author from the Authors table."""
    print("\n--- Delete an Author ---")
    view_authors(conn)
    try:
        author_id = int(input("Enter the ID of the author you want to delete: "))
        
        # Check if author exists and show details
        cursor = conn.cursor()
        cursor.execute("SELECT AuthorName FROM Authors WHERE AuthorID = ?", (author_id,))
        author = cursor.fetchone()
        if not author:
            print("Error: No author found with that ID.")
            return False
            
        # Check how many books this author has
        cursor.execute("SELECT COUNT(*) FROM Books WHERE AuthorID = ?", (author_id,))
        book_count = cursor.fetchone()[0]
        
        warning = f" This will affect {book_count} book(s)." if book_count > 0 else ""
        confirm = input(f"Are you sure you want to delete '{author[0]}'?{warning} (yes/no): ").lower().strip()

        if confirm == 'yes':
            sql = "DELETE FROM Authors WHERE AuthorID = ?"
            cursor.execute(sql, (author_id,))
            conn.commit()  # CRITICAL: Commit the changes
            
            # Verify the deletion worked
            cursor.execute("SELECT AuthorName FROM Authors WHERE AuthorID = ?", (author_id,))
            if not cursor.fetchone():
                print("✓ Author deleted successfully!")
                print("✓ Changes have been saved to the database.")
            else:
                print("Error: Deletion verification failed!")
                return False
                
            return True
        else:
            print("Delete canceled.")
            return False
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

# --- Borrowing Operations ---

def borrow_book(conn):
    """(Create) Records a book being borrowed."""
    print("\n--- Borrow a Book ---")
    view_all_books(conn)
    try:
        book_id = int(input("Enter the ID of the book to borrow: "))
        borrower_name = input("Enter borrower's name: ").strip()
        
        if not borrower_name:
            print("Error: Borrower name cannot be empty.")
            return False
        
        # Check if the book exists and is available
        cursor = conn.cursor()
        cursor.execute("SELECT Title FROM Books WHERE BookID = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            print("Error: That Book ID does not exist.")
            return False
            
        # Check if the book is already borrowed
        cursor.execute("SELECT BorrowerName FROM Borrows WHERE BookID = ? AND ReturnDate IS NULL", (book_id,))
        current_borrower = cursor.fetchone()
        if current_borrower:
            print(f"Sorry, this book is currently borrowed by {current_borrower[0]}.")
            return False

        borrow_date = date.today().isoformat()
        sql = "INSERT INTO Borrows (BookID, BorrowerName, DateBorrowed) VALUES (?, ?, ?)"
        cursor.execute(sql, (book_id, borrower_name, borrow_date))
        conn.commit()  # CRITICAL: Commit the changes
        
        # Verify the borrow record was created
        borrow_id = cursor.lastrowid
        cursor.execute("SELECT BorrowerName FROM Borrows WHERE BorrowID = ?", (borrow_id,))
        if cursor.fetchone():
            print(f"Success! Book '{book[0]}' borrowed by {borrower_name}.")
            print("✓ Borrow record has been saved to the database.")
        else:
            print("Error: Borrow record creation failed!")
            return False

        return True

    except ValueError:
        print("Invalid ID. Please enter a number.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def return_book(conn):
    """(Update) Records a book being returned."""
    print("\n--- Return a Book ---")
    view_borrowed_books(conn, only_outstanding=True)
    try:
        borrow_id = int(input("Enter the Borrow ID of the book you are returning: "))
        
        # Check if the borrow record exists and is outstanding
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.Title, br.BorrowerName 
            FROM Borrows br 
            JOIN Books b ON br.BookID = b.BookID 
            WHERE br.BorrowID = ? AND br.ReturnDate IS NULL
        """, (borrow_id,))
        borrow_info = cursor.fetchone()
        
        if not borrow_info:
            print("Error: No outstanding borrow found with that ID.")
            return False
            
        return_date = date.today().isoformat()
        sql = "UPDATE Borrows SET ReturnDate = ? WHERE BorrowID = ?"
        cursor.execute(sql, (return_date, borrow_id))
        conn.commit()  # CRITICAL: Commit the changes

        # Verify the return was recorded
        cursor.execute("SELECT ReturnDate FROM Borrows WHERE BorrowID = ?", (borrow_id,))
        updated_record = cursor.fetchone()
        if updated_record and updated_record[0]:
            print(f"Success! '{borrow_info[0]}' returned by {borrow_info[1]}.")
            print("✓ Return has been recorded in the database.")
        else:
            print("Error: Return recording failed!")
            return False

        return True
        
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def view_borrowed_books(conn, only_outstanding=False):
    """(Read) Shows borrowed books, either all or just outstanding ones."""
    if only_outstanding:
        print("\n--- Currently Borrowed Books ---")
        sql_filter = "WHERE br.ReturnDate IS NULL"
    else:
        print("\n--- All Borrow History ---")
        sql_filter = ""
        
    sql = f"""
    SELECT br.BorrowID, b.Title, br.BorrowerName, br.DateBorrowed, br.ReturnDate
    FROM Borrows br
    JOIN Books b ON br.BookID = b.BookID
    {sql_filter}
    ORDER BY br.DateBorrowed DESC
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        all_borrows = cursor.fetchall()

        if all_borrows:
            print(f"{'ID':<4} {'Title':<25} {'Borrower':<20} {'Borrowed':<12} {'Returned':<12}")
            print("-" * 75)
            for borrow in all_borrows:
                return_status = borrow[4] if borrow[4] else "Not Returned"
                title = borrow[1][:22] + "..." if len(borrow[1]) > 25 else borrow[1]
                borrower = borrow[2][:17] + "..." if len(borrow[2]) > 20 else borrow[2]
                print(f"{borrow[0]:<4} {title:<25} {borrower:<20} {borrow[3]:<12} {return_status:<12}")
            print(f"\nTotal records: {len(all_borrows)}")
        else:
            if only_outstanding:
                print("No books are currently borrowed.")
            else:
                print("No borrow records found.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# --- Database Testing Function ---

def test_database_connection(conn):
    """Test function to verify database is working properly."""
    print("\n--- Database Connection Test ---")
    try:
        cursor = conn.cursor()
        
        # Test inserting a dummy record
        print("Testing database write capability...")
        cursor.execute("INSERT INTO Authors (AuthorName, BirthYear) VALUES (?, ?)", ("Test Author", 2000))
        test_id = cursor.lastrowid
        
        # Test reading it back
        cursor.execute("SELECT AuthorName FROM Authors WHERE AuthorID = ?", (test_id,))
        result = cursor.fetchone()
        
        if result and result[0] == "Test Author":
            print("✓ Database write/read test successful!")
            
            # Clean up the test record
            cursor.execute("DELETE FROM Authors WHERE AuthorID = ?", (test_id,))
            conn.commit()
            print("✓ Test cleanup completed.")
            return True
        else:
            print("✗ Database test failed!")
            return False
            
    except sqlite3.Error as e:
        print(f"Database test error: {e}")
        return False

# --- The Command Line Interface (CLI) Menu ---

def main_menu():
    """
    This function displays the main menu and handles user input.
    """
    print("=== Library Management System ===")
    print("Connecting to existing database...")
    
    conn = create_connection()
    if not conn:
        print("Failed to connect to database. Exiting...")
        return

    # Verify the database has the required structure
    if not verify_database_structure(conn):
        print("Database structure verification failed. Please check your database.")
        conn.close()
        return
    
    # Test database functionality
    if not test_database_connection(conn):
        print("Database functionality test failed. There may be issues with database permissions.")
        conn.close()
        return

    # Main loop to keep the program running
    while True:
        print("\n===== Library Menu =====")
        print("Books:")
        print("1. View all books")
        print("2. Add a new book")
        print("3. Update a book's title")
        print("4. Delete a book")
        print("---")
        print("Authors:")
        print("5. View all authors")
        print("6. Add a new author")
        print("7. Update author information")
        print("8. Delete an author")
        print("---")
        print("Borrowing:")
        print("9. Borrow a book")
        print("10. Return a book")
        print("11. View currently borrowed books")
        print("12. View all borrow history")
        print("---")
        print("13. Test database connection")
        print("14. Exit")
        print("========================")

        choice = input("Enter your choice (1-14): ").strip()

        try:
            if choice == '1':
                view_all_books(conn)
            elif choice == '2':
                add_book(conn)
            elif choice == '3':
                update_book_title(conn)
            elif choice == '4':
                delete_book(conn)
            elif choice == '5':
                view_authors(conn)
            elif choice == '6':
                add_author(conn)
            elif choice == '7':
                update_author(conn)
            elif choice == '8':
                delete_author(conn)
            elif choice == '9':
                borrow_book(conn)
            elif choice == '10':
                return_book(conn)
            elif choice == '11':
                view_borrowed_books(conn, only_outstanding=True)
            elif choice == '12':
                view_borrowed_books(conn)
            elif choice == '13':
                test_database_connection(conn)
            elif choice == '14':
                print("Thank you for using the Library System. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 14.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Please try again.")

    # Close the database connection when the program ends
    conn.close()
    print("Database connection closed.")

# --- Program Start ---
if __name__ == "__main__":
    main_menu()