from fastapi import FastAPI


from routers import prices, trades


app = FastAPI()
app.include_router(prices.router)
app.include_router(trades.router)
