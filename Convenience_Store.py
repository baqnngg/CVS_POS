import json
import schedule
import time

INVENTORY_FILE = "inventory.json"

# 영수증 출력 함수
def receipt(cart, inventory, total, out_of_stock):
    width = 32
    print("=" * width)
    print("       편의점 영수증".center(width))
    print("-" * width)
    for name, quantity in cart: # 장바구니 항목 출력
        product = inventory.get(name)
        if product and name not in out_of_stock:
            price = product.get("price", 0)
            print(f"  {name[:12]:<12} x{quantity}  {price * quantity:>7,}원")
    if out_of_stock: # 재고 부족 항목이 있을 때 출력
        print("-" * width)
        print("  [재고 부족 - 미처리 항목]")
        for name in out_of_stock:
            print(f"  {name[:12]:<12}  재고 부족")
    print("-" * width)
    vat = int(total / 11)
    supply = total - vat
    print(f"  {'공급가액':<14} {supply:>10,}원")
    print(f"  {'부가세(10%)':<14} {vat:>9,}원")
    print(f"  {'총 결제금액':<13} {total:>9,}원")
    print("=" * width)
    print("    감사합니다! 또 방문해주세요 :)")
    print("=" * width)

# 재고 및 매출 데이터 로드 함수
def load_inventory():
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 재고 및 매출 데이터 저장 함수
def save_inventory(data):
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 재고 부족 확인 함수
def check_out_of_stock(inventory):
    for product in inventory.values():
        stock = product.get("stock", 0)
        if stock <= 5:
            print(f"상품 {product.get('name')}의 재고가 부족합니다. (현재 재고: {stock})")

# 재고 확인 함수
def check_inventory(inventory):
    print("=== 재고 현황 ===")
    for product in inventory.values():
        print(f"{product.get('name')}({product.get('price'):,}원): {product.get('stock', 0)}개")

# 재고 추가 함수
def add_stock(inventory):
    name = input("재고를 추가할 상품 이름을 입력하세요: ")
    if name in inventory:
        quantity = int(input("추가할 재고 수량을 입력하세요: "))
        inventory[name]["stock"] += quantity
        print(f"상품 {name}의 재고가 {quantity}개 추가되었습니다. (현재 재고: {inventory[name]['stock']}개)")
        save_inventory(inventory)
    else:
        print(f"상품 {name}이(가) 존재하지 않습니다.")

# 상품 등록 함수
def register_product():
    name = input("상품 이름을 입력하세요: ")
    category = input("상품 카테고리를 입력하세요: ")
    price = int(input("상품 가격을 입력하세요: "))
    stock = int(input("상품 재고를 입력하세요: "))
    inventory[name] = {"name": name, "price": price, "stock": stock, "category": category, "sold": 0}
    print(f"상품 {name}이(가) 등록되었습니다.")
    save_inventory(inventory)

# 상품 판매 함수
def sell_product(product, inventory):
    if product not in inventory: # 상품이 존재하지 않을 때 처리
        print(f"상품 {product}이(가) 존재하지 않습니다.")
        return False # 판매 실패를 나타내는 False 반환
    elif inventory[product]["stock"] <= 0: # 재고가 부족할 때 처리
        print(f"상품 {product}의 재고가 부족합니다.")
        return False # 판매 실패를 나타내는 False 반환
    
    inventory[product]["stock"] -= 1
    inventory[product]["sold"] += 1
    print(f"상품 {product}이(가) 1개 판매되었습니다.")
    save_inventory(inventory)
    return True # 판매 성공을 나타내는 True 반환

# 장바구니 처리 함수
def process_cart(cart, inventory):
    total = 0
    out_of_stock = []
    for name, quantity in cart: 
        product = inventory.get(name)
        stock = product.get("stock", 0)

        if product and stock >= quantity: # 재고가 충분할 때 처리
            total += product.get("price", 0) * quantity
            inventory[name]["stock"] -= quantity
            inventory[name]["sold"] = inventory[name].get("sold", 0) + quantity
        else: # 재고가 부족할 때 처리
            print(f"상품 {name}의 재고가 부족합니다.")
            out_of_stock.append(name)
    save_inventory(inventory)
    # 프롬프트 : 총결제 금액좀 영수증 처럼 꾸며줘
    receipt(cart, inventory, total, out_of_stock)

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
def print_daily_report(products):
    daily_total = sum(product.get("sold", 0) * product.get("price", 0) for product in products.values())
    print(f"=== 일일 매출 리포트 ===")
    print(f"일일 총 매출: {daily_total:,}원")

# 상품 재고 
inventory = load_inventory()

# 판매(sold) 초기화 함수
def reset_sold_counts(filename="inventory.json"):
    # 1. 파일 읽기
    with open(filename, "r", encoding="utf-8") as f:
        inventory = json.load(f)
    # 2. sold 값 0으로 리셋
    for product in inventory.values():
        product["sold"] = 0
    # 3. 파일에 다시 저장
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=4)

reset_sold_counts()

# 5분마다 재고 확인
schedule.every(5).minutes.do(check_out_of_stock, inventory)
# 1일마다 판매량 초기화
schedule.every(1).days.do(reset_sold_counts)

while 1:
    schedule.run_pending()
    time.sleep(2)
    print("명령어: 상품등록 / 단일상품구매 / 장바구니 / 재고확인/ 재고 부족 확인 / 재고 추가 / 매출리포트 / 베스트셀러 / 카테고리매출 / sold초기화 / 종료")
    n = input("명령어를 입력하세요: ")
    print()
    if n == "상품등록": register_product()
    elif n == "단일상품구매": # 단일 상품 구매 처리
        product_name = input("구매할 상품 이름을 입력하세요: ")
        
        if product_name not in inventory:
            print(f"상품 {product_name}이(가) 존재하지 않습니다.")
            continue
        success = sell_product(product_name, inventory)
        if success:
            receipt([(product_name, 1)], inventory, inventory[product_name]["price"], [])
        else:
            receipt([(product_name, 1)], inventory, 0, [product_name])
    elif n == "장바구니": # 장바구니 처리
        cart = []
        while True:
            check = input("상품을 확인하고 싶으신가요?(y/n): ")
            if check in ("y", "n"):
                break
            print("y 또는 n만 입력해주세요.")
        if check == "y": # 사용자가 상품 확인을 원할 때 재고 현황 출력
            check_inventory(inventory)
        item_count = int(input("장바구니에 담을 상품의 종류 수를 입력하세요: "))
        for _ in range(item_count): 
            item = input("상품 이름과 수량을 입력하세요(예: 코카콜라 355ml,2): ").strip(" ").split(",")
            cart.append((item[0], int(item[1])))
        process_cart(cart, inventory)
    elif n == "재고확인": check_inventory(inventory) 
    elif n == "재고 부족 확인": check_out_of_stock(inventory)
    elif n == "재고 추가": add_stock(inventory)
    elif n == "매출리포트": print_daily_report(inventory)
    elif n == "베스트셀러": print(get_best_seller(inventory))
    elif n == "카테고리매출": print(get_sales_by_category(inventory))
    elif n == "sold초기화": reset_sold_counts()
    elif n == "종료": break
    else: print("잘못된 명령어입니다. 다시 입력해주세요.")

# 테스트 함수(구매 기능 및 각 기능 테스트)
# def test():
#     process_cart([("코카콜라 355ml", 2), ("오리온 초코파이", 1)], inventory)  # 장바구니 처리 테스트
#     print(get_sales_by_category(inventory))  # 카테고리별 매출 집계 테스트
#     print(get_best_seller(inventory))  # 베스트셀러 추출 테스트
#     print_daily_report(inventory)  # 일일 매출 리포트 출력 테스트

# test()