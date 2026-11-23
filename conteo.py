import re
import os
import csv
import glob
import pandas as pd

from opencc import OpenCC

data = 'data_nlp4if_2018'
t2s = OpenCC('t2s')
cosas_raras = re.compile(r'[\u200b\u200c\u200d\ufeff\u00a0]')
re_url = re.compile(r'https?://\S+')
arroba = re.compile(r'@\S+')
chino = re.compile(r'[\u4e00-\u9fff]')
caracteres_minimos = 5


def cargar() -> pd.DataFrame:
    """Lee todos los csv y devuelve una fila por publicación.

    El tema y la etiqueta (censurado o no_censurado) se obtienen del nombre del archivo.
    Se omiten las líneas vacías y la cabecera 'Content'.
    """
    filas: list[pd.DataFrame] = []
    for ruta in sorted(glob.glob(os.path.join(data, '*.csv'))):

        nombre: str = os.path.basename(ruta)[:-4]

        if nombre.endswith('-uncensored'):

            tema, etiqueta = nombre[: -len('-uncensored')], 'no_censurado'

        elif nombre.endswith('-censored'):

            tema, etiqueta = nombre[: -len('-censored')], 'censurado'

        else:

            print('Archivo ignorado:', nombre)
            continue

        with open(ruta, encoding = 'utf-8-sig') as f:

            lineas = [l.strip() for l in f.read().splitlines()]

        lineas = [l for l in lineas if l and l != 'Content']
        filas.append(pd.DataFrame({'texto': lineas, 
                                   'tema': tema, 
                                   'etiqueta': etiqueta}))

    return pd.concat(filas, ignore_index = True)

def limpiar(t: str) -> str:
    """Quita caracteres invisibles, URLs y menciones (@), une comas repetidas
    y normaliza los espacios. Devuelve el texto limpio."""
    t = cosas_raras.sub('', t)
    t = re_url.sub(' ', t)
    t = arroba.sub(' ', t)
    t = re.sub(r',{2,}', '，', t)

    return re.sub(r'\s+', ' ', t).strip()

df: pd.DataFrame = cargar()
print("Filas crudas:", len(df))

df["texto_zh"] = df.texto.map(limpiar).map(t2s.convert)
df = df[df.texto_zh.map(lambda t: len(chino.findall(t)) >= caracteres_minimos)]
df = df.drop_duplicates(subset=["tema", "etiqueta", "texto_zh"]).reset_index(drop = True)

print('\nConteo tras limpieza:')
print(df.groupby(['tema', 'etiqueta']).size().unstack(fill_value = 0))
print('\nTotal:', len(df))