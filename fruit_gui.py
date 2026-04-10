import tkinter as tk
from tkinter import ttk, messagebox
import fruit_db as db

class FruitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fruit Management System")

        # Make sure table exists when GUI starts
        db.create_table()

        self.selected_id = None

        # ---- Form ----
        form = ttk.LabelFrame(root, text="Fruit Information")
        form.pack(fill="x", padx=10, pady=8)

        self.name_var = tk.StringVar()
        self.color_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.origin_var = tk.StringVar()
        self.stock_var = tk.StringVar(value="1")

        fields = [
            ("Name", self.name_var),
            ("Color", self.color_var),
            ("Category", self.category_var),
            ("Price per lb", self.price_var),
            ("Origin Country", self.origin_var),
            ("In Stock (1/0)", self.stock_var),
        ]

        for i, (label, var) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", padx=6, pady=3)
            ttk.Entry(form, textvariable=var, width=45).grid(row=i, column=1, sticky="w", padx=6, pady=3)

        # ---- Buttons ----
        btns = ttk.Frame(root)
        btns.pack(fill="x", padx=10, pady=5)

        ttk.Button(btns, text="Insert", command=self.insert).pack(side="left", padx=4)
        ttk.Button(btns, text="Update", command=self.update).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete", command=self.delete).pack(side="left", padx=4)
        ttk.Button(btns, text="Report", command=self.report).pack(side="left", padx=4)
        ttk.Button(btns, text="Refresh", command=self.refresh).pack(side="left", padx=4)

        # ---- Search ----
        searchf = ttk.LabelFrame(root, text="Search")
        searchf.pack(fill="x", padx=10, pady=6)

        self.s_name = tk.StringVar()
        self.s_cat = tk.StringVar()
        self.s_origin = tk.StringVar()

        ttk.Label(searchf, text="Name").grid(row=0, column=0, padx=6, pady=3)
        ttk.Entry(searchf, textvariable=self.s_name, width=18).grid(row=0, column=1, padx=6, pady=3)

        ttk.Label(searchf, text="Category").grid(row=0, column=2, padx=6, pady=3)
        ttk.Entry(searchf, textvariable=self.s_cat, width=18).grid(row=0, column=3, padx=6, pady=3)

        ttk.Label(searchf, text="Origin").grid(row=0, column=4, padx=6, pady=3)
        ttk.Entry(searchf, textvariable=self.s_origin, width=18).grid(row=0, column=5, padx=6, pady=3)

        ttk.Button(searchf, text="Search", command=self.search).grid(row=0, column=6, padx=8, pady=3)

        # ---- Table ----
        cols = ("fruit_id", "name", "color", "category", "price_per_lb", "origin_country", "in_stock")
        self.tree = ttk.Treeview(root, columns=cols, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.refresh()

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.color_var.set("")
        self.category_var.set("")
        self.price_var.set("")
        self.origin_var.set("")
        self.stock_var.set("1")

    def load_rows(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            self.tree.insert("", "end", values=(
                r["fruit_id"], r["name"], r["color"], r["category"],
                r["price_per_lb"], r["origin_country"], r["in_stock"]
            ))

    def refresh(self):
        self.load_rows(db.get_all_fruits())
        self.clear_form()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.selected_id = int(values[0])

        self.name_var.set(values[1])
        self.color_var.set(values[2])
        self.category_var.set(values[3])
        self.price_var.set(values[4])
        self.origin_var.set(values[5])
        self.stock_var.set(str(values[6]))

    def insert(self):
        try:
            price = float(self.price_var.get())
            stock = int(self.stock_var.get())
            if stock not in (0, 1):
                raise ValueError("In Stock must be 0 or 1.")

            db.add_fruit(
                self.name_var.get().strip(),
                self.color_var.get().strip(),
                self.category_var.get().strip(),
                price,
                self.origin_var.get().strip(),
                stock
            )
            self.refresh()
            messagebox.showinfo("Success", "Fruit inserted.")
        except Exception as e:
            messagebox.showerror("Insert Error", str(e))

    def update(self):
        if self.selected_id is None:
            messagebox.showwarning("Select Row", "Click a row first.")
            return
        try:
            price = float(self.price_var.get())
            stock = int(self.stock_var.get())
            if stock not in (0, 1):
                raise ValueError("In Stock must be 0 or 1.")

            changed = db.update_fruit(
                self.selected_id,
                self.name_var.get().strip(),
                self.color_var.get().strip(),
                self.category_var.get().strip(),
                price,
                self.origin_var.get().strip(),
                stock
            )
            self.refresh()
            messagebox.showinfo("Success", f"Updated {changed} row(s).")
        except Exception as e:
            messagebox.showerror("Update Error", str(e))

    def delete(self):
        if self.selected_id is None:
            messagebox.showwarning("Select Row", "Click a row first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this fruit?"):
            return
        deleted = db.delete_fruit(self.selected_id)
        self.refresh()
        messagebox.showinfo("Deleted", f"Deleted {deleted} row(s).")

    def search(self):
        rows = db.search_fruits(
            self.s_name.get().strip(),
            self.s_cat.get().strip(),
            self.s_origin.get().strip()
        )
        self.load_rows(rows)

    def report(self):
        total, instock, avg = db.report_stats()
        messagebox.showinfo("Report", f"Total fruits: {total}\nIn stock: {instock}\nAverage price/lb: ${avg}")


if __name__ == "__main__":
    root = tk.Tk()
    FruitGUI(root)
    root.mainloop()
