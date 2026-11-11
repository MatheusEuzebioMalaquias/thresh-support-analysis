import json
import glob
import pandas as pd

linhas = []
for caminho in sorted(glob.glob("data/raw/partida_*.json")):
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    info = dados["info"]
    minutos = info["gameDuration"] / 60
    participantes = info["participants"]

    # Total de abates de cada time, para calcular a participação de cada jogador
    abates_time = {}
    for p in participantes:
        abates_time[p["teamId"]] = abates_time.get(p["teamId"], 0) + p["kills"]

    for p in participantes:
        abates = abates_time[p["teamId"]]
        linhas.append({
            "partida": dados["metadata"]["matchId"],
            "jogador": p["riotIdGameName"],
            "campeao": p["championName"],
            "posicao": p["teamPosition"],
            "time": p["teamId"],
            "vitoria": p["win"],
            "minutos": round(minutos, 1),
            "kills": p["kills"],
            "deaths": p["deaths"],
            "assists": p["assists"],
            "kda": round((p["kills"] + p["assists"]) / max(p["deaths"], 1), 2),
            "participacao_abates": round((p["kills"] + p["assists"]) / max(abates, 1), 2),
            "ouro": p["goldEarned"],
            "ouro_por_min": round(p["goldEarned"] / minutos, 1),
            "dano": p["totalDamageDealt"],
            "dano_por_min": round(p["totalDamageDealt"] / minutos, 1),
            "dano_recebido": p["totalDamageTaken"],
            "visao": p["visionScore"],
        })

df = pd.DataFrame(linhas)
df.to_csv("data/processed/partidas_jogadores.csv", index=False, encoding="utf-8-sig")

print(df.groupby("vitoria")[["kda", "participacao_abates", "ouro_por_min", "dano_por_min", "visao"]].mean().round(2))
print("\nSalvo em data/processed/partidas_jogadores.csv")