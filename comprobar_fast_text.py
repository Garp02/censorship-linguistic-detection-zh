from representaciones import cargar, tokenizar
from vectores import PromedioPreentrenado

df = cargar()
t = PromedioPreentrenado().fit(df["texto_zh"])
print("Dimensión:", t.dim_, "| palabras cargadas:", len(t.wv_))

tokens = [tok for texto in df["texto_zh"] for tok in tokenizar(texto)]
cubiertos = sum(tok in t.wv_ for tok in tokens)
print("Tokens totales:", len(tokens))
print("Tokens con vector:", cubiertos, f"({cubiertos / len(tokens) * 100:.1f} %)")

X = t.transform(df["texto_zh"])
print("Matriz:", X.shape)