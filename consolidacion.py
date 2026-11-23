"""
Une los 16 CSV de Ng et al. (2018) en un solo corpus depurado.

Sigue la misma lógica que las secciones 1, 3 y 9 de EDA_censura_weibo2.ipynb:
- Carga sin encabezado (salvo fifty-cent-uncensored.csv, que trae "Content").
- Etiqueta y tema salen del nombre del archivo: <tema>-<etiqueta>.csv.
- Quita \u200b y espacios de los extremos.
- Elimina textos vacíos.
- Elimina textos que aparecen con etiquetas contradictorias.
- Conserva una sola copia de cada texto duplicado.
"""
import numpy as np
import pandas as pd

from pathlib import Path

DATA_DIR = Path("data_nlp4if_2018")   # carpeta con los 16 CSV
OUT = Path("corpus_zh.csv")
ZW = "\u200b"

# Categoría que Ng et al. (2018) asignan a cada tema (igual que el notebook, sección 9).
# melamine y poisonous-milk-powder forman el tema "milk scandal" del artículo.
CATEGORIA = {
    "boxilai": "Bo Xilai",
    "fifty-cent": "censura y propaganda en internet",
    "censored": "censura y propaganda en internet",
    "ditch-oil": "contaminación e inocuidad alimentaria",
    "melamine": "contaminación e inocuidad alimentaria",
    "poisonous-milk-powder": "contaminación e inocuidad alimentaria",
    "smog": "contaminación e inocuidad alimentaria",
    "kindergarten": "abuso en guarderías",
}

def cargar(path: Path) -> pd.DataFrame:
    """Lee un CSV de Ng et al. y devuelve texto, tema, etiqueta y archivo."""
    df = pd.read_csv(path, header = None, names = ['texto'], dtype = str, keep_default_na = False)

    # Solo fifty-cent-uncensored.csv trae encabezado
    if df["texto"].iloc[0].strip() == "Content": df = df.iloc[1:]

    # "fifty-cent-uncensored" -> tema "fifty-cent", etiqueta "uncensored"
    tema, etiqueta = path.stem.rsplit("-", 1)
    return df.assign(tema=tema, etiqueta=etiqueta, archivo=path.name)

def main() -> None:
    archivos = sorted(DATA_DIR.glob("*.csv"))
    if not archivos:
        raise FileNotFoundError(f"No hay CSV en {DATA_DIR.resolve()}")
    print(f"Archivos encontrados: {len(archivos)}")

    df = pd.concat([cargar(f) for f in archivos], ignore_index=True)
    print("Filas cargadas:", len(df))

    # Limpieza (notebook, sección 1)
    df["tiene_zw"] = df["texto"].str.contains(ZW, regex=False)
    df["texto_zh"] = df["texto"].str.replace(ZW, "", regex=False).str.strip()

    # Textos vacíos
    df = df[df["texto_zh"].str.len() > 0].copy()

    # Textos con etiquetas contradictorias: se eliminan todas sus apariciones (sección 9)
    n_lab = df.groupby("texto_zh")["etiqueta"].nunique()
    contradictorios = set(n_lab[n_lab > 1].index)
    df = df[~df["texto_zh"].isin(contradictorios)]

    # Duplicados: se conserva la primera copia (sección 9)
    df = df.drop_duplicates("texto_zh").reset_index(drop=True)

    # Columnas finales
    df["label"] = (df["etiqueta"] == "censored").astype(int)   # 1 = censurado, 0 = no censurado
    df["categoria"] = df["tema"].map(CATEGORIA)
    df["longitud"] = df["texto_zh"].str.len()

    corpus = df[[
        "texto",          # original, tal como viene en el CSV
        "texto_zh",       # limpio: sin \u200b ni espacios extremos
        "label",          # 1 = censored, 0 = uncensored
        "etiqueta",       # censored / uncensored
        "tema",           # p. ej. smog, boxilai
        "categoria",      # categoría de Ng et al.
        "archivo",        # CSV de origen
        "tiene_zw",       # True si traía \u200b
        "longitud",       # caracteres de texto_zh
    ]].rename(columns={"texto": "texto_original"})

    corpus.to_csv(OUT, index=False, encoding="utf-8")

    print(f"Contradictorios eliminados (textos): {len(contradictorios)}")
    print(f"Corpus final: {len(corpus)} publicaciones")
    print(corpus.groupby(["tema", "etiqueta"]).size().unstack(fill_value=0))

if __name__ == "__main__":
    
    main()