from fastapi import Depends, FastAPI, status, Response
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
import logging

from Data.dbconnector import get_db,engine
from Models import Products
from Models.Products import Base
from Services import products_service as _prodsvc

app = FastAPI()
Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@app.get("/")
def home():
    return {"Hello":"World"}



@app.get("/products/", response_model=list[Products.Product])
def get_products(db: Session = Depends(get_db)):
    logger.info("getting all products")
    db_products = _prodsvc.get_all_products(db)
    return db_products

@app.get("/products/{product_id}", response_model=Products.Product)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Products.ProductORM)\
    .options(joinedload(Products.ProductORM.reviews))\
    .filter(Products.ProductORM.id == product_id)\
    .first()
    if not product:
        return {"error": "Product not found"}
    return product

@app.post("/products/", response_model=Products.Product)
def create_product(product: Products.Product, db: Session = Depends(get_db)):
    db_product = Products.ProductORM(
        id=product.id,
        name=product.name,
        price=product.price,
        image=product.image,
        description=product.description,
        in_stock=product.in_stock
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.post("/products/{product_id}/reviews",response_model=Products.Review)
def create_review(product_id:str,review: Products.Review, db: Session = Depends(get_db)):
    product = db.query(Products.ProductORM).filter(Products.ProductORM.id == product_id).first()

    if not product:
        return {"error":"Product not found"}

    db_review = Products.ReviewORM(
        product_id=product_id,
        reviewer_name=review.reviewer_name,
        rating=review.rating,
        comment = review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review