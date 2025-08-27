import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import date
from collections import defaultdict

FILENAME = "expenses.csv"
HEADERS = ["Date", "Category", "Description", "Amount"]


# ---------- File helpers ----------
def load_expenses():
    """Return list of dicts or [] if file missing."""
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, "r", newline="") as f:
        return list(csv.DictReader(f))


def save_expenses(expenses):
    """Overwrite CSV with given list of dicts."""
    with open(FILENAME, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(expenses)


# ---------- GUI logic ----------
def refresh_table():
    """Clear Treeview and repopulate from CSV, update totals."""
    for iid in tree.get_children():
        tree.delete(iid)
    expenses = load_expenses()
    for i, e in enumerate(expenses, start=1):
        # use string iid for safety
        tree.insert("", "end", iid=str(i), values=(e["Date"], e["Category"], e["Description"], e["Amount"]))
    update_totals(expenses)
    clear_form()


def update_totals(expenses=None):
    """Compute and display total and per-category totals."""
    if expenses is None:
        expenses = load_expenses()
    total = 0.0
    cat_totals = defaultdict(float)
    for r in expenses:
        try:
            amt = float(r.get("Amount", 0) or 0)
            total += amt
            cat_totals[r.get("Category", "Uncategorized")] += amt
        except ValueError:
            continue
    # show total and category breakdown in the summary_label
    lines = [f"Total spent: ${total:.2f}"]
    for cat, amt in cat_totals.items():
        lines.append(f"{cat}: ${amt:.2f}")
    summary_var.set("\n".join(lines))


def validate_amount(value):
    """Return True if value can be parsed as float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def clear_form():
    date_var.set(str(date.today()))
    category_var.set("")
    description_var.set("")
    amount_var.set("")
    tree.selection_remove(tree.selection())


def on_add():
    d = date_var.get().strip() or str(date.today())
    c = category_var.get().strip()
    desc = description_var.get().strip()
    amt = amount_var.get().strip()

    if not (d and c and desc and amt):
        messagebox.showwarning("Missing fields", "Please fill all fields.")
        return
    if not validate_amount(amt):
        messagebox.showerror("Invalid amount", "Amount must be a number.")
        return

    expenses = load_expenses()
    expenses.append({"Date": d, "Category": c, "Description": desc, "Amount": f"{float(amt):.2f}"})
    save_expenses(expenses)
    refresh_table()
    messagebox.showinfo("Saved", "Expense added.")


def on_update():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select an expense to update.")
        return
    idx = int(sel[0]) - 1
    d = date_var.get().strip() or str(date.today())
    c = category_var.get().strip()
    desc = description_var.get().strip()
    amt = amount_var.get().strip()
    if not (d and c and desc and amt):
        messagebox.showwarning("Missing fields", "Please fill all fields.")
        return
    if not validate_amount(amt):
        messagebox.showerror("Invalid amount", "Amount must be a number.")
        return

    expenses = load_expenses()
    if idx < 0 or idx >= len(expenses):
        messagebox.showerror("Error", "Selected item no longer exists.")
        refresh_table()
        return
    expenses[idx] = {"Date": d, "Category": c, "Description": desc, "Amount": f"{float(amt):.2f}"}
    save_expenses(expenses)
    refresh_table()
    messagebox.showinfo("Updated", "Expense updated.")


def on_delete():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Select an expense to delete.")
        return
    idx = int(sel[0]) - 1
    if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected expense?"):
        expenses = load_expenses()
        if idx < 0 or idx >= len(expenses):
            messagebox.showerror("Error", "Selected item no longer exists.")
            refresh_table()
            return
        deleted = expenses.pop(idx)
        save_expenses(expenses)
        refresh_table()
        messagebox.showinfo("Deleted", f"Deleted: {deleted}")


def on_tree_select(event):
    """When user selects a row, populate the form with its values."""
    sel = tree.selection()
    if not sel:
        return
    idx = int(sel[0]) - 1
    expenses = load_expenses()
    if idx < 0 or idx >= len(expenses):
        return
    row = expenses[idx]
    date_var.set(row.get("Date", ""))
    category_var.set(row.get("Category", ""))
    description_var.set(row.get("Description", ""))
    amount_var.set(row.get("Amount", ""))


# ---------- Build the UI ----------
root = tk.Tk()
root.title("Expense Tracker")

# Form frame (top)
form = ttk.Frame(root, padding=(10, 10))
form.pack(fill="x", padx=10, pady=5)

date_var = tk.StringVar(value=str(date.today()))
category_var = tk.StringVar()
description_var = tk.StringVar()
amount_var = tk.StringVar()

ttk.Label(form, text="Date").grid(row=0, column=0, sticky="w")
ttk.Entry(form, textvariable=date_var, width=15).grid(row=0, column=1, padx=5)
ttk.Label(form, text="Category").grid(row=0, column=2, sticky="w")
ttk.Entry(form, textvariable=category_var, width=20).grid(row=0, column=3, padx=5)
ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w")
ttk.Entry(form, textvariable=description_var, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=5)
ttk.Label(form, text="Amount").grid(row=0, column=4, sticky="w")
ttk.Entry(form, textvariable=amount_var, width=12).grid(row=0, column=5, padx=5)

# Buttons frame
btns = ttk.Frame(root, padding=(10, 5))
btns.pack(fill="x", padx=10)
ttk.Button(btns, text="Add", command=on_add).grid(row=0, column=0, padx=5)
ttk.Button(btns, text="Update", command=on_update).grid(row=0, column=1, padx=5)
ttk.Button(btns, text="Delete", command=on_delete).grid(row=0, column=2, padx=5)
ttk.Button(btns, text="Refresh", command=refresh_table).grid(row=0, column=3, padx=5)
ttk.Button(btns, text="Clear", command=clear_form).grid(row=0, column=4, padx=5)

# Table (Treeview)
columns = ("Date", "Category", "Description", "Amount")
tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse", height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150 if col != "Amount" else 80, anchor="w")
tree.pack(fill="both", expand=True, padx=10, pady=5)
tree.bind("<<TreeviewSelect>>", on_tree_select)

# Summary / totals
summary_var = tk.StringVar(value="")
summary_label = ttk.Label(root, textvariable=summary_var, anchor="w", justify="left")
summary_label.pack(fill="x", padx=10, pady=(0, 10))

# Start
refresh_table()
root.mainloop()
