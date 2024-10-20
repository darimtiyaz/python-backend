from fastapi import FastAPI
from auth.auth import router as auth_router
from auth.ormAuth import router as auth_orm_router
from products.products import router as products_router
from products.ormProducts import router as products_orm_router
from cron.cron import scheduler 
from config import init_orm_db

app = FastAPI()
init_orm_db()

# odm
app.include_router(auth_router, prefix="/api/auth")
app.include_router(products_router, prefix="/api/products")
# orm
app.include_router(auth_orm_router, prefix="/api/auth/orm")
app.include_router(products_orm_router, prefix="/api/products/orm")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
