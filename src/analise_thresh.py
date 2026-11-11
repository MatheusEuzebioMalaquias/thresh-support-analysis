import json
import glob
import pandas as pd

PUUID = "6fLHj7QnJdnPZZWFLFHMLV9HFDoq0eV7Mk0-Kel9W4t5T-1OxVgaioRfRPHvZCKfNd-in76ni11GEg"
CAMPEAO = "Thresh"
POSICAO = "UTILITY"
FILAS = {420, 440}  # ranqueada solo e flex

linhas = []
for caminho in glob.glob("data/raw/historico/*.json"):
    with open(caminho, encoding="utf-8") as arquivo:
        info = json.load(arquivo)["info"]

    if info["queueId"] not in FILAS:
        continue

    # Só a sua linha, pelo puuid, com o campeão e a posição certos
    eu = next((p for p in info["participants"] if p["puuid"] == PUUID), None)
    if eu is None or eu["championName"] != CAMPEAO or eu["teamPosition"] != POSICAO:
        continue

    minutos = info["gameDuration"] / 60
    if minutos < 5:  # remake ou partida abandonada
        continue
    linhas.append({
        "partida": info["gameId"],
        "data": pd.to_datetime(info["gameCreation"], unit="ms"),
        "vitoria": eu["win"],
        "minutos": round(minutos, 1),
        "kda": round((eu["kills"] + eu["assists"]) / max(eu["deaths"], 1), 2),
        "ouro_por_min": round(eu["goldEarned"] / minutos, 1),
        "dano_por_min": round(eu["totalDamageDealt"] / minutos, 1),
        "visao": eu["visionScore"],
        "kills": eu["kills"],
        "deaths": eu["deaths"],
        "assists": eu["assists"],
        "visao_por_min": round(eu["visionScore"] / minutos, 2),
    })
    

if not linhas:
    print("Nenhuma partida encontrada. Confira o PUUID e os arquivos em data/raw/historico/.")
    raise SystemExit

df = pd.DataFrame(linhas).sort_values("data").reset_index(drop=True)
metricas = ["kda", "ouro_por_min", "dano_por_min", "visao_por_min", "minutos"]

print(f"Partidas analisadas: {len(df)}")
print(f"Taxa de vitória: {df['vitoria'].mean():.1%}\n")

# Média e mediana por resultado, para checar outliers
print(df.groupby("vitoria")[metricas].agg(["mean", "median"]).round(2).to_string())

# Evolução em blocos de 20 partidas
df["bloco"] = df.index // 20 + 1
print("\nEvolução por bloco de 20 partidas:")
print(df.groupby("bloco").agg(partidas=("vitoria", "size"), taxa_vitoria=("vitoria", "mean")).round(3).to_string())

df.to_csv("data/processed/thresh_suporte_ranqueada.csv", index=False, encoding="utf-8-sig")
print("\nSalvo em data/processed/thresh_suporte_ranqueada.csv")

# Tabela Markdown para o README
nomes = {
    "kda": "KDA",
    "ouro_por_min": "Ouro por minuto",
    "dano_por_min": "Dano por minuto",
    "visao_por_min": "Visão por minuto",
    "minutos": "Duração (min)",
}

resumo = df.groupby("vitoria")[list(nomes)].agg(["mean", "median"]).round(2)
derrota = resumo.loc[False]
vitoria = resumo.loc[True]

tabela = pd.DataFrame({
    "Indicador": list(nomes.values()),
    "Derrota (média)": derrota.xs("mean", level=1).values,
    "Derrota (mediana)": derrota.xs("median", level=1).values,
    "Vitória (média)": vitoria.xs("mean", level=1).values,
    "Vitória (mediana)": vitoria.xs("median", level=1).values,
})

taxa = df["vitoria"].mean()
cabecalho = (
    "# Thresh no suporte (ranqueada solo + flex)\n\n"
    f"Partidas analisadas: {len(df)} | Taxa de vitória: {taxa:.1%}\n\n"
)

markdown = tabela.to_markdown(index=False)
with open("data/processed/tabela_thresh.md", "w", encoding="utf-8") as arquivo:
    arquivo.write(cabecalho + markdown + "\n")

print("\nTabela Markdown salva em data/processed/tabela_thresh.md")
print(markdown)

# Extremos do KDA por resultado
extremos = df.groupby("vitoria")["kda"].agg(["min", "max"]).round(2)
extremos.index = ["Derrota", "Vitória"]
print("\nExtremos do KDA:")
print(extremos.to_string())

# Partidas com KDA mais alto, para checar se são atípicas
print("\nTop 3 partidas por KDA:")
print(df.nlargest(3, "kda")[["partida", "vitoria", "kda", "minutos", "kills", "deaths", "assists"]].to_string(index=False))