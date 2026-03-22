# FreshMart Grocery Delivery App

## Project Overview
This project is a **FreshMart Grocery Delivery App** built using **FastAPI**.  
It provides a complete backend for a grocery store, allowing management of items, orders, and a shopping cart with search, sorting, and pagination capabilities.

---

## Key Features
- RESTful APIs with FastAPI  
- Pydantic data validation for request payloads  
- CRUD operations for grocery items  
- Shopping cart management with add, view, remove, and checkout  
- Order placement with delivery slots, bulk order discounts, and total calculation  
- Search, sorting, and pagination for items and orders  
- API documentation and testing via **Swagger UI**

---

## How to Run the Project

1. **Clone the repository:**
 git clone https://github.com/snehaaa2703/grocery-delivery-app.git
 cd grocery-delivery-app

2.**Install dependencies:**

  pip install -r requirements.txt

3.**Run the FastAPI server:**

uvicorn main:app --reload

4.**Open API documentation in your browser:**

http://127.0.0.1:8000/docs
