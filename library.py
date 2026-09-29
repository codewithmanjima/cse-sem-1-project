"""
library.py
----------
Core library logic: books, members, issuing/returning, fines, reports.

Rules used by the program (easy to customize, see the constants below):
- A book can be borrowed for LOAN_DAYS days.
- Each day late costs FINE_PER_DAY rupees.
- A member can hold at most MAX_BOOKS_PER_MEMBER books at once.
"""

from datetime import datetime, timedelta

from utils import (
    get_non_empty_string,
    get_positive_int,
    get_yes_no,
    today,
)
from storage import next_id

LOAN_DAYS = 14
FINE_PER_DAY = 2
MAX_BOOKS_PER_MEMBER = 3


# ---------------------------------------------------------------- HELPERS

def find_by_id(records, record_id):
    """Return the record (book/member/transaction) with this id, or None."""
    for record in records:
        if record["id"] == record_id:
            return record
    return None


def parse_date(text):
    """Convert a 'YYYY-MM-DD' string into a date object."""
    return datetime.strptime(text, "%Y-%m-%d").date()


def ask_for_id(records, prompt, label):
    """Ask for an ID and check it exists. Returns the record or None."""
    raw = input(prompt).strip()
    if not raw.isdigit():
        print("Please enter a numeric ID.")
        return None
    record = find_by_id(records, int(raw))
    if record is None:
        print(f"No {label} found with that ID.")
    return record


def active_loans(data):
    """Return transactions where the book has not been returned yet."""
    return [t for t in data["transactions"] if t["return_date"] is None]


def calculate_fine(due_date_text, returned_on):
    """Fine = days late * FINE_PER_DAY. Zero if returned on time."""
    days_late = (returned_on - parse_date(due_date_text)).days
    return max(0, days_late) * FINE_PER_DAY


# ---------------------------------------------------------------- BOOKS

def add_book(data):
    """Add a new book with a number of copies."""
    print("\n--- Add Book ---")
    title = get_non_empty_string("Title: ")
    author = get_non_empty_string("Author: ")
    category = get_non_empty_string("Category: ")
    copies = get_positive_int("Number of copies: ")

    book = {
        "id": next_id(data["books"]),
        "title": title,
        "author": author,
        "category": category,
        "total_copies": copies,
        "available_copies": copies,
    }
    data["books"].append(book)
    print(f"Book added with ID {book['id']}.")


def print_books(books):
    """Print a list of books as a table."""
    if not books:
        print("\nNo books to show.")
        return
    print("\n{:<4}{:<26}{:<18}{:<14}{:<10}".format(
        "ID", "Title", "Author", "Category", "Available"))
    print("-" * 72)
    for b in books:
        print("{:<4}{:<26}{:<18}{:<14}{}/{}".format(
            b["id"], b["title"][:25], b["author"][:17], b["category"][:13],
            b["available_copies"], b["total_copies"]))


def view_books(data):
    print_books(data["books"])


def search_books(data):
    """Search by title, author, or category (case-insensitive, partial match)."""
    keyword = get_non_empty_string("Enter search keyword: ").lower()
    results = [
        b for b in data["books"]
        if keyword in b["title"].lower()
        or keyword in b["author"].lower()
        or keyword in b["category"].lower()
    ]
    print_books(results)


def update_book(data):
    """Edit a book's details. Blank input keeps the old value."""
    print_books(data["books"])
    book = ask_for_id(data["books"], "Enter book ID to update: ", "book")
    if book is None:
        return

    new_title = input(f"Title [{book['title']}]: ").strip()
    if new_title:
        book["title"] = new_title
    new_author = input(f"Author [{book['author']}]: ").strip()
    if new_author:
        book["author"] = new_author
    new_category = input(f"Category [{book['category']}]: ").strip()
    if new_category:
        book["category"] = new_category

    if get_yes_no("Change the total number of copies?"):
        new_total = get_positive_int("New total copies: ")
        on_loan = book["total_copies"] - book["available_copies"]
        if new_total < on_loan:
            print(f"Cannot go below {on_loan}: that many copies are currently issued.")
        else:
            book["total_copies"] = new_total
            book["available_copies"] = new_total - on_loan
    print("Book updated.")


def delete_book(data):
    """Delete a book, but only if no copy is currently issued."""
    print_books(data["books"])
    book = ask_for_id(data["books"], "Enter book ID to delete: ", "book")
    if book is None:
        return

    if book["available_copies"] < book["total_copies"]:
        print("Cannot delete: some copies of this book are currently issued.")
        return
    if get_yes_no(f"Delete '{book['title']}'?"):
        data["books"].remove(book)
        print("Book deleted.")


# ---------------------------------------------------------------- MEMBERS

def add_member(data):
    """Register a new library member."""
    print("\n--- Add Member ---")
    name = get_non_empty_string("Member name: ")
    while True:
        phone = input("Phone number (10 digits): ").strip()
        if phone.isdigit() and len(phone) == 10:
            break
        print("Phone number must be exactly 10 digits.")

    member = {"id": next_id(data["members"]), "name": name, "phone": phone}
    data["members"].append(member)
    print(f"Member added with ID {member['id']}.")


def view_members(data):
    if not data["members"]:
        print("\nNo members registered yet.")
        return
    print("\n{:<4}{:<24}{:<14}{:<8}".format("ID", "Name", "Phone", "Books out"))
    print("-" * 52)
    for m in data["members"]:
        holding = len([t for t in active_loans(data) if t["member_id"] == m["id"]])
        print("{:<4}{:<24}{:<14}{:<8}".format(m["id"], m["name"][:23], m["phone"], holding))


# ---------------------------------------------------------------- ISSUE / RETURN

def issue_book(data):
    """Issue a book to a member after checking every rule."""
    if not data["books"] or not data["members"]:
        print("\nYou need at least one book and one member first.")
        return

    print_books(data["books"])
    book = ask_for_id(data["books"], "Enter book ID to issue: ", "book")
    if book is None:
        return
    if book["available_copies"] == 0:
        print("Sorry, no copies of this book are available right now.")
        return

    view_members(data)
    member = ask_for_id(data["members"], "Enter member ID: ", "member")
    if member is None:
        return

    member_loans = [t for t in active_loans(data) if t["member_id"] == member["id"]]
    if len(member_loans) >= MAX_BOOKS_PER_MEMBER:
        print(f"{member['name']} already has {MAX_BOOKS_PER_MEMBER} books issued (the limit).")
        return
    if any(t["book_id"] == book["id"] for t in member_loans):
        print("This member already has a copy of this book.")
        return

    issue_date = today()
    due_date = issue_date + timedelta(days=LOAN_DAYS)
    transaction = {
        "id": next_id(data["transactions"]),
        "book_id": book["id"],
        "member_id": member["id"],
        "issue_date": issue_date.isoformat(),
        "due_date": due_date.isoformat(),
        "return_date": None,
        "fine": 0,
    }
    data["transactions"].append(transaction)
    book["available_copies"] -= 1
    print(f"Issued '{book['title']}' to {member['name']}. Due on {due_date.isoformat()}.")


def return_book(data):
    """Return a book and calculate any fine."""
    loans = active_loans(data)
    if not loans:
        print("\nNo books are currently issued.")
        return

    view_issued(data)
    transaction = ask_for_id(loans, "Enter transaction ID to return: ", "issued record")
    if transaction is None:
        return

    returned_on = today()
    fine = calculate_fine(transaction["due_date"], returned_on)
    transaction["return_date"] = returned_on.isoformat()
    transaction["fine"] = fine

    book = find_by_id(data["books"], transaction["book_id"])
    if book is not None:
        book["available_copies"] += 1

    print("Book returned successfully.")
    if fine > 0:
        print(f"Late return! Fine to pay: Rs {fine}")
    else:
        print("Returned on time. No fine.")


# ---------------------------------------------------------------- REPORTS

def loan_description(data, transaction):
    """Return (book title, member name) for a transaction, safely."""
    book = find_by_id(data["books"], transaction["book_id"])
    member = find_by_id(data["members"], transaction["member_id"])
    return (book["title"] if book else "(deleted book)",
            member["name"] if member else "(deleted member)")


def view_issued(data):
    """Show all books currently issued."""
    loans = active_loans(data)
    if not loans:
        print("\nNo books are currently issued.")
        return
    print("\n{:<5}{:<24}{:<18}{:<12}{:<12}".format(
        "TxID", "Book", "Member", "Issued", "Due"))
    print("-" * 71)
    for t in loans:
        title, name = loan_description(data, t)
        print("{:<5}{:<24}{:<18}{:<12}{:<12}".format(
            t["id"], title[:23], name[:17], t["issue_date"], t["due_date"]))


def view_overdue(data):
    """Show issued books that are past their due date, with the fine so far."""
    overdue = [t for t in active_loans(data) if parse_date(t["due_date"]) < today()]
    if not overdue:
        print("\nNo overdue books.")
        return
    print("\n{:<5}{:<24}{:<18}{:<12}{:<10}".format(
        "TxID", "Book", "Member", "Due", "Fine so far"))
    print("-" * 69)
    for t in overdue:
        title, name = loan_description(data, t)
        fine = calculate_fine(t["due_date"], today())
        print("{:<5}{:<24}{:<18}{:<12}Rs {}".format(
            t["id"], title[:23], name[:17], t["due_date"], fine))


def view_statistics(data):
    """Summary numbers for the whole library."""
    total_titles = len(data["books"])
    total_copies = sum(b["total_copies"] for b in data["books"])
    available = sum(b["available_copies"] for b in data["books"])
    issued = len(active_loans(data))
    fines_collected = sum(t["fine"] for t in data["transactions"] if t["return_date"])

    # Count how many times each book was borrowed (dictionary counting).
    borrow_counts = {}
    for t in data["transactions"]:
        borrow_counts[t["book_id"]] = borrow_counts.get(t["book_id"], 0) + 1

    print("\n--- Library Statistics ---")
    print(f"Book titles         : {total_titles}")
    print(f"Total copies        : {total_copies}")
    print(f"Copies available    : {available}")
    print(f"Copies issued       : {issued}")
    print(f"Registered members  : {len(data['members'])}")
    print(f"Total fines charged : Rs {fines_collected}")

    if borrow_counts:
        top_id = max(borrow_counts, key=borrow_counts.get)
        top_book = find_by_id(data["books"], top_id)
        if top_book:
            print(f"Most borrowed book  : {top_book['title']} ({borrow_counts[top_id]} times)")