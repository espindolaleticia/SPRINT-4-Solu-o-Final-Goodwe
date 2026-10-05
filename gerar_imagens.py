# Gera as imagens do README a partir dos resultados reais do sers_sprint4.py
# Precisa do matplotlib: pip install matplotlib
import io
import contextlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import sers_sprint4 as s

# ---------- roda a simulação e captura o texto do terminal ----------
s.reiniciar_sistema(50)
buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    s.simular_dia()
texto_dia = buffer.getvalue()

buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    s.mostrar_curva_solar()
texto_curva = buffer.getvalue()


def imagem_terminal(texto, arquivo, largura=15):
    linhas = texto.rstrip("\n").split("\n")
    altura = max(2, 0.185 * len(linhas) + 1.0)
    fig = plt.figure(figsize=(largura, altura), facecolor="#1e1e1e")
    fig.text(0.015, 0.975, "$ python sers_sprint4.py", color="#9cdcfe",
             family="monospace", fontsize=10, va="top")
    fig.text(0.015, 0.92, "\n".join(linhas), color="#d4d4d4",
             family="monospace", fontsize=9, va="top", linespacing=1.35)
    fig.savefig(arquivo, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


imagem_terminal(texto_dia, "imagens/03_terminal_simulacao_dia.png")
imagem_terminal(texto_curva, "imagens/05_terminal_curva_solar.png", largura=8)

# ---------- gráfico: fonte de energia por recarga + nível da bateria ----------
horas = [f"{int(x['hora']):02d}h" for x in s.historico]
solar = [x["solar_kwh"] for x in s.historico]
bat = [x["bateria_kwh"] for x in s.historico]
rede = [x["rede_kwh"] for x in s.historico]
nivel = [x["bateria_pct"] for x in s.historico]

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(horas, solar, label="Solar", color="#f4b400")
ax.bar(horas, bat, bottom=solar, label="Bateria", color="#34a853")
base = [a + b for a, b in zip(solar, bat)]
ax.bar(horas, rede, bottom=base, label="Rede", color="#7f7f7f")
ax.set_ylabel("Energia da recarga (kWh)")
ax.set_xlabel("Horário da recarga")
ax.set_title("Origem da energia em cada recarga (dia simulado)")
ax2 = ax.twinx()
ax2.plot(horas, nivel, color="#d93025", marker="o", label="Nível da bateria (%)")
ax2.set_ylabel("Bateria após a recarga (%)")
ax2.set_ylim(0, 100)
l1, n1 = ax.get_legend_handles_labels()
l2, n2 = ax2.get_legend_handles_labels()
ax.legend(l1 + l2, n1 + n2, loc="upper left")
fig.tight_layout()
fig.savefig("imagens/04_origem_energia_por_recarga.png", dpi=130)
plt.close(fig)

# ---------- gráfico: curva solar ----------
hs = list(range(5, 20))
kw = [s.gerar_energia_solar(h) for h in hs]
fig, ax = plt.subplots(figsize=(8, 4))
ax.fill_between(hs, kw, color="#f4b400", alpha=0.6)
ax.plot(hs, kw, color="#b8860b")
ax.set_xlabel("Hora do dia")
ax.set_ylabel("Geração solar (kW)")
ax.set_title("Curva de geração solar simulada (painel de 10 kW)")
ax.set_xticks(hs)
fig.tight_layout()
fig.savefig("imagens/06_curva_geracao_solar.png", dpi=130)
plt.close(fig)

# ---------- diagrama de arquitetura ----------
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, 12)
ax.set_ylim(0, 6)
ax.axis("off")


def caixa(x, y, w, h, texto, cor):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                fc=cor, ec="#333333", lw=1.2))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=10)


def seta(x1, y1, x2, y2, duplo=False):
    estilo = "<->" if duplo else "->"
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=estilo,
                                 mutation_scale=15, lw=1.5, color="#333333"))


caixa(0.3, 4.3, 2.6, 1.0, "Painel solar\n10 kW", "#fde68a")
caixa(0.3, 2.5, 2.6, 1.0, "Bateria\n20 kWh", "#bbf7d0")
caixa(0.3, 0.7, 2.6, 1.0, "Rede elétrica\nR$ 0,85/kWh", "#e5e7eb")
caixa(4.4, 2.3, 3.0, 1.4, "AUTOMAÇÃO\nsolar > bateria > rede", "#bfdbfe")
caixa(9.0, 4.3, 2.7, 1.0, "Ponto Rápido\n50 kW", "#fecaca")
caixa(9.0, 2.5, 2.7, 1.0, "Ponto Semirrápido\n22 kW", "#fecaca")
caixa(9.0, 0.7, 2.7, 1.0, "Ponto Padrão\n7,4 kW", "#fecaca")
caixa(4.4, 0.2, 3.0, 0.9, "Histórico + relatório\n(fontes, custo, CO₂)", "#ddd6fe")
seta(2.95, 4.8, 4.4, 3.4)
seta(2.95, 3.0, 4.4, 3.0, duplo=True)
seta(2.95, 1.2, 4.4, 2.6)
seta(7.4, 3.4, 9.0, 4.8)
seta(7.4, 3.0, 9.0, 3.0)
seta(7.4, 2.6, 9.0, 1.2)
seta(5.9, 2.3, 5.9, 1.1)
ax.set_title("SERS — arquitetura da solução", fontsize=13)
fig.savefig("imagens/01_arquitetura.png", dpi=130, bbox_inches="tight")
plt.close(fig)

# ---------- fluxograma da automação ----------
fig, ax = plt.subplots(figsize=(11, 6.5))
ax.set_xlim(0, 11)
ax.set_ylim(-0.4, 6.5)
ax.axis("off")
caixa(0.3, 5.3, 3.0, 0.9, "Início da recarga:\nenergia = tempo × potência", "#bfdbfe")
caixa(4.0, 5.3, 3.0, 0.9, "Solar cobre\ntoda a energia?", "#fde68a")
caixa(7.7, 5.5, 3.0, 0.8, "Usa 100% solar;\nexcedente vai à bateria", "#bbf7d0")
caixa(4.0, 3.7, 3.0, 0.9, "Usa todo o solar\ndisponível", "#fde68a")
caixa(4.0, 2.2, 3.0, 0.9, "Bateria cobre\no restante?", "#bbf7d0")
caixa(0.3, 0.7, 3.2, 0.9, "Completa com a bateria", "#bbf7d0")
caixa(7.5, 0.7, 3.2, 0.9, "Completa com a rede", "#e5e7eb")
caixa(3.9, 0.0, 3.2, 0.6, "Registra no histórico", "#ddd6fe")
seta(3.3, 5.75, 4.0, 5.75)
seta(7.0, 5.9, 7.7, 5.9)
ax.text(7.05, 5.6, "Sim", fontsize=9)
seta(5.5, 5.3, 5.5, 4.6)
ax.text(5.6, 4.9, "Não", fontsize=9)
seta(5.5, 3.7, 5.5, 3.1)
seta(4.0, 2.65, 2.4, 1.6)
ax.text(2.8, 2.4, "Sim", fontsize=9)
seta(7.0, 2.65, 9.1, 1.6)
ax.text(8.4, 2.4, "Não", fontsize=9)
seta(3.5, 1.15, 4.4, 0.6)
seta(7.5, 1.15, 6.6, 0.6)
ax.set_title("Lógica de automação — escolha da fonte de energia", fontsize=13)
fig.savefig("imagens/02_fluxograma_automacao.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("imagens geradas")
