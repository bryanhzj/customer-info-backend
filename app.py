# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return "Hello, World!"

# @app.route('/api/addCustomer')

# @app.route('/api/customers/all')

# @app.route('/api/customer')

# if __name__ == '__main__':
#     app.run(debug=True)

from fastapi import FastAPI
from fastapi.routing import Request
from pydantic import BaseModel
import sqlalchemy
import databases
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

customers = sqlalchemy.Table(
    "customers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("firstName", sqlalchemy.String),
    sqlalchemy.Column("lastName", sqlalchemy.String),
    sqlalchemy.Column("emailAdd", sqlalchemy.String),
    sqlalchemy.Column("contactNumber", sqlalchemy.String)
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

class CustomerIn(BaseModel):
    firstName: str
    lastName: str
    emailAdd: str
    contactNumber: str

class Customer(BaseModel):
    id: int
    firstName: str
    lastName: str
    emailAdd: str
    contactNumber: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/api/addCustomer", response_model=Customer)
# customer details include first name, last name, email address, contact number (required)
async def addCustomer(customer: CustomerIn):
    query = customers.insert().values(firstName=customer.firstName, lastName=customer.lastName, emailAdd=customer.emailAdd, contactNumber=customer.contactNumber)
    last_record_id = await database.execute(query)
    return {**customer.dict(), "id": last_record_id}

@app.get("/api/customers", response_model=List[Customer])
async def viewCustomers():
    query = customers.select(customers)
    return await database.fetch_all(query)

@app.get("/api/customer/{cust_id}", response_model=List[Customer])
async def viewCustomer(cust_id: int):
    query = customers.select(customers).where(customers.c.id == cust_id)
    return await database.fetch_all(query)

@app.put("/api/customer/edit/{cust_id}")
async def editCustomer(cust_id: int, customer: CustomerIn):
    query = customers.update(customers).where(customers.c.id == cust_id).values(firstName=customer.firstName, lastName=customer.lastName, emailAdd=customer.emailAdd, contactNumber=customer.contactNumber)
    await database.execute(query)
    return {**customer.dict(), "id": cust_id}

@app.delete("/api/customer/delete/{cust_id}")
async def deleteCustomer(cust_id: int):
    query = customers.delete(customers).where(customers.c.id == cust_id)
    # execution return 1 if sucessful
    res = await database.execute(query)
    if res == 1:
        return {"message": "Successfully deleted customer id " + str(cust_id)}
    else:
        return {"message": "customer id " + str(cust_id) + " not found"}

# @app.api_route("/api/customer", methods = ["GET", "POST", "PUT", "DELETE"])
# async def actCustomer(cust_id: int, customer: Optional[CustomerIn] = None):
#     if request.method == "GET":
#         query = customers.select(customers).where(customers.c.id == cust_id)
#         return "success"
#         return await database.fetch_all(query)
#     return {}

# @app.api_route("/api/generic", methods = ["GET", "POST", "DELETE"])
# async def test(request: Request):
#     if request.method == "GET":
#         print("received a get request")
#     if request.method == "POST":
#         print("received a post request")
#     if request.method == "DELETE":
#         print("received a delete request")
#     return {"method": request.method}