"""
Une los 16 CSV de Ng et al. (2018) en un solo corpus depurado.

- Carga sin encabezado (salvo fifty-cent-uncensored.csv, que trae 'Content').
- Etiqueta y tema salen del nombre del archivo: <tema>-<etiqueta>.csv.
- Quita \u200b y espacios de los extremos.
- Elimina textos vacíos.
- Elimina textos que aparecen con etiquetas contradictorias.
- Conserva una sola copia de cada texto duplicado.
- Agrega la representación en pinyin (tono numérico) de cada texto.
"""
import numpy as np
import pandas as pd

from pathlib import Path
from pypinyin import pinyin, Style

data = Path('data_nlp4if_2018')
salida = Path('corpus_zh.csv')
ZW = '\u200b'

# Categoría que Ng et al. (2018) asignan a cada tema.
# melamine y poisonous-milk-powder forman el tema 'milk scandal' del artículo.
categoria = {
    'boxilai': 'Bo Xilai',
    'fifty-cent': 'censura y propaganda en internet',
    'censored': 'censura y propaganda en internet',
    'ditch-oil': 'contaminación e inocuidad alimentaria',
    'melamine': 'contaminación e inocuidad alimentaria',
    'poisonous-milk-powder': 'contaminación e inocuidad alimentaria',
    'smog': 'contaminación e inocuidad alimentaria',
    'kindergarten': 'abuso en guarderías'}

def cargar(path: Path) -> pd.DataFrame:
    """Lee un CSV de Ng et al. y devuelve texto, tema, etiqueta y archivo."""
    df = pd.read_csv(path, header = None, names = ['texto'], dtype = str,  keep_default_na = False)

    # Solo fifty-cent-uncensored.csv trae encabezado
    if df['texto'].iloc[0].strip() == 'Content': df = df.iloc[1:]

    # 'fifty-cent-uncensored' -> tema: 'fifty-cent', etiqueta: 'uncensored'
    tema, etiqueta = path.stem.rsplit('-', 1)
    return df.assign(tema = tema, etiqueta = etiqueta, archivo = path.name)

def a_pinyin(texto: str) -> str:
    """Convierte cada carácter chino en su sílaba con tono."""
    silabas = pinyin(texto, style = Style.TONE3, heteronym = True, errors = 'default')
    return ' '.join(s[0] for s in silabas)

if __name__ == '__main__':

    archivos = sorted(data.glob('*.csv'))

    if not archivos:

        raise FileNotFoundError(f'No hay CSV en {data.resolve()}')

    print(f'Archivos encontrados: {len(archivos)}')

    df = pd.concat([cargar(f) for f in archivos], ignore_index = True)
    print('Filas cargadas:', len(df))

    # Limpieza
    df['tiene_zw'] = df['texto'].str.contains(ZW, regex = False)
    df['texto_zh'] = df['texto'].str.replace(ZW, '', regex = False).str.strip()

    # Textos vacíos
    df = df[df['texto_zh'].str.len() > 0].copy()

    # Textos con etiquetas contradictorias: se eliminan todas sus apariciones
    n_lab = df.groupby('texto_zh')['etiqueta'].nunique()
    contradictorios = set(n_lab[n_lab > 1].index)
    df = df[~df['texto_zh'].isin(contradictorios)]

    # Duplicados
    df = df.drop_duplicates('texto_zh').reset_index(drop = True)

    # Columnas finales
    df['censured'] = (df['etiqueta'] == 'censored').astype(int) # 1 = censurado
    df['categoria'] = df['tema'].map(categoria)
    df['longitud'] = df['texto_zh'].str.len()

    # Pinyin con tono numérico
    df['pinyin'] = df['texto_zh'].apply(a_pinyin)

    corpus = df[[
        'texto',
        'texto_zh', # limpio: sin \u200b
        'pinyin', # sílabas con tono
        'censured',
        'tema', # ej. smog, boxilai
        'categoria', # categoría de Ng et al.
        'longitud' # caracteres de texto_zh
    ]].rename(columns = {'texto': 'texto_original'})

    corpus.to_csv(salida, index = False, encoding = 'utf-8')

    print(f'Textos contradictorios eliminados: {len(contradictorios)}')
    print(f'Corpus final: {len(corpus)} publicaciones')
    print(corpus.groupby(['tema', 'categoria']).size().unstack(fill_value = 0))