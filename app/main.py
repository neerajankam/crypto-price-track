from fastapi import FastAPI


from routers import prices, trades, accounts


app = FastAPI()
app.include_router(prices.router)
app.include_router(trades.router)
app.include_router(accounts.router)
