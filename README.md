# Crypto price tracker
A simple FastAPI backend to fetch the buying and selling prices of cryptocurrencies from exchanges like Coinbase, Kraken and Gemini.


## API Endpoints

#### Fetch buying and selling price of cryptocurrency.

```http
GET /prices/{$crypto}?{$quantity}&{$price_type}
```

| Parameter | Type     | Description                | Required                  |
| :-------- | :------- | :------------------------- |:------------------------- |
| `crypto` | `string` | capitalized string denoting crypto ticker(Ex: BTC).| Yes
|`quantity` | `string` | quantity of the cryptocurrency.| Yes
|`price_type` | `string` | parameter to fetch individual/ consolidated prices.| Yes


## Requirements

1) [Python3](https://www.python.org/downloads/)(preferably 3.11.3 or newer)

2) [Postman](https://www.postman.com/downloads/)/ your API platform of choice to test the endpoints.




## Usage

1) Clone this repository [crypto-price-track](https://github.com/neerajankam/crypto-price-track) using ssh/ https/ Git CLI. Use the command below if you'd like to clone using ssh.
```
git clone git@github.com:neerajankam/crypto-price-track.git
```
2) Create a virtual environment using `venv` module of python.
```
python3 -m venv <virtual-environment-name>
```
3) Activate the virtual environment and install the requirements present in requirements.txt
```
source <virtual-environment-name>/bin/activate
pip3 install -r requirements.txt
```
4) Add the absolute path of the repository to the PYTHONPATH to ensure python can find the modules.
```
export PYTHONPATH = <absolute-path-of-crypto-price-track-directory>
```
5) Change to the app directory and launch the FastAPI app that is present in the main.py module using [uvicorn](https://www.uvicorn.org/). It is downloaded in Step 3 and you don't need to download it again.
```
cd /app
uvicorn main:app --reload
```
6) Ensure that the server is up and running by going to `http://127.0.0.1:8000/docs`. You should be able to see swagger documentation page if the server is running.

7) You can now headover to Postman/ your choice of API platform to test the endpoints.
## Directory structure

```
├── LICENSE
├── README.md
├── __init__.py
├── app (Application modules)
│   ├── __init__.py
│   ├── exchanges
│   │   ├── __init__.py
│   │   ├── coinbase.py
│   │   ├── exchange_interface.py
│   │   ├── gemini.py
│   │   ├── kraken.py
│   │   └── utils.py
│   ├── main.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── price.py
│   │   └── utils.py
│   ├── supported_cryptos.py
│   └── urls.py
├── logger (Logger modules)
│   └── app_logger.py
├── models (Application models)
│   └── schemas.py
└── requirements.txt
```
## License

[MIT](https://choosealicense.com/licenses/mit/)

