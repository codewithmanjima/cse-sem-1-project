# cse-sem-1-project
#Library Management System

A terminal-based Python program to manage a small library: books, members,
issuing and returning books, overdue tracking, and automatic fine calculation.

## Requirements
- Python 3.8 or newer
- No external packages (standard library only)

## How to Run
From inside this folder:

```
python3 main.py
```

(Use `python main.py` on Windows.) Always run `main.py`; the other files are
supporting modules. The data file `data/library.json` is created automatically.

## Run the Tests
```
python3 test_library.py
```

## Features
| # | Menu option | What it does |
|---|-------------|--------------|
| 1 | Add Book | Adds a title with author, category and number of copies |
| 2 | View All Books | Table of all books with available/total copies |
| 3 | Search Books | Partial, case-insensitive search by title, author or category |
| 4 | Update Book | Edit details; blank input keeps the old value |
| 5 | Delete Book | Blocked while any copy is issued |
| 6 | Add Member | Registers a member (phone must be 10 digits) |
| 7 | View Members | Lists members and how many books each holds |
| 8 | Issue Book | Checks availability, member limit, duplicate copy |
| 9 | Return Book | Restores the copy and calculates any fine |
| 10 | View Issued Books | Books currently out, with due dates |
| 11 | View Overdue Books | Overdue loans with fine accumulated so far |
| 12 | View Statistics | Totals, fines charged, most borrowed book |
| 13 | Exit | Saves and quits |

## Library Rules (constants at the top of `library.py`)
- Loan period: `LOAN_DAYS = 14`
- Fine: `FINE_PER_DAY = 2` (rupees per day late)
- Limit per member: `MAX_BOOKS_PER_MEMBER = 3`

**Fine formula:** `fine = max(0, days_late) x FINE_PER_DAY`, where
`days_late = return date - due date`.

## Project Structure
```
library-management-system/
├── main.py          # menu loop (entry point)
├── library.py       # books, members, issue/return, fines, reports
├── storage.py       # JSON load/save
├── utils.py         # input validation and display helpers
├── test_library.py  # runnable tests
├── data/
│   └── library.json # created automatically
├── README.md
└── requirements.txt
```

## Data Storage
One JSON file holds three lists: `books`, `members`, and `transactions`.
A transaction records the book, member, issue date, due date, return date
(`null` until returned) and fine. Data is saved after every action, and a
corrupted file is replaced with empty data instead of crashing the program.

## Input Validation
Empty names, non-numeric IDs, zero/negative copies, bad phone numbers,
invalid menu choices and non-existent IDs are all rejected with a message
and a re-prompt. The program does not crash on these.

## Limitations
- One librarian, no login system
- Fines are calculated but payment is not tracked
- No book reservations or renewals
- Dates use the computer's current date

## Future Improvements
- Renewals and reservations
- Fine payment tracking
- Login for librarian and members
- Export reports to CSV