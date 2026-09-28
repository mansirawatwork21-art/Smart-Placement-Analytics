"""MySQL persistence layer for students and company offers.

The MySQL password is only ever taken from the GUI's password prompt at
save-time and passed straight through to mysql-connector; it is never
written to disk or kept in this module.
"""

from contextlib import contextmanager

import mysql.connector

DB_NAME = "placement_db"
DB_CONFIG = {"host": "localhost", "user": "root"}

STUDENTS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS students (
        student_id VARCHAR(20) PRIMARY KEY,
        student_name VARCHAR(100),
        department VARCHAR(100),
        cgpa DECIMAL(4,2),
        skills VARCHAR(500),
        placement_status VARCHAR(30),
        company VARCHAR(100),
        package_lpa DECIMAL(6,2)
    )
"""

OFFERS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS company_offers (
        offer_id INT PRIMARY KEY,
        company VARCHAR(100),
        job_role VARCHAR(100),
        department VARCHAR(100),
        min_cgpa DECIMAL(4,2),
        required_skills VARCHAR(500),
        package_lpa DECIMAL(6,2)
    )
"""


def get_connection(password: str | None = None, use_database: bool = True):
    config = dict(DB_CONFIG)
    if password is not None:
        config["password"] = password
    if use_database:
        config["database"] = DB_NAME
    return mysql.connector.connect(**config)


@contextmanager
def _cursor(password=None, use_database=True):
    conn = get_connection(password, use_database)
    try:
        cur = conn.cursor()
        yield conn, cur
        conn.commit()
    finally:
        conn.close()


def setup_database(password: str | None = None) -> None:
    """Create the database and tables if they don't already exist."""
    with _cursor(password, use_database=False) as (_, cur):
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    with _cursor(password) as (_, cur):
        cur.execute(STUDENTS_TABLE_SQL)
        cur.execute(OFFERS_TABLE_SQL)


def _clean_value(v):
    return None if str(v).strip().lower() in ("nan", "none", "") else v


def save_students(df, password: str | None = None, chunk_size: int = 500) -> int:
    """Upsert student records. Returns the number of rows written."""
    setup_database(password)
    sql = """
        INSERT INTO students
            (student_id, student_name, department, cgpa, skills, placement_status, company, package_lpa)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            student_name = VALUES(student_name), department = VALUES(department),
            cgpa = VALUES(cgpa), skills = VALUES(skills),
            placement_status = VALUES(placement_status),
            company = VALUES(company), package_lpa = VALUES(package_lpa)
    """
    columns = ["student_id", "student_name", "department", "cgpa",
               "skills", "placement_status", "company", "package_lpa"]
    rows = [tuple(_clean_value(r.get(c)) for c in columns) for _, r in df.iterrows()]

    with _cursor(password) as (_, cur):
        for i in range(0, len(rows), chunk_size):
            cur.executemany(sql, rows[i:i + chunk_size])
    return len(rows)


def save_offers(df, password: str | None = None) -> int:
    """Upsert company offer records. Returns the number of rows written."""
    setup_database(password)
    sql = """
        INSERT INTO company_offers
            (offer_id, company, job_role, department, min_cgpa, required_skills, package_lpa)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            company = VALUES(company), job_role = VALUES(job_role),
            department = VALUES(department), min_cgpa = VALUES(min_cgpa),
            required_skills = VALUES(required_skills), package_lpa = VALUES(package_lpa)
    """
    columns = ["offer_id", "company", "job_role", "department",
               "min_cgpa", "required_skills", "package_lpa"]
    rows = [tuple(r.get(c) for c in columns) for _, r in df.iterrows()]

    with _cursor(password) as (_, cur):
        cur.executemany(sql, rows)
    return len(rows)


def fetch_offers(password: str | None = None) -> list[dict]:
    setup_database(password)
    conn = get_connection(password)
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM company_offers")
        return cur.fetchall()
    finally:
        conn.close()
