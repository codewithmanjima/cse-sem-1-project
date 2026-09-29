"""
test_library.py
---------------
Simple tests you can run yourself:   python3 test_library.py
Each test feeds fake keyboard input into the real functions and checks the result.
"""

import unittest
from datetime import timedelta
from unittest.mock import patch

import library
import storage
from utils import today


def fresh_data():
    return storage.empty_data()


def feed(answers):
    """Pretend the user typed these answers, in order."""
    return patch("builtins.input", side_effect=answers)


class TestBooks(unittest.TestCase):
    def test_add_book_rejects_empty_title_and_bad_copies(self):
        data = fresh_data()
        with feed(["", "Python", "Guido", "Tech", "0", "abc", "3"]):
            library.add_book(data)
        self.assertEqual(data["books"][0]["title"], "Python")
        self.assertEqual(data["books"][0]["total_copies"], 3)

    def test_search_is_case_insensitive_partial(self):
        data = fresh_data()
        data["books"] = [{"id": 1, "title": "Clean Code", "author": "Martin",
                          "category": "Tech", "total_copies": 1, "available_copies": 1}]
        with feed(["CLEAN"]):
            library.search_books(data)   # should not crash

    def test_cannot_delete_issued_book(self):
        data = fresh_data()
        data["books"] = [{"id": 1, "title": "A", "author": "B", "category": "C",
                          "total_copies": 2, "available_copies": 1}]
        with feed(["1"]):
            library.delete_book(data)
        self.assertEqual(len(data["books"]), 1)


class TestMembers(unittest.TestCase):
    def test_phone_must_be_10_digits(self):
        data = fresh_data()
        with feed(["Asha", "123", "abcdefghij", "9876543210"]):
            library.add_member(data)
        self.assertEqual(data["members"][0]["phone"], "9876543210")


class TestIssueReturn(unittest.TestCase):
    def setUp(self):
        self.data = fresh_data()
        self.data["books"] = [{"id": 1, "title": "Solo", "author": "X", "category": "Y",
                               "total_copies": 1, "available_copies": 1}]
        self.data["members"] = [{"id": 1, "name": "Asha", "phone": "9876543210"},
                                {"id": 2, "name": "Ravi", "phone": "9123456780"}]

    def test_issue_reduces_available_copies(self):
        with feed(["1", "1"]):
            library.issue_book(self.data)
        self.assertEqual(self.data["books"][0]["available_copies"], 0)
        self.assertEqual(len(library.active_loans(self.data)), 1)

    def test_cannot_issue_when_no_copies_left(self):
        with feed(["1", "1"]):
            library.issue_book(self.data)
        with feed(["1", "2"]):
            library.issue_book(self.data)
        self.assertEqual(len(self.data["transactions"]), 1)

    def test_invalid_ids_do_not_crash(self):
        with feed(["abc"]):
            library.issue_book(self.data)
        with feed(["99"]):
            library.issue_book(self.data)
        self.assertEqual(self.data["transactions"], [])

    def test_on_time_return_has_no_fine(self):
        with feed(["1", "1"]):
            library.issue_book(self.data)
        with feed(["1"]):
            library.return_book(self.data)
        self.assertEqual(self.data["transactions"][0]["fine"], 0)
        self.assertEqual(self.data["books"][0]["available_copies"], 1)

    def test_late_return_charges_fine(self):
        with feed(["1", "1"]):
            library.issue_book(self.data)
        # Pretend the book was issued 20 days ago (6 days overdue).
        t = self.data["transactions"][0]
        t["issue_date"] = (today() - timedelta(days=20)).isoformat()
        t["due_date"] = (today() - timedelta(days=6)).isoformat()
        with feed(["1"]):
            library.return_book(self.data)
        self.assertEqual(t["fine"], 6 * library.FINE_PER_DAY)

    def test_member_limit(self):
        self.data["books"] = [{"id": i, "title": f"B{i}", "author": "A", "category": "C",
                               "total_copies": 1, "available_copies": 1} for i in range(1, 6)]
        for book_id in (1, 2, 3, 4):
            with feed([str(book_id), "1"]):
                library.issue_book(self.data)
        self.assertEqual(len(library.active_loans(self.data)), library.MAX_BOOKS_PER_MEMBER)


class TestStorage(unittest.TestCase):
    def test_corrupted_file_recovers(self):
        import os
        storage.ensure_data_file()
        backup = None
        if os.path.exists(storage.DATA_FILE):
            with open(storage.DATA_FILE) as f:
                backup = f.read()
        try:
            with open(storage.DATA_FILE, "w") as f:
                f.write("{ broken json")
            self.assertEqual(storage.load_data(), storage.empty_data())
        finally:
            with open(storage.DATA_FILE, "w") as f:
                f.write(backup if backup is not None else "")


if __name__ == "__main__":
    unittest.main(verbosity=2)