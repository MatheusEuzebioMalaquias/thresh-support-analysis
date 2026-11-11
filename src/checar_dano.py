import pandas as pd

df = pd.read_csv("data/processed/thresh_suporte_ranqueada.csv", encoding="utf-8-sig")

baixos = df.nsmallest(5, "dano_por_min")[["partida", "data", "vitoria", "minutos", "dano_por_min", "kda", "ouro_por_min"]]
print(baixos.to_string(index=False))