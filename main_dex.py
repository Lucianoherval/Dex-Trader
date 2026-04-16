import time
import pandas as pd
import math
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from dex_trader import conectar_dex, buscar_ohlcv
from indicadores import calcular_macd
from registro import inicializar_csv, registrar_operacao

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==========================================
# 📱 ALERTA TELEGRAM
# ==========================================
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"⚠️ Erro no Telegram: {e}")

# ==========================================
# ⚙️ CONFIGURAÇÕES DA ESTRATÉGIA DEX DCA
# ==========================================
PAR = 'SOL/USDC'
MOEDA_BASE = 'SOL'                    # O pareamento oficial Web3
INTERVALO = '15m'                   # Tempo gráfico ideal para o seu MACD rápido
INVESTIMENTO_INICIAL = 78.00       # Valor em DÓLARES (USDC)
MAX_COMPRAS = 3                     

DISTANCIA_MINIMA_QUEDA = 0.019      
LUCRO_MINIMO_PERCENTUAL = 0.69      

dex = conectar_dex()
inicializar_csv()

# ==========================================
# 🧠 MEMÓRIA DO BOT (CÉREBRO JSON)
# ==========================================
ARQUIVO_MEMORIA = "memoria_dex.json"

def salvar_memoria(estado):
    with open(ARQUIVO_MEMORIA, "w") as f:
        json.dump(estado, f)

def carregar_memoria():
    if os.path.exists(ARQUIVO_MEMORIA):
        with open(ARQUIVO_MEMORIA, "r") as f:
            return json.load(f)
    return None

posicao_aberta = False
num_compras = 0
total_investido = 0.0
total_qtd_comprada = 0.0
ultimo_preco_compra = 0.0
preco_medio = 0.0
capital_operacional = INVESTIMENTO_INICIAL
contador_telegram = 0

memoria_salva = carregar_memoria()
if memoria_salva:
    posicao_aberta = memoria_salva.get("posicao_aberta", False)
    num_compras = memoria_salva.get("num_compras", 0)
    total_investido = memoria_salva.get("total_investido", 0.0)
    total_qtd_comprada = memoria_salva.get("total_qtd_comprada", 0.0)
    ultimo_preco_compra = memoria_salva.get("ultimo_preco_compra", 0.0)
    preco_medio = memoria_salva.get("preco_medio", 0.0)
    capital_operacional = memoria_salva.get("capital_operacional", INVESTIMENTO_INICIAL)
    if posicao_aberta:
        print(f"💾 Memória DEX recuperada! Lotes: {num_compras}. PM: ${preco_medio:.2f}")

try:
    teste = buscar_ohlcv(dex, PAR, INTERVALO, limite=10)
    print("✅ Conexão Web3 OK! Dados recebidos da Blockchain.")
except Exception as e:
    print("❌ Falha no teste Web3:", e)
    exit()

print("🤖 Bot DEX DCA Iniciado...")

while True:
    try:
        ohlcv = buscar_ohlcv(dex, PAR, INTERVALO)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)

        df = calcular_macd(df)
        df.dropna(inplace=True)

        atual = df.iloc[-1]
        anterior = df.iloc[-2]

        dif_atual = atual['MACD_3_10_16']
        dea_atual = atual['MACDs_3_10_16']
        dif_anterior = anterior['MACD_3_10_16']
        dea_anterior = anterior['MACDs_3_10_16']
        preco_mercado = atual['close']

        cruzamento_compra = (dif_anterior < dea_anterior) and (dif_atual >= dea_atual)
        cruzamento_venda = (dif_anterior > dea_anterior) and (dif_atual <= dea_atual)
        
        #=========================================
        # 🟢 COMPRA 🟢
        #=========================================
        if cruzamento_compra and num_compras < MAX_COMPRAS:
            distancia_ok = True
            if num_compras > 0:
                preco_alvo = ultimo_preco_compra * (1 - DISTANCIA_MINIMA_QUEDA)
                if preco_mercado > preco_alvo:
                    distancia_ok = False

            if distancia_ok:
                usdc_balance = dex.fetch_balance().get('total', {}).get('USDC', 0)
                valor_da_ordem = capital_operacional / MAX_COMPRAS

                if valor_da_ordem > usdc_balance:
                    print(f"[{datetime.now()}] 💸 Saldo USDC insuficiente na Carteira.")
                else:
                    qtd_moeda = math.floor((valor_da_ordem / preco_mercado) * 100000) / 100000.0
                    valor_real_gasto = qtd_moeda * preco_mercado

                    dex.create_order(PAR, 'market', 'buy', qtd_moeda, preco_mercado)

                    num_compras += 1
                    total_qtd_comprada += qtd_moeda
                    total_investido += valor_real_gasto

                    preco_medio = total_investido / total_qtd_comprada
                    ultimo_preco_compra = preco_mercado
                    posicao_aberta = True

                    salvar_memoria({
                        "posicao_aberta": posicao_aberta, "num_compras": num_compras,
                        "total_investido": total_investido, "total_qtd_comprada": total_qtd_comprada,
                        "ultimo_preco_compra": ultimo_preco_compra, "preco_medio": preco_medio,
                        "capital_operacional": capital_operacional
                    })

                    registrar_operacao([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"COMPRA {num_compras}", preco_mercado, qtd_moeda, "", "", "", valor_real_gasto])
                    enviar_telegram(f"🛒 <b>COMPRA DEX ({num_compras}/{MAX_COMPRAS})</b>\n<b>Moeda:</b> {qtd_moeda} {MOEDA_BASE}\n<b>Preço:</b> ${preco_mercado:.2f}\n<b>Investido:</b> ${valor_real_gasto:.2f}\n📊 <b>Novo PM:</b> ${preco_medio:.2f}")

        #=========================================
        # 🔴 VENDA 🔴
        #=========================================
        elif posicao_aberta and cruzamento_venda:
            if preco_mercado > preco_medio:
                valor_total_venda = total_qtd_comprada * preco_mercado
                lucro = valor_total_venda - total_investido
                lucro_percentual = (lucro / total_investido) * 100

                if lucro_percentual >= LUCRO_MINIMO_PERCENTUAL:
                    moeda_balance = dex.fetch_balance().get('total', {}).get(MOEDA_BASE, 0.0)
                    qtd_para_venda = min(total_qtd_comprada, moeda_balance)
                    
                    # Venda executada na Blockchain
                    dex.create_order(PAR, 'market', 'sell', qtd_para_venda, preco_mercado)

                    registrar_operacao([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "VENDA TOTAL", "", total_qtd_comprada, preco_mercado, valor_total_venda, lucro, total_investido])
                    
                    capital_operacional += lucro
                    enviar_telegram(f"💰 <b>VENDA DEX COM LUCRO!</b>\n<b>Preço de Saída:</b> ${preco_mercado:.2f}\n🎉 <b>LUCRO:</b> ${lucro:.2f} ({lucro_percentual:.2f}%)\n🏦 <b>Novo Capital:</b> ${capital_operacional:.2f}")

                    posicao_aberta = False; num_compras = 0; total_investido = 0.0; total_qtd_comprada = 0.0; ultimo_preco_compra = 0.0; preco_medio = 0.0
                    salvar_memoria({"posicao_aberta": False, "num_compras": 0, "total_investido": 0.0, "total_qtd_comprada": 0.0, "ultimo_preco_compra": 0.0, "preco_medio": 0.0, "capital_operacional": capital_operacional})
                else:
                    print(f"[{datetime.now()}] ⏳ Venda ignorada: Lucro de {lucro_percentual:.2f}% não bateu o alvo.")

    except Exception as e:
        print(f"[{datetime.now()}] ⚠️ Erro Web3: {e}")

    if posicao_aberta:
        msg = f"📊 STATUS DEX | Preço: ${preco_mercado:.2f} | PM: ${preco_medio:.2f} | Lotes: {num_compras}/{MAX_COMPRAS}"
    else:
        msg = f"🔎 BUSCANDO SINAL DEX | Preço: ${preco_mercado:.2f} | Bolo Atual: ${capital_operacional:.2f}"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    contador_telegram += 1
    if contador_telegram >= 48:
        enviar_telegram(msg)
        contador_telegram = 0

    time.sleep(69)