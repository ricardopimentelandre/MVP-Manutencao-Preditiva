#!/usr/bin/env python3
"""Auditoria reprodutível dos CSVs AI4I 2020 bronze/prata.

Uso:
  python scripts/auditar_dados.py --bronze caminho/bronze.csv --prata caminho/prata.csv
O script só lê os arquivos; opcionalmente salva um novo JSON com --saida arquivo.json.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ENTRADAS = [
    "Type", "Air temperature", "Process temperature",
    "Rotational speed", "Torque", "Tool wear", "Machine failure",
]
CAMPOS_BRONZE = [
    "UID", "Product ID", *ENTRADAS, "TWF", "HDF", "PWF", "OSF", "RNF",
]
MODOS = ["TWF", "HDF", "PWF", "OSF", "RNF"]


def ler_csv(caminho):
    with Path(caminho).open(encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        cabecalho = list(leitor.fieldnames or [])
        linhas = list(leitor)
    if not linhas:
        raise ValueError(f"Arquivo vazio: {caminho}")
    if any(None in linha for linha in linhas):
        raise ValueError(f"Quantidade inconsistente de colunas em {caminho}")
    return cabecalho, linhas


def sha256(caminho):
    h = hashlib.sha256()
    with Path(caminho).open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def auditar(bronze_path, prata_path):
    col_b, bronze = ler_csv(bronze_path)
    col_p, prata = ler_csv(prata_path)
    if col_b != CAMPOS_BRONZE:
        raise ValueError(f"Esquema bronze inesperado: {col_b}")
    if col_p != ENTRADAS:
        raise ValueError(f"Esquema prata inesperado: {col_p}")
    if len(bronze) != len(prata):
        raise ValueError("Contagens diferentes: bronze x prata")

    estatisticas = {}
    nulos_totais = 0
    for coluna in ENTRADAS:
        valores = [row[coluna] for row in prata]
        ausentes = sum(v is None or not v.strip() for v in valores)
        nulos_totais += ausentes
        frequencias = Counter(valores)
        registro = {
            "n": len(valores), "nulos": ausentes, "distintos": len(frequencias)
        }
        if coluna in ("Type", "Machine failure"):
            registro["valores"] = dict(sorted(frequencias.items()))
        else:
            numeros = [float(v) for v in valores if v and v.strip()]
            registro["minimo"] = min(numeros) if numeros else None
            registro["maximo"] = max(numeros) if numeros else None
            registro["inteiros"] = all(x.is_integer() for x in numeros)
        estatisticas[coluna] = registro

    preservadas = sum(
        bronze[i][col] == prata[i][col]
        for i in range(len(prata)) for col in ENTRADAS
    )
    ids = [row["UID"] for row in bronze]
    linhas_duplicadas = len(prata) - len({
        tuple(row[col] for col in ENTRADAS) for row in prata
    })
    categorias_invalidas = sum(
        row["Type"] not in {"L", "M", "H"}
        or row["Machine failure"] not in {"0", "1"}
        for row in prata
    )
    fisicos_invalidos = sum(
        float(row["Air temperature"]) <= 0
        or float(row["Process temperature"]) <= 0
        or float(row["Rotational speed"]) <= 0
        or float(row["Torque"]) < 0
        or float(row["Tool wear"]) < 0
        for row in prata
    )
    processo_abaixo_ar = sum(
        float(row["Process temperature"]) < float(row["Air temperature"])
        for row in prata
    )
    divergencias = []
    for row in bronze:
        alvo = int(row["Machine failure"])
        algum_modo = int(any(int(row[modo]) == 1 for modo in MODOS))
        if alvo != algum_modo:
            divergencias.append((alvo, algum_modo))
    controles = {
        "nulos_em_prata": nulos_totais,
        "linhas_duplicadas_exatas_na_prata": linhas_duplicadas,
        "celulas_preservadas_da_bronze_para_prata": preservadas,
        "celulas_esperadas": len(prata) * len(ENTRADAS),
        "tipos_de_categoria_ou_alvo_invalidos": categorias_invalidas,
        "valores_fisicos_sinal_invalido": fisicos_invalidos,
        "temperatura_processo_menor_que_ar": processo_abaixo_ar,
        "UID_bronze_valores_unicos": len(set(ids)),
        "UID_bronze_fora_sequencia": sum(
            not uid.isdigit() or int(uid) != i
            for i, uid in enumerate(ids, start=1)
        ),
        "ID_produto_tipo_incompativel": sum(
            not r["Product ID"].startswith(r["Type"]) for r in bronze
        ),
        "divergencias_alvo_versus_ou_dos_modos": len(divergencias),
        "alvo_1_sem_modo_1": sum(a == 1 for a, m in divergencias),
        "alvo_0_com_modo_1": sum(a == 0 for a, m in divergencias),
    }
    return {
        "projeto": "MVP SSD — Manutenção Preditiva",
        "verificacao": "Qualidade e linhagem bronze/prata",
        "data_verificacao_utc": datetime.now(timezone.utc).isoformat(),
        "fonte": "AI4I 2020, UCI id=601 (dados sintéticos)",
        "arquivos": {
            "bronze": {"linhas": len(bronze), "colunas": col_b, "sha256": sha256(bronze_path)},
            "prata": {"linhas": len(prata), "colunas": col_p, "sha256": sha256(prata_path)},
        },
        "estatisticas_por_coluna": estatisticas,
        "controles": controles,
        "ressalva": "Não altera rótulos nem dados. Divergências alvo/modos são registradas como achado.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bronze", type=Path, required=True)
    parser.add_argument("--prata", type=Path, required=True)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    resultado = auditar(args.bronze, args.prata)
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    if args.saida:
        args.saida.write_text(conteudo, encoding="utf-8")
    print(conteudo)


if __name__ == "__main__":
    main()
