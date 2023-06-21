from fastapi import FastAPI


from routers import price


app = FastAPI()
app.include_router(price.router)
