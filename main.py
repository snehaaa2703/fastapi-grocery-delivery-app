from fastapi import FastAPI,Query,Response,status,HTTPException
from pydantic import BaseModel, Field
import math

app=FastAPI()

# Q2 Day 1 Data
items=[
    {"id":1, "name":"Rice", "price":60, "unit":"kg", "category":"Grain", "in_stock":True},
    {"id":2, "name":"Apple","price":150,"unit":"kg","category":"Fruit","in_stock":True},
    {"id":3,"name":"Milk","price":50,"unit":"litre","category":"Dairy","in_stock":True},
    {"id":4,"name":"Watermelon","price":40,"unit":"kg","category":"Fruit","in_stock":False},
    {"id":5,"name":"Tomato","price":30,"unit":"kg","category":"Vegetable","in_stock":True},
    {"id":6,"name":"Potato","price":25,"unit":"kg","category":"Vegetable","in_stock":False},
    {"id":7,"name":"Eggs","price":70,"unit":"dozen","category":"Dairy","in_stock":True},
    {"id":8,"name":"Oil","price":150,"unit":"litre","category":"Grain","in_stock":True}
]

# Q4
orders=[]
order_counter=1

# Q14
cart=[]

# Q6 - Q9 Day 2: pydantic models
class OrderRequest(BaseModel):
    customer_name:str=Field(...,min_length=2)
    item_id:int=Field(...,gt=0)
    quantity:int=Field(...,gt=0,le=50)
    delivery_address:str=Field(...,min_length=10)
    delivery_slot:str="Morning"
    bulk_order:bool=False 

# Q11
class NewItem(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    unit: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    in_stock: bool = True

# Q15
class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)
    delivery_slot: str = "Morning"

# Helper Functions
# Day 3
# Q7 find item
def find_item(item_id):
    for item in items:
        if item["id"]==item_id:
            return item
    return None

# Q7-Q9
# calculate order total
def calculate_order_total(price, quantity, delivery_slot, bulk_order):
    original_total = price * quantity

    # discount
    if bulk_order and quantity >= 10:
        discounted_total = original_total * 0.92
    else:
        discounted_total = original_total

    # delivery charge
    if delivery_slot == "Morning":
        final_total = discounted_total + 40
    elif delivery_slot == "Evening":
        final_total = discounted_total + 60
    else:
        final_total = discounted_total

    return original_total, round(final_total,2)

# Q10
def filter_items_logic(category=None, max_price=None, unit=None, in_stock=None):
    filtered = []

    for item in items:
        if category is not None and item["category"] != category:
            continue
        if max_price is not None and item["price"] > max_price:
            continue
        if unit is not None and item["unit"] != unit:
            continue
        if in_stock is not None and item["in_stock"] != in_stock:
            continue

        filtered.append(item)

    return filtered

# Q1
@app.get("/")
def home():
    return{"message":"Welcome to FreshMart Grocery"}

@app.get("/items")
def get_items():
    total=len(items)

    in_stock_total=0
    for item in items:
        if item["in_stock"]==True:
            in_stock_total+=1
    
    return{
        "items":items,
        "total":total,
        "in_stock_total":in_stock_total
    }

# Q5
@app.get("/items/summary")
def items_summary():
    total=len(items)
    in_stock=sum(1 for item in items if item["in_stock"])
    out_of_stock=total-in_stock

    category_count={}
    for item in items:
        cat=item["category"]
        if cat in category_count:
            category_count[cat]+=1
        else:
            category_count[cat]=1
    
    return{
        "total_items":total,
        "in_stock":in_stock,
        "out_of_stock":out_of_stock,
        "category_breakdown":category_count
    }

# Q10
@app.get("/items/filter")
def filter_items(
    category: str = Query(None),
    max_price: int = Query(None),
    unit: str = Query(None),
    in_stock: bool = Query(None)
):
    result = filter_items_logic(category, max_price, unit, in_stock)

    return {
        "filtered_items": result,
        "total": len(result)
    }

# Q16
@app.get("/items/search")
def search_items(keyword: str = Query(..., min_length=1)):
    keyword_lower = keyword.lower()
    matched_items = [
        item for item in items
        if keyword_lower in item["name"].lower() or keyword_lower in item["category"].lower()
    ]
    return {
        "matched_items": matched_items,
        "total_found": len(matched_items)
    }

# Q17
@app.get("/items/sort")
def sort_items(
    sort_by: str = Query("name", pattern="^(price|name|category)$"),
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    reverse = True if order == "desc" else False
    sorted_list = sorted(items, key=lambda x: x[sort_by], reverse=reverse)
    return {
        "sorted_by": sort_by,
        "order": order,
        "total_items": len(sorted_list),
        "items": sorted_list
    }

# Q18
@app.get("/items/page")
def paginate_items(
    page: int = Query(1, gt=0),
    limit: int = Query(4, gt=0)
):
    total_items = len(items)
    total_pages = math.ceil(total_items / limit)
    
    start = (page - 1) * limit
    end = start + limit
    page_items = items[start:end]
    
    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": page_items
    }

# 20
@app.get("/items/browse")
def browse_items(
    keyword: str = Query(None),
    category: str = Query(None),
    in_stock: bool = Query(None),
    sort_by: str = Query("name", pattern="^(price|name|category)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1),
    limit: int = Query(4)
):
    # Keyword search
    result = items
    if keyword:
        keyword_lower = keyword.lower()
        result = [
            item for item in result
            if keyword_lower in item["name"].lower() or keyword_lower in item["category"].lower()
        ]
    
    # Category filter
    if category:
        result = [item for item in result if item["category"] == category]
    
    # In-stock filter
    if in_stock is not None:
        result = [item for item in result if item["in_stock"] == in_stock]
    
    # Sort
    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)
    
    # Pagination
    total_items = len(result)
    total_pages = math.ceil(total_items / limit)
    start = (page - 1) * limit
    end = start + limit
    page_items = result[start:end]
    
    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": page_items
    }

# Q11
@app.post("/items",status_code=201)
def add_item(item: NewItem, response: Response):

    # Duplicate check (case-insensitive)
    for existing in items:
        if existing["name"].lower() == item.name.lower():
            return {"error": "Item already exists"}

    # Generate new ID
    new_id = len(items) + 1

    # Create new item
    new_item = {
        "id": new_id,
        "name": item.name,
        "price": item.price,
        "unit": item.unit,
        "category": item.category,
        "in_stock": item.in_stock
    }

    # Add to list
    items.append(new_item)

    # Set status code 201
    response.status_code = status.HTTP_201_CREATED

    return new_item

# Q12
@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    price: int = Query(None),
    in_stock: bool = Query(None)
):
    # find item
    item = find_item(item_id)

    if item is None:
       raise HTTPException(status_code=404, detail={"error":"Item not found"})


    # update only if provided
    if price is not None:
        item["price"] = price

    if in_stock is not None:
        item["in_stock"] = in_stock

    return {
        "message": "Item updated successfully",
        "updated_item": item
    }

# Q13
@app.delete("/items/{item_id}")
def delete_item(item_id: int):

    item = find_item(item_id)

    # 404 if not found
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Business rule: cannot delete if used in orders
    for order in orders:
        if order["item_name"] == item["name"]:
            raise HTTPException(
                status_code=400,
                detail="Item has active orders, cannot delete"
            )

    # delete
    items.remove(item)

    return {
        "message": "Item deleted successfully",
        "deleted_item": item
    }

# Q3
@app.get("/items/{item_id}")
def get_item_by_id(item_id:int):
    for item in items:
        if item["id"]==item_id:
            return item
        
    return {"error":"Item not found"}

# Q4
@app.get("/orders")
def get_orders():
    return{
        "orders":orders,
        "total":len(orders)
    }

# Q8
@app.post("/orders")
def create_order(order:OrderRequest):     #input comes via pydantic 
    global order_counter

    # check item exists
    # reusing helper function
    item=find_item(order.item_id)
    if item is None:
        return {"error":"Item not found"}
    
    # check stock
    # business rule validation
    if not item["in_stock"]:
        return {"error":"Item is out of stock"}
    
    #calculate total
    original,final_total=calculate_order_total(
        item["price"],
        order.quantity,
        order.delivery_slot,
        order.bulk_order
    )

    # create order
    new_order={
        "order_id":order_counter,
        "customer_name":order.customer_name,
        "item_name":item["name"],
        "quantity":order.quantity,
        "unit":item["unit"],
        "delivery_slot":order.delivery_slot,
        "original_amount":original,
        "final_amount":final_total,
        "status":"confirmed"
    }

    # store order
    orders.append(new_order)
    order_counter+=1  #ensures unique order_id

    return new_order

#Q19 Search orders
@app.get("/orders/search")
def search_orders(keyword: str = Query(..., min_length=1)):
    keyword_lower = keyword.lower()
    matched_orders = [
        order for order in orders
        if keyword_lower in order["customer_name"].lower()
        or keyword_lower in order["item_name"].lower()
    ]
    return {
        "matched_orders": matched_orders,
        "total_found": len(matched_orders)
    }

# Q19 Sort orders
@app.get("/orders/sort")
def sort_orders(
    sort_by: str = Query("order_id", pattern="^(order_id|customer_name|item_name|final_amount)$"),
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    reverse = True if order == "desc" else False
    sorted_list = sorted(orders, key=lambda x: x[sort_by], reverse=reverse)
    return {
        "sorted_by": sort_by,
        "order": order,
        "total_orders": len(sorted_list),
        "orders": sorted_list
    }

# Q19 Paginate orders
@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, gt=0),
    limit: int = Query(4, gt=0)
):
    total_orders = len(orders)
    total_pages = math.ceil(total_orders / limit)
    
    start = (page - 1) * limit
    end = start + limit
    page_orders = orders[start:end]
    
    return {
        "page": page,
        "limit": limit,
        "total_orders": total_orders,
        "total_pages": total_pages,
        "orders": page_orders
    }

# Q14
@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int = 1):

    # check item exists
    item = find_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # check stock
    if not item["in_stock"]:
        raise HTTPException(status_code=400, detail="Item is out of stock")

    # check if already in cart
    for cart_item in cart:
        if cart_item["item_id"] == item_id:
            cart_item["quantity"] += quantity
            return {"message": "Cart updated", "cart": cart}

    # add new item
    cart.append({
        "item_id": item_id,
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity
    })

    return {"message": "Item added to cart", "cart": cart}

@app.get("/cart")
def view_cart():

    cart_details = []
    grand_total = 0

    for item in cart:
        subtotal = item["price"] * item["quantity"]
        grand_total += subtotal

        cart_details.append({
            "item_id": item["item_id"],
            "name": item["name"],
            "quantity": item["quantity"],
            "price": item["price"],
            "subtotal": subtotal
        })

    return {
        "cart_items": cart_details,
        "grand_total": grand_total
    }

# Q15
@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int):

    for item in cart:
        if item["item_id"] == item_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")
# Q15
@app.post("/cart/checkout",status_code=201)
def checkout(request: CheckoutRequest):
    global order_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    placed_orders = []
    grand_total = 0

    for cart_item in cart:

        item = find_item(cart_item["item_id"])

        # safety check
        if item is None:
            continue

        # calculate total (reuse helper)
        original, final_total = calculate_order_total(
            item["price"],
            cart_item["quantity"],
            request.delivery_slot,
            False   # bulk_order not used here
        )

        new_order = {
            "order_id": order_counter,
            "customer_name": request.customer_name,
            "item_name": item["name"],
            "quantity": cart_item["quantity"],
            "unit": item["unit"],
            "delivery_slot": request.delivery_slot,
            "original_amount": original,
            "final_amount": final_total,
            "status": "confirmed"
        }

        orders.append(new_order)
        placed_orders.append(new_order)

        grand_total += final_total
        order_counter += 1

    # clear cart after checkout
    cart.clear()

    return {
        "message": "Checkout successful",
        "orders": placed_orders,
        "grand_total": grand_total
    }