import requests
import statistics
import time
from datetime import datetime, timedelta

BLOCKCHAINS = {
    'bitcoin': 'https://mempool.space/api/mempool',
    'ethereum': 'https://api.blocknative.com/gasprices/blockprices'  # requires API key
}

ETH_HEADERS = {
    'Authorization': 'Bearer YOUR_BLOCKNATIVE_API_KEY'
}

def fetch_bitcoin_mempool():
    try:
        response = requests.get(BLOCKCHAINS['bitcoin'])
        data = response.json()
        return data['count'], data['vsize']
    except Exception as e:
        print(f"[BTC] Error fetching mempool: {e}")
        return None, None

def fetch_eth_gas():
    try:
        response = requests.get(BLOCKCHAINS['ethereum'], headers=ETH_HEADERS)
        data = response.json()
        price = data['blockPrices'][0]['estimatedPrices'][0]['price']
        return price
    except Exception as e:
        print(f"[ETH] Error fetching gas data: {e}")
        return None

def monitor(duration_minutes=10, interval_seconds=60):
    print("📊 Starting Cryptopsy mempool analysis...")
    btc_counts = []
    btc_sizes = []
    eth_gas_prices = []

    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)

    while datetime.utcnow() < end_time:
        btc_count, btc_size = fetch_bitcoin_mempool()
        eth_gas = fetch_eth_gas()

        if btc_count is not None:
            btc_counts.append(btc_count)
            btc_sizes.append(btc_size)

        if eth_gas is not None:
            eth_gas_prices.append(eth_gas)

        print(f"[{datetime.utcnow().isoformat()}] BTC: {btc_count} txs | ETH: {eth_gas} gwei")
        time.sleep(interval_seconds)

    analyze(btc_counts, btc_sizes, eth_gas_prices)

def analyze(btc_counts, btc_sizes, eth_gas_prices):
    print("\n🔍 Analysis Summary:\n")
    if btc_counts:
        avg_count = statistics.mean(btc_counts)
        peak_count = max(btc_counts)
        low_count = min(btc_counts)
        print(f"📈 Bitcoin mempool tx count — avg: {avg_count:.0f}, peak: {peak_count}, low: {low_count}")

    if btc_sizes:
        avg_vsize = statistics.mean(btc_sizes)
        print(f"📦 Bitcoin mempool avg virtual size: {avg_vsize:.0f} vbytes")

    if eth_gas_prices:
        avg_gas = statistics.mean(eth_gas_prices)
        min_gas = min(eth_gas_prices)
        print(f"⛽ Ethereum gas price — avg: {avg_gas:.1f} gwei, min: {min_gas} gwei")
        if min_gas < avg_gas * 0.75:
            print("✅ Recommended: Wait for low gas window — fees expected to drop soon.")
        else:
            print("⚠️ Gas prices relatively stable or rising — consider waiting.")

if __name__ == "__main__":
    monitor(duration_minutes=5, interval_seconds=60)
