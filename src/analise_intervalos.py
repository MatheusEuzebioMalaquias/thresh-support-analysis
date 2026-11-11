import math
import numpy as np
import pandas as pd

df = pd.read_csv("data/processed/thresh_suporte_ranqueada.csv", encoding="utf-8-sig")
Z = 1.96  # 95% de confiança
np.random.seed(42)  # para o bootstrap sair sempre igual


def wilson(k, n, z=Z):
    """Intervalo de Wilson para uma proporção (taxa de vitória)."""
    p = k / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margem = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return centro - margem, centro + margem


def bootstrap_mediana(valores, reamostras=10000):
    """Intervalo de 95% da mediana, por reamostragem."""
    valores = np.asarray(valores)
    medianas = [np.median(np.random.choice(valores, len(valores), replace=True))
                for _ in range(reamostras)]
    return np.percentile(medianas, [2.5, 97.5])


def bootstrap_diferenca(a, b, reamostras=10000):
    """Intervalo de 95% da diferença de medianas (a - b)."""
    a, b = np.asarray(a), np.asarray(b)
    difs = [np.median(np.random.choice(a, len(a), replace=True))
            - np.median(np.random.choice(b, len(b), replace=True))
            for _ in range(reamostras)]
    return np.percentile(difs, [2.5, 97.5])


# 1. Taxa de vitória
n = len(df)
k = int(df["vitoria"].sum())
baixo, alto = wilson(k, n)
print(f"Taxa de vitória: {k}/{n} = {k/n:.1%}")
print(f"Intervalo de Wilson (95%): {baixo:.1%} a {alto:.1%}\n")

# 2. Mediana do KDA por resultado
kda_vit = df.loc[df["vitoria"], "kda"]
kda_der = df.loc[~df["vitoria"], "kda"]

print(f"Mediana KDA vitórias: {kda_vit.median():.2f}  IC 95%: {np.round(bootstrap_mediana(kda_vit), 2)}")
print(f"Mediana KDA derrotas: {kda_der.median():.2f}  IC 95%: {np.round(bootstrap_mediana(kda_der), 2)}")

# 3. Diferença entre as medianas
dif = kda_vit.median() - kda_der.median()
ic_dif = bootstrap_diferenca(kda_vit, kda_der)
print(f"\nDiferença de medianas (vitória - derrota): {dif:.2f}  IC 95%: {np.round(ic_dif, 2)}")
if ic_dif[0] > 0:
    print("O intervalo não inclui zero: a diferença é consistente com os dados.")
else:
    print("O intervalo inclui zero: a diferença não é conclusiva.")

# 4. Mesma análise para o dano por minuto (comparação com a referência)
dano_vit = df.loc[df["vitoria"], "dano_por_min"]
dano_der = df.loc[~df["vitoria"], "dano_por_min"]
print(f"\nMediana dano/min vitórias: {dano_vit.median():.1f}  IC 95%: {np.round(bootstrap_mediana(dano_vit), 1)}")
print(f"Mediana dano/min derrotas: {dano_der.median():.1f}  IC 95%: {np.round(bootstrap_mediana(dano_der), 1)}")