"""
Etapa 6: representaciones del texto chino (texto_zh) para los modelos.

Las representaciones se definen como constructores, no como objetos ya
ajustados, para que cada pliegue de validación cruzada aprenda su
vocabulario solo con sus datos de entrenamiento.
"""
import re

import jieba
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

jieba.setLogLevel(60)

HAN = re.compile(r"^[\u4e00-\u9fff]{2,}$")
CORPUS = "corpus_zh.csv"


def cargar(path=CORPUS):
    """Lee el corpus consolidado y verifica que el texto esté limpio."""
    df = pd.read_csv(path, dtype={"texto_zh": str, "etiqueta": str, "tema": str})
    if df["texto_zh"].str.contains("\u200b", regex=False).any():
        raise ValueError("texto_zh todavía contiene U+200B")
    return df


def tokenizar(texto):
    """Segmenta con jieba y conserva solo palabras de dos o más caracteres chinos."""
    return [t for t in jieba.lcut(texto) if HAN.match(t)]


def constructores():
    """Representaciones a comparar, sin ajustar."""
    return {
        "bow_palabras": lambda: CountVectorizer(
            tokenizer=tokenizar, token_pattern=None, lowercase=False, min_df=2
        ),
        "tfidf_palabras": lambda: TfidfVectorizer(
            tokenizer=tokenizar, token_pattern=None, lowercase=False, min_df=2
        ),
        "tfidf_palabras_bigramas": lambda: TfidfVectorizer(
            tokenizer=tokenizar, token_pattern=None, lowercase=False,
            ngram_range=(1, 2), min_df=2
        ),
        "tfidf_caracteres_1_3": lambda: TfidfVectorizer(
            analyzer="char", ngram_range=(1, 3), min_df=2
        ),
    }


def resumen(df):
    """Dimensión y densidad de cada representación ajustada sobre todo el corpus."""
    filas = []
    for nombre, nuevo in constructores().items():
        vec = nuevo()
        X = vec.fit_transform(df["texto_zh"])
        filas.append({
            "representacion": nombre,
            "documentos": X.shape[0],
            "rasgos": X.shape[1],
            "densidad_%": round(X.nnz / (X.shape[0] * X.shape[1]) * 100, 3),
        })
    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = cargar()
    print(f"Corpus: {len(df)} publicaciones")
    print(resumen(df).to_string(index=False))