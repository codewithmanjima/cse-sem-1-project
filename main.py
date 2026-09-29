"""
main.py
-------
Entry point of the Library Management System.
Run from the project folder with:   python3 main.py
"""

from utils import print_header, pause, get_menu_choice
from storage import load_data, save_data
import library

MENU = """
===== LIBRARY MANAGEMENT SYSTEM =====

 1. Add Book
 2. View All Books
 3. Search Books
 4. Update Book
 5. Delete Book
 6. Add Member
 7. View Members
 8. Issue Book
 9. Return Book
10. View Issued Books
11. View Overdue Books
12. View Statistics
13. Exit
"""


def main():
    data = load_data()
    choices = [str(n) for n in range(1, 14)]

    while True:
        print(MENU)
        choice = get_menu_choice("Choose an option (1-13): ", choices)

        if choice == "1":
            library.add_book(data)
        elif choice == "2":
            print_header("ALL BOOKS")
            library.view_books(data)
        elif choice == "3":
            print_header("SEARCH BOOKS")
            library.search_books(data)
        elif choice == "4":
            print_header("UPDATE BOOK")
            library.update_book(data)
        elif choice == "5":
            print_header("DELETE BOOK")
            library.delete_book(data)
        elif choice == "6":
            library.add_member(data)
        elif choice == "7":
            print_header("MEMBERS")
            library.view_members(data)
        elif choice == "8":
            print_header("ISSUE BOOK")
            library.issue_book(data)
        elif choice == "9":
            print_header("RETURN BOOK")
            library.return_book(data)
        elif choice == "10":
            print_header("ISSUED BOOKS")
            library.view_issued(data)
        elif choice == "11":
            print_header("OVERDUE BOOKS")
            library.view_overdue(data)
        elif choice == "12":
            print_header("STATISTICS")
            library.view_statistics(data)
        elif choice == "13":
            save_data(data)
            print("\nData saved. Goodbye!")
            break

        # Save after every action so nothing is lost if the program closes unexpectedly.
        save_data(data)
        pause()


if __name__ == "__main__":
    main()