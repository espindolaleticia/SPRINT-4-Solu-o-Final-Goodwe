# =========================================================
# Gestão Sustentável de Eletropostos
# Sprint 4 - Entrega Final
# =========================================================
#
# Evolução da Sprint 3. A lógica é a mesma (solar > bateria > rede),
# com estas novidades:
#   - Simulação automática de um dia inteiro (opção 1 do menu)
#   - Relatório com economia e estimativa de CO2 evitado
#   - Gráfico simples da geração solar feito com texto
#
# =========================================================

import math
from datetime import datetime

# ---------- Configurações fixas do sistema ----------
CAPACIDADE_PAINEL_KW = 10.0
CAPACIDADE_BATERIA_KWH = 20.0
VALOR_KWH_REDE = 0.85

# FATOR DE EMISSÃO DA REDE (kg de CO2 por kWh) - VALOR PROVISÓRIO, CONFIRMAR NA FONTE OFICIAL ANTES DE ENTREGAR
FATOR_EMISSAO_REDE = 0.04

eletropostos = [
    {"id": 1, "nome": "Ponto Rápido", "potencia_kw": 50.0},
    {"id": 2, "nome": "Ponto Semirrápido", "potencia_kw": 22.0},
    {"id": 3, "nome": "Ponto Padrão", "potencia_kw": 7.4},
]

bateria = {
    "capacidade_kwh": CAPACIDADE_BATERIA_KWH,
    "nivel_kwh": CAPACIDADE_BATERIA_KWH * 0.5,
}

historico = []


def gerar_energia_solar(hora=None):
    if hora is None:
        agora = datetime.now()
        hora = agora.hour + agora.minute / 60

    if hora < 6 or hora > 18:
        return 0.0

    fator = math.sin(math.pi * (hora - 6) / 12)
    if fator < 0:
        fator = 0.0

    return round(CAPACIDADE_PAINEL_KW * fator, 2)


def carregar_bateria(kwh):
    espaco_livre = bateria["capacidade_kwh"] - bateria["nivel_kwh"]
    carregado = min(espaco_livre, kwh)
    bateria["nivel_kwh"] = bateria["nivel_kwh"] + carregado
    return carregado


def descarregar_bateria(kwh):
    fornecido = min(bateria["nivel_kwh"], kwh)
    bateria["nivel_kwh"] = bateria["nivel_kwh"] - fornecido
    return fornecido


def nivel_bateria_pct():
    return round((bateria["nivel_kwh"] / bateria["capacidade_kwh"]) * 100, 1)


def reiniciar_sistema(nivel_inicial_pct=50):
    # Volta a bateria ao nível inicial e limpa o histórico (útil para repetir testes)
    bateria["nivel_kwh"] = bateria["capacidade_kwh"] * nivel_inicial_pct / 100
    historico.clear()


def buscar_eletroposto(id_escolhido):
    for e in eletropostos:
        if e["id"] == id_escolhido:
            return e
    return None


def simular_recarga(id_eletroposto, tempo, hora, mostrar=True):
    estacao = buscar_eletroposto(id_eletroposto)
    if estacao is None:
        print("Eletroposto inválido.")
        return

    energia_necessaria = tempo * estacao["potencia_kw"]
    geracao_kw = gerar_energia_solar(hora)
    solar_disponivel = geracao_kw * tempo

    # Lógica de automação: solar -> bateria -> rede
    if solar_disponivel >= energia_necessaria:
        solar_usado = energia_necessaria
        excedente = solar_disponivel - energia_necessaria
        carregar_bateria(excedente)
        bateria_usada = 0.0
        rede_usada = 0.0
    else:
        solar_usado = solar_disponivel
        faltante = energia_necessaria - solar_usado
        bateria_usada = descarregar_bateria(faltante)
        faltante = faltante - bateria_usada
        rede_usada = faltante

    custo = rede_usada * VALOR_KWH_REDE
    perc_renovavel = round(((solar_usado + bateria_usada) / energia_necessaria) * 100, 1)

    sessao = {
        "hora": hora,
        "estacao": estacao["nome"],
        "tempo_h": tempo,
        "energia_kwh": energia_necessaria,
        "solar_kwh": solar_usado,
        "bateria_kwh": bateria_usada,
        "rede_kwh": rede_usada,
        "custo_rs": custo,
        "perc_renovavel": perc_renovavel,
        "bateria_pct": nivel_bateria_pct(),
    }
    historico.append(sessao)

    if mostrar:
        print(f"{hora:5.1f}h | {estacao['nome']:18s} | {tempo:4.2f}h | "
              f"{energia_necessaria:6.2f} kWh | solar {solar_usado:6.2f} | "
              f"bat {bateria_usada:6.2f} | rede {rede_usada:6.2f} | "
              f"R$ {custo:6.2f} | bateria {nivel_bateria_pct():5.1f}%")


def mostrar_barra(nome, valor, total):
    if total > 0:
        tamanho = int((valor / total) * 40)
    else:
        tamanho = 0
    barra = "#" * tamanho
    print(f"{nome:8s} | {barra} {valor:.1f} kWh")


def gerar_relatorio():
    if len(historico) == 0:
        print("Nenhuma recarga foi simulada ainda.")
        return

    total_energia = 0
    total_solar = 0
    total_bateria = 0
    total_rede = 0
    total_custo = 0

    for sessao in historico:
        total_energia = total_energia + sessao["energia_kwh"]
        total_solar = total_solar + sessao["solar_kwh"]
        total_bateria = total_bateria + sessao["bateria_kwh"]
        total_rede = total_rede + sessao["rede_kwh"]
        total_custo = total_custo + sessao["custo_rs"]

    perc_medio = round(((total_solar + total_bateria) / total_energia) * 100, 1)

    # Comparação: quanto custaria e emitiria se TODA a energia viesse da rede
    custo_sem_solar = total_energia * VALOR_KWH_REDE
    economia = custo_sem_solar - total_custo
    co2_sem_solar = total_energia * FATOR_EMISSAO_REDE
    co2_com_solar = total_rede * FATOR_EMISSAO_REDE
    co2_evitado = co2_sem_solar - co2_com_solar

    print("====== RELATÓRIO GERAL ======")
    print(f"Sessões registradas: {len(historico)}")
    print(f"Energia total: {total_energia:.2f} kWh")
    print(f"  Solar:   {total_solar:.2f} kWh")
    print(f"  Bateria: {total_bateria:.2f} kWh")
    print(f"  Rede:    {total_rede:.2f} kWh")
    print(f"Participação renovável média: {perc_medio}%")
    print()
    print(f"Custo com o sistema:    R$ {total_custo:.2f}")
    print(f"Custo só com a rede:    R$ {custo_sem_solar:.2f}")
    print(f"Economia:               R$ {economia:.2f}")
    print(f"CO2 evitado (estimado): {co2_evitado:.2f} kg")
    print()
    print("Distribuição de energia por fonte:")
    mostrar_barra("Solar", total_solar, total_energia)
    mostrar_barra("Bateria", total_bateria, total_energia)
    mostrar_barra("Rede", total_rede, total_energia)


def simular_dia():
    cenarios = [
        (8.0, 3, 1.0),    # manhã, ponto padrão (sol ainda fraco)
        (10.0, 3, 1.0),   # sol forte, sobra energia para a bateria
        (11.0, 3, 1.0),   # sol forte
        (12.0, 3, 1.0),   # pico solar
        (13.0, 3, 0.5),   # recarga curta
        (14.0, 2, 0.5),   # semirrápido, usa solar + bateria
        (17.0, 3, 1.0),   # fim da tarde, sol caindo
        (19.0, 3, 1.0),   # noite, sem sol: bateria + rede
        (20.0, 1, 0.25),  # noite, ponto rápido: quase tudo da rede
    ]

    reiniciar_sistema(50)
    print(f"Bateria inicial: {nivel_bateria_pct()}%\n")

    for hora, id_posto, tempo in cenarios:
        simular_recarga(id_posto, tempo, hora)

    print()
    gerar_relatorio()


def mostrar_curva_solar():
    print("Geração solar por horário:")
    for h in range(5, 20):
        kw = gerar_energia_solar(h)
        print(f"{h:02d}h | {'#' * int(kw * 4)} {kw:.2f} kW")


def main():
    print("===================================")
    print(" GESTÃO SUSTENTÁVEL DE ELETROPOSTOS ")
    print("===================================")

    while True:
        print("\nMENU")
        print("1 - Simular um dia inteiro (automático)")
        print("2 - Simular uma recarga (digitando os dados)")
        print("3 - Ver status do sistema")
        print("4 - Gerar relatório")
        print("5 - Ver curva de geração solar")
        print("6 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            simular_dia()
        elif opcao == "2":
            try:
                hora = float(input("Hora do dia (0-23): "))
                id_posto = int(input("Eletroposto (1-3): "))
                tempo = float(input("Tempo de carregamento (horas): "))
            except ValueError:
                print("Valor inválido.")
                continue
            simular_recarga(id_posto, tempo, hora)
        elif opcao == "3":
            print(f"Geração solar atual: {gerar_energia_solar():.2f} kW")
            print(f"Bateria: {nivel_bateria_pct()}%")
        elif opcao == "4":
            gerar_relatorio()
        elif opcao == "5":
            mostrar_curva_solar()
        elif opcao == "6":
            print("Encerrando sistema...")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()
