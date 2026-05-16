from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "change-this-secret"

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def default_photo_url():
    return "https://via.placeholder.com/160x120.png?text=Pet+Image"


def get_categories(conn):
    return conn.execute("SELECT category_id, name FROM categories ORDER BY name").fetchall()


def get_suppliers(conn):
    return conn.execute("SELECT supplier_id, name FROM suppliers ORDER BY name").fetchall()


def get_customers(conn):
    return conn.execute("SELECT customer_id, name FROM customers ORDER BY name").fetchall()


def wrap_items(items, id_field, edit_endpoint, delete_endpoint):
    rows = []
    for item in items:
        rows.append(
            {
                "item": item,
                "edit_url": url_for(edit_endpoint, **{id_field: item[id_field]}),
                "delete_url": url_for(delete_endpoint, **{id_field: item[id_field]}),
            }
        )
    return rows


@app.route("/")
def index():
    conn = get_db_connection()
    pets = conn.execute(
        """
        SELECT pets.*, categories.name AS category_name, suppliers.name AS supplier_name
        FROM pets
        LEFT JOIN categories ON pets.category_id = categories.category_id
        LEFT JOIN suppliers ON pets.supplier_id = suppliers.supplier_id
        ORDER BY pets.created_at DESC
        """
    ).fetchall()
    conn.close()
    return render_template("index.html", pets=pets, default_photo_url=default_photo_url())


@app.route("/menu")
def menu():
    conn = get_db_connection()
    featured = conn.execute("SELECT * FROM pets WHERE name = 'Nemo'").fetchone()
    pets = conn.execute(
        "SELECT name, photo_url FROM pets WHERE photo_url IS NOT NULL AND photo_url != '' ORDER BY RANDOM() LIMIT 4"
    ).fetchall()
    conn.close()
    return render_template(
        "menu.html",
        featured=featured,
        pets=pets,
        default_photo_url=default_photo_url(),
    )


@app.route("/categories")
def categories():
    conn = get_db_connection()
    categories_data = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    conn.close()
    rows = wrap_items(categories_data, "category_id", "edit_category", "delete_category")
    columns = [
        ("category_id", "ID"),
        ("name", "ประเภทสัตว์"),
        ("description", "รายละเอียด"),
        ("created_at", "วันที่สร้าง"),
    ]
    return render_template(
        "list_entities.html",
        title="ประเภทสัตว์เลี้ยง",
        create_url=url_for("create_category"),
        rows=rows,
        columns=columns,
    )


@app.route("/category/create", methods=["GET", "POST"])
def create_category():
    fields = [
        {"name": "name", "label": "ชื่อประเภท", "type": "text", "required": True},
        {"name": "description", "label": "คำอธิบาย", "type": "textarea"},
    ]
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("กรุณากรอกชื่อประเภท", "danger")
            return render_template("entity_form.html", title="เพิ่มประเภทสัตว์เลี้ยง", fields=fields, item=request.form, submit_label="สร้าง")
        conn = get_db_connection()
        conn.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()
        flash("เพิ่มประเภทสัตว์เลี้ยงเรียบร้อยแล้ว", "success")
        return redirect(url_for("categories"))
    return render_template("entity_form.html", title="เพิ่มประเภทสัตว์เลี้ยง", fields=fields, item=None, submit_label="สร้าง")


@app.route("/category/edit/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    conn = get_db_connection()
    category = conn.execute("SELECT * FROM categories WHERE category_id = ?", (category_id,)).fetchone()
    if category is None:
        conn.close()
        flash("ไม่พบข้อมูลประเภทสัตว์เลี้ยง", "warning")
        return redirect(url_for("categories"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("กรุณากรอกชื่อประเภท", "danger")
            return render_template("entity_form.html", title="แก้ไขประเภทสัตว์เลี้ยง", fields=[{"name": "name", "label": "ชื่อประเภท", "type": "text", "required": True}, {"name": "description", "label": "คำอธิบาย", "type": "textarea"}], item=request.form, submit_label="บันทึก")
        conn.execute("UPDATE categories SET name = ?, description = ? WHERE category_id = ?", (name, description, category_id))
        conn.commit()
        conn.close()
        flash("แก้ไขประเภทสัตว์เลี้ยงเรียบร้อยแล้ว", "success")
        return redirect(url_for("categories"))
    conn.close()
    return render_template("entity_form.html", title="แก้ไขประเภทสัตว์เลี้ยง", fields=[{"name": "name", "label": "ชื่อประเภท", "type": "text", "required": True}, {"name": "description", "label": "คำอธิบาย", "type": "textarea"}], item=category, submit_label="บันทึก")


@app.route("/category/delete/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
        conn.commit()
        flash("ลบประเภทสัตว์เลี้ยงเรียบร้อยแล้ว", "success")
    except sqlite3.IntegrityError:
        flash("ไม่สามารถลบได้ เพราะมีสัตว์เลี้ยงที่เชื่อมโยงกับประเภทนี้อยู่", "danger")
    finally:
        conn.close()
    return redirect(url_for("categories"))


@app.route("/suppliers")
def suppliers():
    conn = get_db_connection()
    supplier_data = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    conn.close()
    rows = wrap_items(supplier_data, "supplier_id", "edit_supplier", "delete_supplier")
    columns = [
        ("supplier_id", "ID"),
        ("name", "ชื่อผู้จัดหา"),
        ("email", "อีเมล"),
        ("phone", "โทร"),
        ("city", "จังหวัด"),
    ]
    return render_template("list_entities.html", title="ผู้จัดหา", create_url=url_for("create_supplier"), rows=rows, columns=columns)


@app.route("/supplier/create", methods=["GET", "POST"])
def create_supplier():
    fields = [
        {"name": "name", "label": "ชื่อผู้จัดหา", "type": "text", "required": True},
        {"name": "email", "label": "อีเมล", "type": "email"},
        {"name": "phone", "label": "โทรศัพท์", "type": "text"},
        {"name": "address", "label": "ที่อยู่", "type": "textarea"},
        {"name": "city", "label": "จังหวัด", "type": "text"},
    ]
    if request.method == "POST":
        data = {field["name"]: request.form.get(field["name"], "").strip() for field in fields}
        if not data["name"]:
            flash("กรุณากรอกชื่อผู้จัดหา", "danger")
            return render_template("entity_form.html", title="เพิ่มผู้จัดหา", fields=fields, item=request.form, submit_label="สร้าง")
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO suppliers (name, email, phone, address, city) VALUES (?, ?, ?, ?, ?)",
            (data["name"], data["email"], data["phone"], data["address"], data["city"]),
        )
        conn.commit()
        conn.close()
        flash("เพิ่มผู้จัดหาเรียบร้อยแล้ว", "success")
        return redirect(url_for("suppliers"))
    return render_template("entity_form.html", title="เพิ่มผู้จัดหา", fields=fields, item=None, submit_label="สร้าง")


@app.route("/supplier/edit/<int:supplier_id>", methods=["GET", "POST"])
def edit_supplier(supplier_id):
    conn = get_db_connection()
    supplier = conn.execute("SELECT * FROM suppliers WHERE supplier_id = ?", (supplier_id,)).fetchone()
    if supplier is None:
        conn.close()
        flash("ไม่พบข้อมูลผู้จัดหา", "warning")
        return redirect(url_for("suppliers"))
    fields = [
        {"name": "name", "label": "ชื่อผู้จัดหา", "type": "text", "required": True},
        {"name": "email", "label": "อีเมล", "type": "email"},
        {"name": "phone", "label": "โทรศัพท์", "type": "text"},
        {"name": "address", "label": "ที่อยู่", "type": "textarea"},
        {"name": "city", "label": "จังหวัด", "type": "text"},
    ]
    if request.method == "POST":
        data = {field["name"]: request.form.get(field["name"], "").strip() for field in fields}
        if not data["name"]:
            flash("กรุณากรอกชื่อผู้จัดหา", "danger")
            return render_template("entity_form.html", title="แก้ไขผู้จัดหา", fields=fields, item=request.form, submit_label="บันทึก")
        conn.execute(
            "UPDATE suppliers SET name = ?, email = ?, phone = ?, address = ?, city = ? WHERE supplier_id = ?",
            (data["name"], data["email"], data["phone"], data["address"], data["city"], supplier_id),
        )
        conn.commit()
        conn.close()
        flash("แก้ไขผู้จัดหาเรียบร้อยแล้ว", "success")
        return redirect(url_for("suppliers"))
    conn.close()
    return render_template("entity_form.html", title="แก้ไขผู้จัดหา", fields=fields, item=supplier, submit_label="บันทึก")


@app.route("/supplier/delete/<int:supplier_id>", methods=["POST"])
def delete_supplier(supplier_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM suppliers WHERE supplier_id = ?", (supplier_id,))
        conn.commit()
        flash("ลบผู้จัดหาเรียบร้อยแล้ว", "success")
    except sqlite3.IntegrityError:
        flash("ไม่สามารถลบได้ เพราะมีสัตว์เลี้ยงที่เชื่อมโยงกับผู้จัดหานี้อยู่", "danger")
    finally:
        conn.close()
    return redirect(url_for("suppliers"))


@app.route("/customers")
def customers():
    conn = get_db_connection()
    customer_data = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    conn.close()
    rows = wrap_items(customer_data, "customer_id", "edit_customer", "delete_customer")
    columns = [
        ("customer_id", "ID"),
        ("name", "ชื่อลูกค้า"),
        ("email", "อีเมล"),
        ("phone", "โทร"),
        ("city", "จังหวัด"),
    ]
    return render_template("list_entities.html", title="ลูกค้า", create_url=url_for("create_customer"), rows=rows, columns=columns)


@app.route("/customer/create", methods=["GET", "POST"])
def create_customer():
    fields = [
        {"name": "name", "label": "ชื่อลูกค้า", "type": "text", "required": True},
        {"name": "email", "label": "อีเมล", "type": "email"},
        {"name": "phone", "label": "โทรศัพท์", "type": "text"},
        {"name": "address", "label": "ที่อยู่", "type": "textarea"},
        {"name": "city", "label": "จังหวัด", "type": "text"},
    ]
    if request.method == "POST":
        data = {field["name"]: request.form.get(field["name"], "").strip() for field in fields}
        if not data["name"]:
            flash("กรุณากรอกชื่อลูกค้า", "danger")
            return render_template("entity_form.html", title="เพิ่มลูกค้า", fields=fields, item=request.form, submit_label="สร้าง")
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO customers (name, email, phone, address, city) VALUES (?, ?, ?, ?, ?)",
            (data["name"], data["email"], data["phone"], data["address"], data["city"]),
        )
        conn.commit()
        conn.close()
        flash("เพิ่มลูกค้าเรียบร้อยแล้ว", "success")
        return redirect(url_for("customers"))
    return render_template("entity_form.html", title="เพิ่มลูกค้า", fields=fields, item=None, submit_label="สร้าง")


@app.route("/customer/edit/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
    if customer is None:
        conn.close()
        flash("ไม่พบข้อมูลลูกค้า", "warning")
        return redirect(url_for("customers"))
    fields = [
        {"name": "name", "label": "ชื่อลูกค้า", "type": "text", "required": True},
        {"name": "email", "label": "อีเมล", "type": "email"},
        {"name": "phone", "label": "โทรศัพท์", "type": "text"},
        {"name": "address", "label": "ที่อยู่", "type": "textarea"},
        {"name": "city", "label": "จังหวัด", "type": "text"},
    ]
    if request.method == "POST":
        data = {field["name"]: request.form.get(field["name"], "").strip() for field in fields}
        if not data["name"]:
            flash("กรุณากรอกชื่อลูกค้า", "danger")
            return render_template("entity_form.html", title="แก้ไขลูกค้า", fields=fields, item=request.form, submit_label="บันทึก")
        conn.execute(
            "UPDATE customers SET name = ?, email = ?, phone = ?, address = ?, city = ? WHERE customer_id = ?",
            (data["name"], data["email"], data["phone"], data["address"], data["city"], customer_id),
        )
        conn.commit()
        conn.close()
        flash("แก้ไขลูกค้าเรียบร้อยแล้ว", "success")
        return redirect(url_for("customers"))
    conn.close()
    return render_template("entity_form.html", title="แก้ไขลูกค้า", fields=fields, item=customer, submit_label="บันทึก")


@app.route("/customer/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
        conn.commit()
        flash("ลบลูกค้าเรียบร้อยแล้ว", "success")
    except sqlite3.IntegrityError:
        flash("ไม่สามารถลบได้ เพราะมีบันทึกการขายที่เชื่อมโยงกับลูกค้ารายนี้อยู่", "danger")
    finally:
        conn.close()
    return redirect(url_for("customers"))


@app.route("/sales")
def sales():
    conn = get_db_connection()
    sale_data = conn.execute(
        """
        SELECT sales.*, pets.name AS pet_name, customers.name AS customer_name
        FROM sales
        LEFT JOIN pets ON sales.pet_id = pets.pet_id
        LEFT JOIN customers ON sales.customer_id = customers.customer_id
        ORDER BY sales.sale_date DESC
        """
    ).fetchall()
    conn.close()
    rows = wrap_items(sale_data, "sale_id", "edit_sale", "delete_sale")
    columns = [
        ("sale_id", "ID"),
        ("sale_date", "วันที่"),
        ("pet_name", "สัตว์เลี้ยง"),
        ("customer_name", "ลูกค้า"),
        ("quantity", "จำนวน"),
        ("total_price", "ยอดรวม"),
        ("payment_method", "วิธีชำระเงิน"),
    ]
    return render_template("list_entities.html", title="บันทึกการขาย", create_url=url_for("create_sale"), rows=rows, columns=columns)


@app.route("/sale/create", methods=["GET", "POST"])
def create_sale():
    conn = get_db_connection()
    pets = conn.execute("SELECT pet_id, name FROM pets ORDER BY name").fetchall()
    customers_list = conn.execute("SELECT customer_id, name FROM customers ORDER BY name").fetchall()
    conn.close()
    fields = [
        {"name": "pet_id", "label": "สัตว์เลี้ยง", "type": "select", "options": [{"value": pet["pet_id"], "label": pet["name"]} for pet in pets], "required": True},
        {"name": "customer_id", "label": "ลูกค้า", "type": "select", "options": [{"value": customer["customer_id"], "label": customer["name"]} for customer in customers_list], "required": True},
        {"name": "sale_date", "label": "วันที่ขาย", "type": "date", "required": True},
        {"name": "quantity", "label": "จำนวน", "type": "number", "required": True, "min": 1},
        {"name": "total_price", "label": "ยอดรวม", "type": "number", "step": "0.01", "required": True},
        {"name": "payment_method", "label": "วิธีชำระเงิน", "type": "text"},
        {"name": "notes", "label": "หมายเหตุ", "type": "textarea"},
    ]
    if request.method == "POST":
        data = {field["name"]: request.form.get(field["name"], "").strip() for field in fields}
        if not data["pet_id"] or not data["customer_id"] or not data["sale_date"] or not data["quantity"] or not data["total_price"]:
            flash("กรุณากรอกข้อมูลการขายให้ครบถ้วน", "danger")
            return render_template("entity_form.html", title="เพิ่มบันทึกการขาย", fields=fields, item=request.form, submit_label="สร้าง")
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO sales (pet_id, customer_id, sale_date, quantity, total_price, payment_method, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                int(data["pet_id"]),
                int(data["customer_id"]),
                data["sale_date"],
                int(data["quantity"]),
                float(data["total_price"]),
                data["payment_method"],
                data["notes"],
            ),
        )
        conn.commit()
        conn.close()
        flash("เพิ่มบันทึกการขายเรียบร้อยแล้ว", "success")
        return redirect(url_for("sales"))
    return render_template("entity_form.html", title="เพิ่มบันทึกการขาย", fields=fields, item=None, submit_label="สร้าง")


@app.route("/sale/edit/<int:sale_id>", methods=["GET", "POST"])
def edit_sale(sale_id):
    conn = get_db_connection()
    sale = conn.execute("SELECT * FROM sales WHERE sale_id = ?", (sale_id,)).fetchone()
    pets = conn.execute("SELECT pet_id, name FROM pets ORDER BY name").fetchall()
    customers_list = conn.execute("SELECT customer_id, name FROM customers ORDER BY name").fetchall()
    if sale is None:
        conn.close()
        flash("ไม่พบข้อมูลการขาย", "warning")
        return redirect(url_for("sales"))
    fields = [
        {"name": "pet_id", "label": "สัตว์เลี้ยง", "type": "select", "options": [{"value": pet["pet_id"], "label": pet["name"]} for pet in pets], "required": True},
        {"name": "customer_id", "label": "ลูกค้า", "type": "select", "options": [{"value": customer["customer_id"], "label": customer["name"]} for customer in customers_list], "required": True},
        {"name": "sale_date", "label": "วันที่ขาย", "type": "date", "required": True},
        {"name": "quantity", "label": "จำนวน", "type": "number", "required": True, "min": 1},
        {"name": "total_price", "label": "ยอดรวม", "type": "number", "step": "0.01", "required": True},
        {"name": "payment_method", "label": "วิธีชำระเงิน", "type": "text"},
        {"name": "notes", "label": "หมายเหตุ", "type": "textarea"},
    ]
    if request.method == "POST":
        data = {field["name"]: request.form.get(field["name"], "").strip() for field in fields}
        if not data["pet_id"] or not data["customer_id"] or not data["sale_date"] or not data["quantity"] or not data["total_price"]:
            flash("กรุณากรอกข้อมูลการขายให้ครบถ้วน", "danger")
            return render_template("entity_form.html", title="แก้ไขบันทึกการขาย", fields=fields, item=request.form, submit_label="บันทึก")
        conn.execute(
            "UPDATE sales SET pet_id = ?, customer_id = ?, sale_date = ?, quantity = ?, total_price = ?, payment_method = ?, notes = ? WHERE sale_id = ?",
            (
                int(data["pet_id"]),
                int(data["customer_id"]),
                data["sale_date"],
                int(data["quantity"]),
                float(data["total_price"]),
                data["payment_method"],
                data["notes"],
                sale_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("แก้ไขบันทึกการขายเรียบร้อยแล้ว", "success")
        return redirect(url_for("sales"))
    conn.close()
    return render_template("entity_form.html", title="แก้ไขบันทึกการขาย", fields=fields, item=sale, submit_label="บันทึก")


@app.route("/sale/delete/<int:sale_id>", methods=["POST"])
def delete_sale(sale_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM sales WHERE sale_id = ?", (sale_id,))
    conn.commit()
    conn.close()
    flash("ลบบันทึกการขายเรียบร้อยแล้ว", "success")
    return redirect(url_for("sales"))


@app.route("/pet/create", methods=["GET", "POST"])
def create_pet():
    conn = get_db_connection()
    categories = get_categories(conn)
    suppliers = get_suppliers(conn)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id")
        supplier_id = request.form.get("supplier_id")
        age_months = request.form.get("age_months", "0")
        price = request.form.get("price", "0")
        status = request.form.get("status", "Available")
        color = request.form.get("color", "").strip()
        description = request.form.get("description", "").strip()
        photo_url = request.form.get("photo_url", "").strip()

        if not name or not category_id or not supplier_id or not price or not age_months:
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "danger")
            return render_template(
                "pet_form.html",
                action="Create",
                categories=categories,
                suppliers=suppliers,
                pet=request.form,
            )

        conn.execute(
            "INSERT INTO pets (name, category_id, supplier_id, age_months, price, status, color, description, photo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                name,
                category_id,
                supplier_id,
                int(age_months),
                float(price),
                status,
                color,
                description,
                photo_url,
            ),
        )
        conn.commit()
        conn.close()
        flash("เพิ่มสัตว์เลี้ยงเรียบร้อยแล้ว", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template(
        "pet_form.html",
        action="Create",
        categories=categories,
        suppliers=suppliers,
        pet=None,
    )


@app.route("/pet/edit/<int:pet_id>", methods=["GET", "POST"])
def edit_pet(pet_id):
    conn = get_db_connection()
    pet = conn.execute("SELECT * FROM pets WHERE pet_id = ?", (pet_id,)).fetchone()
    if pet is None:
        conn.close()
        flash("ไม่พบข้อมูลสัตว์เลี้ยง", "warning")
        return redirect(url_for("index"))

    categories = get_categories(conn)
    suppliers = get_suppliers(conn)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id")
        supplier_id = request.form.get("supplier_id")
        age_months = request.form.get("age_months", "0")
        price = request.form.get("price", "0")
        status = request.form.get("status", "Available")
        color = request.form.get("color", "").strip()
        description = request.form.get("description", "").strip()
        photo_url = request.form.get("photo_url", "").strip()

        if not name or not category_id or not supplier_id or not price or not age_months:
            flash("กรุณากรอกข้อมูลให้ครบถ้วน", "danger")
            return render_template(
                "pet_form.html",
                action="Edit",
                categories=categories,
                suppliers=suppliers,
                pet=request.form,
            )

        conn.execute(
            "UPDATE pets SET name = ?, category_id = ?, supplier_id = ?, age_months = ?, price = ?, status = ?, color = ?, description = ?, photo_url = ? WHERE pet_id = ?",
            (
                name,
                category_id,
                supplier_id,
                int(age_months),
                float(price),
                status,
                color,
                description,
                photo_url,
                pet_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("อัปเดตข้อมูลสัตว์เลี้ยงเรียบร้อยแล้ว", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template(
        "pet_form.html",
        action="Edit",
        categories=categories,
        suppliers=suppliers,
        pet=pet,
    )


@app.route("/pet/delete/<int:pet_id>", methods=["POST"])
def delete_pet(pet_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM pets WHERE pet_id = ?", (pet_id,))
    conn.commit()
    conn.close()
    flash("ลบสัตว์เลี้ยงเรียบร้อยแล้ว", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
