# Dex-Trader

# 🚀 Hyperliquid DCA Bot (SOL/USDC)

Este é um bot de trading automatizado focado em finanças descentralizadas (DeFi), operando especificamente na DEX **Hyperliquid**. O sistema utiliza uma estratégia de **DCA (Dollar Cost Averaging)** combinada com o indicador técnico **MACD** para realizar entradas e saídas estratégicas no par **SOL/USDC**.

## 📌 Funcionalidades

- **Estratégia DCA Automática:** Divide o capital em fatias para reduzir o preço médio em quedas do mercado.
- **Análise Técnica:** Utiliza um MACD customizado (3, 10, 16) calculado via Pandas para identificar pontos de reversão.
- **Conectividade Web3:** Integração total com a Hyperliquid via biblioteca `ccxt`.
- **Proteção de Slippage:** Execução de ordens a mercado com preço de referência para evitar derrapagens de preço.
- **Gestão de Memória:** Cérebro JSON (`memoria_dex.json`) que permite que o bot seja reiniciado sem perder o rastro da operação atual.
- **Notificações em Tempo Real:** Alertas detalhados via Telegram (Compras, Vendas, Lucro e Status).
- **Registro de Operações:** Histórico completo de trades salvo em `registro_operacoes.csv`.

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Pandas:** Para manipulação de dados e cálculos matemáticos.
- **CCXT:** Para comunicação com a API da Hyperliquid.
- **Python-dotenv:** Para gestão segura de chaves privadas.
- **Telegram API:** Para monitoramento remoto.

## 📂 Estrutura do Projeto

- `main_dex.py`: O motor principal do robô.
- `dex_trader.py`: Módulo de conexão e busca de dados na Blockchain.
- `indicadores.py`: Cálculos matemáticos dos indicadores técnicos.
- `registro.py`: Funções para salvamento e persistência de dados.
- `.env`: Arquivo de configuração de credenciais (não versionado por segurança).

## ⚙️ Configuração e Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/Lucianoherval/Dex-Trader.git
    cd Dex-Trader
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install pandas ccxt python-dotenv requests
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto:
    ```env
    WALLET_ADDRESS=0xSuaCarteiraPublica
    PRIVATE_KEY=SuaChavePrivada
    TELEGRAM_TOKEN=SeuTokenDoBot
    TELEGRAM_CHAT_ID=SeuChatID
    ```

## 📈 Estratégia Detalhada

O bot opera sob os seguintes parâmetros:
- **Intervalo:** 15 minutos.
- **Fatias (DCA):** Máximo de 3 compras.
- **Distância de Queda:** 1.9% entre lotes.
- **Alvo de Lucro:** 0.69% sobre o preço médio.

## ⚠️ Aviso Legal (Disclaimer)

Este software foi desenvolvido para fins de estudo de programação e automação. O mercado de criptomoedas é volátil e envolve riscos financeiros. O autor não se responsabiliza por perdas financeiras decorrentes do uso deste robô. **Nunca compartilhe sua Chave Privada.**

## DEUS NO COMANDO!🙌