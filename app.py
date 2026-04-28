from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).parent / "cakeshop.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    sql_file = Path(__file__).parent / "create_tables.sql"
    db = get_db()
    db.executescript(sql_file.read_text(encoding="utf-8"))
    db.commit()
    db.close()


@app.before_first_request
def setup():
    init_db()
    db = get_db()
    categories = db.execute("SELECT id FROM categories LIMIT 1").fetchone()
    if categories is None:
        db.executemany(
            "INSERT INTO categories (name) VALUES (?)",
            [("ช็อกโกแลต",), ("วานิลลา",), ("สตรอว์เบอร์รี่",)],
        )
        db.commit()
    db.close()


@app.route("/")
def cake_menu():
    db = get_db()
    cakes = db.execute(
        "SELECT cakes.*, categories.name AS category_name FROM cakes "
        "JOIN categories ON cakes.category_id = categories.id "
        "ORDER BY cakes.id"
    ).fetchall()
    db.close()
    return render_template("cakemenu.html", cakes=cakes)


@app.route("/add", methods=["GET", "POST"])
def add_cake():
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()

    if request.method == "POST":
        name = request.form["name"].strip()
        price = float(request.form["price"] or 0)
        stock = int(request.form["stock"] or 0)
        image = request.form["image"].strip()
        category_id = int(request.form["category_id"])

        db.execute(
            "INSERT INTO cakes (name, price, stock, image, category_id) VALUES (?, ?, ?, ?, ?)",
            (name, price, stock, image, category_id),
        )
        db.commit()
        db.close()
        return redirect(url_for("cake_menu"))

    db.close()
    return render_template("append.html", categories=categories)


@app.route("/edit/<int:cake_id>", methods=["GET", "POST"])
def edit_cake(cake_id):
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    cake = db.execute("SELECT * FROM cakes WHERE id = ?", (cake_id,)).fetchone()

    if cake is None:
        db.close()
        return redirect(url_for("cake_menu"))

    if request.method == "POST":
        name = request.form["name"].strip()
        price = float(request.form["price"] or 0)
        stock = int(request.form["stock"] or 0)
        image = request.form["image"].strip()
        category_id = int(request.form["category_id"])

        db.execute(
            "UPDATE cakes SET name = ?, price = ?, stock = ?, image = ?, category_id = ? WHERE id = ?",
            (name, price, stock, image, category_id, cake_id),
        )
        db.commit()
        db.close()
        return redirect(url_for("cake_menu"))

    db.close()
    return render_template("edit.html", cake=cake, categories=categories)


@app.route("/delete/<int:cake_id>", methods=["POST"])
def delete_cake(cake_id):
    db = get_db()
    db.execute("DELETE FROM cakes WHERE id = ?", (cake_id,))
    db.commit()
    db.close()
    return redirect(url_for("cake_menu"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
