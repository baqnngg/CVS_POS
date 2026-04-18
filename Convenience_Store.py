import json

INVENTORY_FILE = "inventory.json"

# 재고 및 매출 데이터 로드 함수
def load_inventory():
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 재고 및 매출 데이터 저장 함수
def save_inventory(data):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 재고 확인 함수
def check_inventory(): return

# 상품 등록 함수
def register_product(): return

# 상품 판매 함수
def sell_product(): return

# 장바구니 처리 함수 (여러 상품 한번에 계산)
def process_cart(): return

# 카테고리별 매출 집계 함수
def get_sales_by_category(products):
    sales_by_category = {}
    for product in products.values():
        category = product.get("category")
        sales = product.get("sold", 0) * product.get("price", 0)
        if category:
            sales_by_category[category] = sales_by_category.get(category, 0) + sales
    return sales_by_category

# 베스트셀러 추출 함수
def get_best_seller(products):
    if not products:
        return None  # 상품이 없을 때 None 반환

    # 딕셔너리 값들 중 판매량 기준 최대 상품 찾기
    best = max(products.values(), key=lambda x: x.get("sold", 0))
    return {"name": best["name"], "sold": best["sold"]}

# 일일 매출 리포트 출력 함수
def print_daily_report(): return

# 상품 재고 
inventory = load_inventory()

# 카테고리별 매출 집계
sales_by_category = {}

# 일일 총 매출
daily_total = 0