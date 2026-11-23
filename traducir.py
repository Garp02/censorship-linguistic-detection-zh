"""
Traduce texto_zh de corpus_zh.csv al inglés con Helsinki-NLP/opus-mt-zh-en.

Salida: corpus_en.csv, con todas las columnas originales y texto_en.
Guarda avance parcial en progreso_en.csv para poder reanudar.
"""
import os
import time

import pandas as pd
import torch

ENTRADA = "corpus_zh.csv"
SALIDA = "corpus_en.csv"
PARCIAL = "progreso_en.csv"
MODELO = "Helsinki-NLP/opus-mt-zh-en"
LOTE = 16
MAX_NUEVOS = 400


def crear_traductor(modelo):
    """Carga el modelo y devuelve una función que traduce un lote de textos."""
    from transformers import MarianMTModel, MarianTokenizer

    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print("Dispositivo:", dispositivo)

    tokenizer = MarianTokenizer.from_pretrained(modelo)
    model = MarianMTModel.from_pretrained(modelo).to(dispositivo).eval()

    def traductor(bloque):
        entrada = tokenizer(bloque, return_tensors="pt", padding=True,
                            truncation=True, max_length=512).to(dispositivo)
        with torch.inference_mode():
            salida = model.generate(**entrada, num_beams=1, do_sample=False,
                                    max_new_tokens=MAX_NUEVOS)
        return tokenizer.batch_decode(salida, skip_special_tokens=True)

    return traductor


def main():
    df = pd.read_csv(ENTRADA, dtype=str, keep_default_na=False)
    traductor = crear_traductor(MODELO)

    # Textos ordenados por longitud para reducir relleno
    orden = df["texto_zh"].str.len().sort_values().index.tolist()
    textos = df.loc[orden, "texto_zh"].tolist()

    resultados = []
    inicio = time.time()
    for i in range(0, len(textos), LOTE):
        resultados.extend(traductor(textos[i:i + LOTE]))
        hechos = len(resultados)
        transcurrido = time.time() - inicio
        print(f"{hechos}/{len(textos)} | {transcurrido / 60:.1f} min")
        if hechos % (LOTE * 10) == 0:
            pd.DataFrame({"idx": orden[:hechos], "texto_en": resultados}).to_csv(PARCIAL, index=False)

    df.loc[orden, "texto_en"] = resultados
    df.to_csv(SALIDA, index=False, encoding="utf-8")
    print(f"Guardado: {SALIDA} ({len(df)} filas)")


if __name__ == "__main__":
    main()