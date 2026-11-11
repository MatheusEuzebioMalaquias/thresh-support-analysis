import os
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/thresh_suporte_ranqueada.csv", encoding="utf-8-sig")
df["resultado"] = df["vitoria"].map({True: "Vitória", False: "Derrota"})
ordem = ["Derrota", "Vitória"]

fig, eixos = plt.subplots(1, 2, figsize=(11, 5))
fig.suptitle("Thresh no suporte: suas 66 partidas ranqueadas", fontsize=14, fontweight="bold")

# Painel 1: KDA
dados_kda = [df.loc[df["resultado"] == r, "kda"] for r in ordem]
eixos[0].boxplot(dados_kda, tick_labels=ordem, showmeans=True)
eixos[0].set_title("KDA por resultado")
eixos[0].set_ylabel("KDA")
eixos[0].grid(axis="y", alpha=0.3)

# Painel 2: Dano por minuto
dados_dano = [df.loc[df["resultado"] == r, "dano_por_min"] for r in ordem]
eixos[1].boxplot(dados_dano, tick_labels=ordem, showmeans=True)
eixos[1].set_title("Dano por minuto, por resultado")
eixos[1].set_ylabel("Dano por minuto")
eixos[1].grid(axis="y", alpha=0.3)

fig.text(0.5, 0.01,
         "Linha dentro da caixa: mediana. Triângulo: média. Fonte: API de partidas da Riot Games.",
         ha="center", fontsize=9)
plt.tight_layout(rect=[0, 0.04, 1, 0.95])

os.makedirs("data/processed/graficos", exist_ok=True)
plt.savefig("data/processed/graficos/kda_dano_thresh.png", dpi=150)
print("Gráfico salvo em data/processed/graficos/kda_dano_thresh.png")
plt.show()