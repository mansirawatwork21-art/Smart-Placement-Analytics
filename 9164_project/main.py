"""Smart Placement Analytics & Recommendation System — Tkinter desktop GUI."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analytics import calculate_analytics
from data_cleaning import clean_data
from database import save_offers, save_students
from export_data import export_data
from import_data import import_file
from recommendation import recommend_placements

BG = "#F4F7FB"
SIDEBAR = "#172033"
CARD = "#FFFFFF"
TEXT = "#172033"
MUTED = "#667085"
BORDER = "#E3E8F0"
ACCENT = "#4F46E5"
GREEN = "#16A34A"
RED = "#C62828"

CHART_COLORS = ["#4F46E5", "#16A34A", "#F59E0B", "#DB2777", "#0EA5E9", "#7C3AED", "#EA580C"]

OFFERS_COLUMNS = ["offer_id", "company", "job_role", "department", "min_cgpa", "required_skills", "package_lpa"]


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Placement Analytics & Recommendation System")
        self.root.geometry("1180x720")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)

        self.df: pd.DataFrame | None = None
        self.offers = self._load_offers()
        self.current_page = "dashboard"

        self.setup_style()
        self.build_ui()
        self.show_dashboard()

    def _load_offers(self) -> pd.DataFrame:
        try:
            return pd.read_csv("data/company_offers.csv")
        except FileNotFoundError:
            messagebox.showwarning(
                "Missing Data",
                "data/company_offers.csv was not found. Recommendations will be unavailable "
                "until it's placed alongside the app.",
            )
            return pd.DataFrame(columns=OFFERS_COLUMNS)

    # ------------------------------------------------------------------ #
    # Chrome: styling, sidebar, header
    # ------------------------------------------------------------------ #
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 9))
        style.configure("Treeview", background="white", fieldbackground="white", foreground=TEXT,
                        rowheight=30, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#E9EEF7", foreground=TEXT,
                         font=("Segoe UI", 9, "bold"), padding=7)
        style.map("Treeview", background=[("selected", "#DDE4FF")], foreground=[("selected", TEXT)])

    def build_ui(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="SMART PLACEMENT", bg=SIDEBAR, fg="white",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=22, pady=(28, 0))
        tk.Label(self.sidebar, text="Analytics & Recommendation", bg=SIDEBAR, fg="#AAB4C8",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(3, 25))

        items = [
            ("Dashboard", self.show_dashboard), ("Import Data", self.import_data),
            ("Clean Data", self.clean), ("Save to MySQL", self.save_mysql),
            ("Analytics", self.analytics), ("Charts", self.charts),
            ("Suggest Placements", self.recommend), ("Export Data", self.export),
        ]
        for text, command in items:
            b = tk.Button(self.sidebar, text="  " + text, command=command, anchor="w",
                          bg=SIDEBAR, fg="#D9E0EC", activebackground="#263552",
                          activeforeground="white", relief="flat", bd=0,
                          font=("Segoe UI", 10, "bold"), padx=18, pady=11, cursor="hand2")
            b.pack(fill="x", padx=10, pady=2)

        tk.Label(self.sidebar, text="\nProject Workflow\nImport → Clean → Store\n→ Analyze → Recommend → Export",
                 bg=SIDEBAR, fg="#8491A8", justify="left", font=("Segoe UI", 8)
                 ).pack(side="bottom", anchor="w", padx=22, pady=25)

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        header = tk.Frame(self.content, bg=BG)
        header.pack(fill="x", padx=30, pady=(25, 10))
        self.page_title = tk.Label(header, text="Dashboard", bg=BG, fg=TEXT, font=("Segoe UI", 23, "bold"))
        self.page_title.pack(side="left")
        self.status = tk.Label(header, text="Ready", bg="#E8F5E9", fg=GREEN,
                               font=("Segoe UI", 9, "bold"), padx=12, pady=6)
        self.status.pack(side="right")

        self.body = tk.Frame(self.content, bg=BG)
        self.body.pack(fill="both", expand=True, padx=30, pady=10)

    def clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def set_status(self, text, good=True):
        self.status.config(text=text, bg="#E8F5E9" if good else "#FDECEC", fg=GREEN if good else RED)

    def card(self, parent, title, value, subtitle, column):
        frame = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        frame.grid(row=0, column=column, sticky="nsew", padx=6)
        tk.Label(frame, text=title.upper(), bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=18, pady=(15, 3))
        tk.Label(frame, text=value, bg=CARD, fg=TEXT, font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=18)
        tk.Label(frame, text=subtitle, bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=18, pady=(2, 15))

    # ------------------------------------------------------------------ #
    # Dashboard
    # ------------------------------------------------------------------ #
    def show_dashboard(self):
        self.current_page = "dashboard"
        self.page_title.config(text="Dashboard")
        self.clear_body()

        if self.df is not None:
            a = calculate_analytics(self.df)
            total, placed, rate, avg = a["total_students"], a["placed_students"], a["placement_percentage"], a["average_package_lpa"]
        else:
            total = placed = rate = avg = 0

        cards = tk.Frame(self.body, bg=BG)
        cards.pack(fill="x", pady=(0, 18))
        for i in range(4):
            cards.columnconfigure(i, weight=1)
        self.card(cards, "Total Students", str(total), "Records loaded", 0)
        self.card(cards, "Placed Students", str(placed), "Successful placements", 1)
        self.card(cards, "Placement Rate", f"{rate}%", "Overall placement", 2)
        self.card(cards, "Average Package", f"{avg} LPA", "Average offered package", 3)

        main = tk.Frame(self.body, bg=BG)
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="Quick Actions", bg=CARD, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(18, 5))
        tk.Label(left, text="Manage your placement data from one place.", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=(0, 15))

        actions = [
            ("Import Placement Data", self.import_data), ("Clean Dataset", self.clean),
            ("Save to MySQL", self.save_mysql), ("View Analytics", self.analytics),
            ("View Charts", self.charts), ("Suggest Placements", self.recommend),
        ]
        action_frame = tk.Frame(left, bg=CARD)
        action_frame.pack(fill="x", padx=8, pady=(0, 12))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        for i, (t, cmd) in enumerate(actions):
            b = tk.Button(action_frame, text=t, command=cmd, bg="#F6F8FC", fg=TEXT,
                          activebackground="#E9EDFF", relief="flat", bd=0,
                          font=("Segoe UI", 10, "bold"), anchor="w", padx=15, pady=10, cursor="hand2")
            b.grid(row=i // 2, column=i % 2, sticky="ew", padx=4, pady=4)

        right = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER, width=280)
        right.pack(side="right", fill="y", padx=(8, 0))
        right.pack_propagate(False)
        tk.Label(right, text="Project Status", bg=CARD, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(18, 15))
        self.status_line(right, "Dataset", f"Loaded ({total})" if self.df is not None else "Not loaded")
        self.status_line(right, "Cleaning", "Available" if self.df is not None else "Waiting")
        self.status_line(right, "MySQL", "Ready")
        self.status_line(right, "Recommendations", "Ready" if len(self.offers) else "No offers file")
        tk.Label(right, text="\nTip\nImport your CSV/Excel file first,\nthen clean and save it to MySQL.",
                 bg=CARD, fg=MUTED, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=20)

    def status_line(self, parent, name, value):
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x", padx=20, pady=6)
        tk.Label(f, text=name, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(f, text=value, bg=CARD, fg=GREEN, font=("Segoe UI", 9, "bold")).pack(side="right")

    # ------------------------------------------------------------------ #
    # Import / clean / save / export
    # ------------------------------------------------------------------ #
    def import_data(self):
        path = filedialog.askopenfilename(filetypes=[("CSV / Excel files", "*.csv *.xlsx *.xls")])
        if not path:
            return
        try:
            self.df = import_file(path)
            self.show_data_page("Imported Data")
            self.set_status(f"Imported {len(self.df)} records")
        except Exception as e:
            self.set_status("Import failed", good=False)
            messagebox.showerror("Import Error", str(e))

    def clean(self):
        if self.df is None:
            return messagebox.showwarning("No Data", "Import data first.")
        try:
            before = len(self.df)
            self.df = clean_data(self.df)
            self.show_data_page("Cleaned Data")
            removed = before - len(self.df)
            note = f" ({removed} duplicate rows removed)" if removed else ""
            self.set_status(f"Data cleaned successfully{note}")
        except Exception as e:
            self.set_status("Cleaning failed", good=False)
            messagebox.showerror("Cleaning Error", str(e))

    def save_mysql(self):
        if self.df is None:
            return messagebox.showwarning("No Data", "Import and clean your placement data first.")
        w = tk.Toplevel(self.root)
        w.title("Save to MySQL")
        w.geometry("430x250")
        w.configure(bg=BG)
        w.transient(self.root)
        w.grab_set()
        tk.Label(w, text="Connect to MySQL", bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(pady=(25, 5))
        tk.Label(w, text="Enter your MySQL root password", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(pady=5)
        pw = ttk.Entry(w, show="*", width=36)
        pw.pack(pady=8)
        pw.focus()

        def connect():
            try:
                n_students = save_students(self.df, pw.get())
                n_offers = save_offers(self.offers, pw.get())
                w.destroy()
                self.set_status("Saved to MySQL")
                messagebox.showinfo(
                    "Success",
                    f"Saved {n_students} student record(s) and {n_offers} company offer(s) to MySQL.",
                )
            except Exception as e:
                messagebox.showerror("MySQL Error", str(e))

        w.bind("<Return>", lambda _e: connect())
        ttk.Button(w, text="Connect & Save", command=connect).pack(pady=20)

    def export(self):
        if self.df is None:
            return messagebox.showwarning("No Data", "Import data first.")
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")])
        if path:
            try:
                export_data(self.df, path)
                self.set_status("Data exported")
                messagebox.showinfo("Export Complete", "Your data was exported successfully.")
            except Exception as e:
                self.set_status("Export failed", good=False)
                messagebox.showerror("Export Error", str(e))

    # ------------------------------------------------------------------ #
    # Analytics (KPIs + department table)
    # ------------------------------------------------------------------ #
    def analytics(self):
        if self.df is None:
            return messagebox.showwarning("No Data", "Import data first.")
        self.current_page = "analytics"
        a = calculate_analytics(self.df)
        self.page_title.config(text="Placement Analytics")
        self.clear_body()

        box = tk.Frame(self.body, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        box.pack(fill="x", pady=5)
        tk.Label(box, text="Key Performance Indicators", bg=CARD, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20, pady=(18, 12))

        details = [
            ("Total Students", a["total_students"]),
            ("Placed", a["placed_students"]),
            ("Not Placed", a["not_placed_students"]),
            ("Placement Rate", f"{a['placement_percentage']}%"),
            ("Average Package", f"{a['average_package_lpa']} LPA"),
            ("Highest Package", f"{a['highest_package_lpa']} LPA"),
        ]
        kpi_frame = tk.Frame(box, bg=CARD)
        kpi_frame.pack(fill="x", padx=8, pady=(0, 20))
        for i in range(len(details)):
            kpi_frame.columnconfigure(i, weight=1)
        for i, (k, v) in enumerate(details):
            f = tk.Frame(kpi_frame, bg="#F7F9FC")
            f.grid(row=0, column=i, sticky="nsew", padx=5)
            tk.Label(f, text=k, bg="#F7F9FC", fg=MUTED, font=("Segoe UI", 8, "bold")).pack(pady=(10, 2))
            tk.Label(f, text=v, bg="#F7F9FC", fg=TEXT, font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        tk.Label(self.body, text="Department-wise Placements", bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(20, 8))
        t = ttk.Treeview(self.body, show="headings", height=9, columns=("Department", "Placed Students"))
        for c, w in zip(t["columns"], (300, 200)):
            t.heading(c, text=c)
            t.column(c, width=w)
        for dept, count in sorted(a["department_wise"].items(), key=lambda kv: kv[1], reverse=True):
            t.insert("", "end", values=(dept, count))
        t.pack(fill="x")
        self.set_status("Analytics generated")

    # ------------------------------------------------------------------ #
    # Charts — embedded directly in the window (no extra pop-up)
    # ------------------------------------------------------------------ #
    def charts(self):
        if self.df is None:
            return messagebox.showwarning("No Data", "Import data first.")
        self.current_page = "charts"
        self.page_title.config(text="Placement Charts")
        self.clear_body()

        a = calculate_analytics(self.df)
        is_placed = self.df["placement_status"].astype(str).str.lower().eq("placed")
        packages = self.df.loc[is_placed, "package_lpa"]

        fig = Figure(figsize=(10.5, 6.5), dpi=100)
        fig.patch.set_facecolor(CARD)

        # 1. Placement status split.
        ax1 = fig.add_subplot(2, 2, 1)
        status_counts = [a["placed_students"], a["not_placed_students"]]
        if sum(status_counts) > 0:
            ax1.pie(status_counts, labels=["Placed", "Not Placed"], autopct="%1.0f%%",
                    colors=[GREEN, "#D9DEE8"], startangle=90,
                    textprops={"fontsize": 8, "color": TEXT})
        ax1.set_title("Placement Status", fontsize=10, fontweight="bold", color=TEXT)

        # 2. Department-wise placements.
        ax2 = fig.add_subplot(2, 2, 2)
        dept = dict(sorted(a["department_wise"].items(), key=lambda kv: kv[1], reverse=True)[:8])
        if dept:
            ax2.barh(list(dept.keys())[::-1], list(dept.values())[::-1], color=ACCENT)
        ax2.set_title("Placements by Department", fontsize=10, fontweight="bold", color=TEXT)
        ax2.tick_params(axis="both", labelsize=7)

        # 3. Top companies by number of students placed.
        ax3 = fig.add_subplot(2, 2, 3)
        top_companies = dict(sorted(a["company_wise"].items(), key=lambda kv: kv[1], reverse=True)[:8])
        if top_companies:
            ax3.bar(list(top_companies.keys()), list(top_companies.values()),
                    color=CHART_COLORS[: len(top_companies)])
        ax3.set_title("Top Hiring Companies", fontsize=10, fontweight="bold", color=TEXT)
        ax3.tick_params(axis="x", rotation=35, labelsize=7)
        ax3.tick_params(axis="y", labelsize=7)

        # 4. Package distribution among placed students.
        ax4 = fig.add_subplot(2, 2, 4)
        if len(packages) > 0:
            ax4.hist(packages, bins=min(10, max(3, len(packages))), color="#0EA5E9", edgecolor="white")
        ax4.set_title("Package Distribution (LPA)", fontsize=10, fontweight="bold", color=TEXT)
        ax4.tick_params(axis="both", labelsize=7)

        fig.tight_layout(pad=2.0)

        canvas_frame = tk.Frame(self.body, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        canvas_frame.pack(fill="both", expand=True)
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.set_status("Charts generated")

    # ------------------------------------------------------------------ #
    # Recommendations
    # ------------------------------------------------------------------ #
    def recommend(self):
        w = tk.Toplevel(self.root)
        w.title("Smart Placement Recommendations")
        w.geometry("850x600")
        w.configure(bg=BG)
        tk.Label(w, text="Smart Placement Recommendations", bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=25, pady=(22, 3))
        tk.Label(w, text="Enter your profile to find eligible companies and job roles.", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=25, pady=(0, 15))

        form = tk.Frame(w, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        form.pack(fill="x", padx=25)

        departments = sorted(self.offers["department"].dropna().unique()) if len(self.offers) else []
        tk.Label(form, text="Department", bg=CARD, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=12, pady=(15, 5), sticky="w")
        dept_box = ttk.Combobox(form, values=departments, state="readonly", width=22)
        dept_box.grid(row=1, column=0, padx=12, pady=(0, 15))

        tk.Label(form, text="CGPA", bg=CARD, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=1, padx=12, pady=(15, 5), sticky="w")
        cgpa_entry = ttk.Entry(form, width=24)
        cgpa_entry.grid(row=1, column=1, padx=12, pady=(0, 15))

        tk.Label(form, text="Skills (comma separated)", bg=CARD, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=2, padx=12, pady=(15, 5), sticky="w")
        skills_entry = ttk.Entry(form, width=32)
        skills_entry.grid(row=1, column=2, padx=12, pady=(0, 15))

        tree = ttk.Treeview(w, columns=("Company", "Role", "Package", "Matched Skills", "Match"), show="headings", height=12)
        for col, width in zip(tree["columns"], [150, 190, 100, 220, 100]):
            tree.heading(col, text=col)
            tree.column(col, width=width)
        tree.pack(fill="both", expand=True, padx=25, pady=15)

        def go():
            if not dept_box.get():
                return messagebox.showwarning("Missing Department", "Please choose a department.")
            try:
                cgpa = float(cgpa_entry.get())
            except ValueError:
                return messagebox.showerror("Invalid CGPA", "Enter a valid CGPA, e.g. 8.2")
            if not 0 <= cgpa <= 10:
                return messagebox.showerror("Invalid CGPA", "CGPA should be between 0 and 10.")

            results = recommend_placements(dept_box.get(), cgpa, skills_entry.get(), self.offers)
            tree.delete(*tree.get_children())
            for r in results:
                tree.insert("", "end", values=(r["company"], r["job_role"], f"{r['package_lpa']} LPA", r["matched_skills"], r["skill_match"]))
            self.set_status(f"Found {len(results)} recommendation(s)")
            if not results:
                messagebox.showinfo("No Matches", "No offers matched this profile. Try adjusting the CGPA or skills.")

        w.bind("<Return>", lambda _e: go())
        ttk.Button(form, text="Find Suitable Placements", command=go).grid(row=1, column=3, padx=12, pady=(0, 15))

    # ------------------------------------------------------------------ #
    # Data table — searchable and sortable, built for larger datasets
    # ------------------------------------------------------------------ #
    def show_data_page(self, title):
        self.current_page = "data"
        self.page_title.config(text=title)
        self.clear_body()

        top = tk.Frame(self.body, bg=BG)
        top.pack(fill="x", pady=(0, 8))
        self.data_count_label = tk.Label(top, text="", bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.data_count_label.pack(side="left")

        search_box = tk.Frame(top, bg=BG)
        search_box.pack(side="right")
        tk.Label(search_box, text="Search:", bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_box, textvariable=search_var, width=28)
        search_entry.pack(side="left")

        frame = tk.Frame(self.body, bg=CARD)
        frame.pack(fill="both", expand=True)
        y_scroll = ttk.Scrollbar(frame, orient="vertical")
        x_scroll = ttk.Scrollbar(frame, orient="horizontal")
        tree = ttk.Treeview(frame, show="headings", yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        columns = list(self.df.columns)
        tree["columns"] = columns
        sort_state = {"column": None, "reverse": False}

        def render(rows: pd.DataFrame):
            tree.delete(*tree.get_children())
            capped = rows.head(500)
            for _, r in capped.iterrows():
                tree.insert("", "end", values=list(r))
            shown = len(capped)
            total = len(rows)
            suffix = f" (of {len(self.df)} total)" if total != len(self.df) else ""
            label = f"Showing {shown} of {total} matching record(s){suffix}"
            self.data_count_label.config(text=label)

        def sort_by(col):
            nonlocal current
            reverse = sort_state["column"] == col and not sort_state["reverse"]
            sort_state["column"], sort_state["reverse"] = col, reverse
            current = current.sort_values(by=col, ascending=not reverse, kind="stable")
            render(current)

        for c in columns:
            tree.heading(c, text=c, command=lambda c=c: sort_by(c))
            tree.column(c, width=130)

        current = self.df
        # Precompute a single lowercase search blob per row so filtering on every
        # keystroke stays snappy even on a few thousand records.
        str_cols = self.df.astype(str)
        search_index = str_cols[columns[0]]
        for c in columns[1:]:
            search_index = search_index + " " + str_cols[c]
        search_index = search_index.str.lower()

        def apply_search(*_args):
            nonlocal current
            query = search_var.get().strip().lower()
            current = self.df if not query else self.df[search_index.str.contains(query, regex=False)]
            render(current)

        search_var.trace_add("write", apply_search)
        render(self.df)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
