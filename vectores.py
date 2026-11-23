"""
Vectores de palabras preentrenados (FastText, chino) para texto_zh.

Descarga el archivo cc.zh.300.vec desde https://fasttext.cc/docs/en/crawl-vectors.html
y ponlo en la misma carpeta que este script. Cada documento se representa como
el promedio de los vectores de sus tokens.
"""
import numpy as np

from gensim.models import KeyedVectors
from representaciones import tokenizar
from sklearn.base import BaseEstimator 
from sklearn.base import TransformerMixin

ARCHIVO = "cc.zh.300.vec"
LIMITE = 500000  # palabras más frecuentes a cargar, para ahorrar memoria

class PromedioPreentrenado(BaseEstimator, TransformerMixin):
    """Promedia vectores preentrenados por documento. No aprende nada del corpus."""

    def __init__(self, archivo=ARCHIVO, limite=LIMITE):
        self.archivo = archivo
        self.limite = limite

    def fit(self, X, y=None):
        self.wv_ = KeyedVectors.load_word2vec_format(self.archivo, limit=self.limite)
        self.dim_ = self.wv_.vector_size

        return self

    def transform(self, X):
        salida = np.zeros((len(X), self.dim_))
        
        for i, texto in enumerate(X):
        
            vecs = [self.wv_[t] for t in tokenizar(texto) if t in self.wv_]
        
            if vecs: salida[i] = np.mean(vecs, axis=0)
        
        return salida