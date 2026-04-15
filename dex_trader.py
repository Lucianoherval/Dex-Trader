import ccxt
import os
from dotenv import load_dotenv

# Carrega as senhas do arquivo .env
load_dotenv()

def conectar_dex():
    wallet_address = os.getenv("WALLET_ADDRESS")
    private_key = os.getenv("PRIVATE_KEY")
    
    # Inicializa a conexão com a Hyperliquid
    dex = ccxt.hyperliquid({
        'walletAddress': wallet_address,
        'privateKey': private_key,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot', # Define que vamos operar o mercado à vista (Spot)
        }
    })
    
    return dex

def buscar_ohlcv(dex, par, intervalo, limite=100):
    velas = dex.fetch_ohlcv(par, intervalo, limit=limite)
    return velas