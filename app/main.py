from fastapi import FastAPI


from routers import prices, trades, balances


app = FastAPI()
app.include_router(prices.router)
app.include_router(trades.router)
app.include_router(balances.router)
