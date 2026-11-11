from dotenv import load_dotenv
import os
import json
import time
import requests

load_dotenv()
headers = {"X-Riot-Token": os.getenv("RIOT_API_KEY")}


PUUID = "hCssjXDwsNfU_EP_uKEUFu8MgmUzf7wcu0j7P50Dfgu2atlqWkOKqSjkqd4elk5mMmn6HrCQfk3Z7g"
CAMPEAO = "Thresh"
BASE = "https://americas.api.riotgames.com/lol/match/v5/matches"

# 1. Lista todos os IDs, de 100 em 100
ids = []
inicio = 0
while True:
    resposta = requests.get(
        f"{BASE}/by-puuid/{PUUID}/ids",
        headers=headers,
        params={"start": inicio, "count": 100},
    )
    if resposta.status_code != 200:
        print("Erro ao listar partidas:", resposta.status_code)
        break
    bloco = resposta.json()
    if not bloco:
        break  # acabou o histórico
    ids.extend(bloco)
    inicio += 100
    time.sleep(1.5)

print(len(ids), "partidas no seu histórico")

# 2. Baixa os detalhes e guarda só as partidas em que você jogou de Thresh
os.makedirs("data/raw/historico", exist_ok=True)
partidas_thresh = []

for i, match_id in enumerate(ids, start=1):
    caminho = f"data/raw/historico/{match_id}.json"

    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    else:
        resposta = requests.get(f"{BASE}/{match_id}", headers=headers)
        time.sleep(1.5)
        if resposta.status_code != 200:
            print(match_id, "| Status:", resposta.status_code)
            continue
        dados = resposta.json()
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False)

    eu = next((p for p in dados["info"]["participants"] if p["puuid"] == PUUID), None)
    if eu and eu["championName"] == CAMPEAO:
        partidas_thresh.append(match_id)

    if i % 20 == 0:
        print(f"{i}/{len(ids)} analisadas")

print(f"\n{len(partidas_thresh)} partidas com {CAMPEAO}")
print(partidas_thresh)