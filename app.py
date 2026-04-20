import json
import os
from datetime import datetime
import subprocess
import sys


try:
    from flask import Flask, jsonify, request, send_from_directory
except ImportError:
    print("flask 라이브러리가 없어 설치합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
INVENTORY_FILE = "inventory.json"

DEFAULT_INVENTORY = {
    "유기농 사과": {"name": "유기농 사과", "price": 3000, "stock": 42, "category": "식품", "sold": 0},
    "코카콜라 355ml": {"name": "코카콜라 355ml", "price": 1800, "stock": 100, "category": "음료", "sold": 0},
}

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        save_inventory(DEFAULT_INVENTORY)
        return dict(DEFAULT_INVENTORY)
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_inventory(data):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def build_receipt(cart, inventory, total, out_of_stock):
    items = []
    for name, quantity in cart:
        product = inventory.get(name)
        if product and name not in out_of_stock:
            items.append({"name": name, "quantity": quantity, "price": product["price"], "subtotal": product["price"] * quantity})
    vat = int(total / 11)
    return {"items": items, "out_of_stock": out_of_stock, "supply": total - vat, "vat": vat, "total": total}

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    return jsonify(load_inventory())

@app.route("/api/product", methods=["POST"])
def register_product():
    data = request.json
    inventory = load_inventory()
    name = data["name"]
    inventory[name] = {"name": name, "price": int(data["price"]), "stock": int(data["stock"]), "category": data["category"], "sold": 0}
    save_inventory(inventory)
    return jsonify({"ok": True, "message": f"상품 '{name}'이(가) 등록되었습니다."})

@app.route("/api/stock", methods=["PATCH"])
def add_stock():
    data = request.json
    inventory = load_inventory()
    name = data["name"]
    if name not in inventory:
        return jsonify({"ok": False, "message": f"상품 '{name}'이(가) 존재하지 않습니다."}), 404
    quantity = int(data["quantity"])
    inventory[name]["stock"] += quantity
    save_inventory(inventory)
    return jsonify({"ok": True, "message": f"'{name}' 재고 {quantity}개 추가 (현재: {inventory[name]['stock']}개)"})

@app.route("/api/sell", methods=["POST"])
def sell():
    data = request.json
    inventory = load_inventory()
    cart = [(item["name"], int(item["quantity"])) for item in data["cart"]]
    total = 0
    out_of_stock = []
    for name, quantity in cart:
        product = inventory.get(name)
        if not product:
            out_of_stock.append(name)
            continue
        if product["stock"] < quantity:
            out_of_stock.append(name)
            continue
        total += product["price"] * quantity
        inventory[name]["stock"] -= quantity
        inventory[name]["sold"] = inventory[name].get("sold", 0) + quantity
    save_inventory(inventory)
    receipt = build_receipt(cart, inventory, total, out_of_stock)
    return jsonify({"ok": True, "receipt": receipt})

@app.route("/api/report", methods=["GET"])
def report():
    inventory = load_inventory()
    daily_total = sum(p.get("sold", 0) * p.get("price", 0) for p in inventory.values())
    by_category = {}
    for p in inventory.values():
        cat = p.get("category", "기타")
        by_category[cat] = by_category.get(cat, 0) + p.get("sold", 0) * p.get("price", 0)
    best = max(inventory.values(), key=lambda x: x.get("sold", 0), default=None)
    low_stock = [p for p in inventory.values() if p.get("stock", 0) <= 5]
    return jsonify({
        "daily_total": daily_total,
        "by_category": by_category,
        "best_seller": {"name": best["name"], "sold": best["sold"]} if best else None,
        "low_stock": low_stock,
    })

@app.route("/api/reset-sold", methods=["POST"])
def reset_sold():
    inventory = load_inventory()
    for p in inventory.values():
        p["sold"] = 0
    save_inventory(inventory)
    return jsonify({"ok": True, "message": "판매량이 초기화되었습니다."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
