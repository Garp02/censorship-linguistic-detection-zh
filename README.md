# Censura en redes sociales chinas

Autor(es):

- Esteva Gallegos Carlos Fabián
- Munive Ramírez Ibrahim

## Descripción

Detección y análisis lingüístico de publicaciones censuradas en redes sociales chinas (Sina Weibo). Se trata de un problema de clasificación binaria (censurado / no censurado) acompañado de un análisis de los rasgos léxicos y gramaticales más discriminativos.

El corpus está en inglés. Las publicaciones o comentarios originales en chino se traducen automáticamente al inglés tentativamente con el modelo `Helsinki-NLP/opus-mt-zh-en`, disponible en Hugging Face bajo licencia CC-BY-4.0.

## Objetivos

- Evaluar qué tan bien distinguen los modelos TF-IDF, n-gramas, Naive Bayes y regresión logística frente a representaciones basadas en vectores de palabras (Word2Vec o FastText).

- Identificar los términos, n-gramas y categorías gramaticales (POS) asociados a cada clase, incluidos los eufemismos y las variantes de evasión.
- Discutir la validez de la etiqueta "censurado" y las limitaciones del enfoque.

## Preguntas de investigación

- **P1.** ¿Qué desempeño alcanzan los modelos clásicos en la detección de contenido censurado?

- **P2.** ¿Mejoran los vectores de palabras los resultados frente a las 
representaciones léxicas dispersas, sobre todo ante eufemismos y homófonos?

- **P3.** ¿Qué términos y categorías gramaticales distinguen a cada clase, y difieren entre subdominios?

## Datos

| Fuente | Contenido |
|---|---|
| Corpus de Ng et al. (2018) | Muestra pequeña para pruebas y comparación; 8 temas en CSV |

**Etiqueta de censura.** La etiqueta proviene de la plataforma (por ejemplo, "permission denied" en WeiboScope), no de anotación propia. Es un indicador indirecto y no una confirmación oficial de censura.

**Muestra.** Se traduce una muestra de publicaciones censuradas y una muestra aleatoria de no censuradas del mismo periodo. Las publicaciones borradas por causas no identificadas se excluyen.

**Traducción.** Se revisará a mano una muestra de traducciones, incluidas publicaciones con homófonos y con chino tradicional, para decidir si el modelo es adecuado.

**Dominio.** Las fuentes no traen etiqueta temática. El filtro de dominio político, económico y comercial se aplica con listas de términos en inglés y se valida con una muestra anotada por los dos integrantes (kappa de Cohen).

**Partición.** Cronológica, no aleatoria, para evitar fuga temporal.

## Limitaciones y consideraciones éticas

- La etiqueta de censura es una señal de la plataforma; una publicación puede desaparecer por spam, decisión del autor o moderación.

- Los datos de 2012 podrían no reflejar los criterios de censura actuales.

- La traducción automática puede borrar o alterar eufemismos y homófonos, y sus errores se propagan a los modelos. El modelo no fue entrenado con texto de redes sociales, por lo que su calidad en este dominio debe verificarse.

- Los resultados no se extienden a otros temas ni a otras plataformas.

- Los textos pertenecen a personas reales: los usuarios se anonimizan y no se publican identificadores.

- El sistema es un instrumento de análisis; no se propone como herramienta de filtrado o vigilancia.

## Referencias

- Bamman, D., O'Connor, B., & Smith, N. A. (2012). Censorship and deletion practices in Chinese social media. *First Monday*, 17(3).
- King, G., Pan, J., & Roberts, M. E. (2013). How censorship in China allows government criticism but silences collective expression. *American Political Science Review*, 107(2), 326–343.
- Ng, K. Y., Feldman, A., Peng, J., & Leberknight, C. (2018). Linguistic characteristics of censorable language on SinaWeibo. *Proceedings of the First Workshop on NLP for Internet Freedom*.
- Arefi, M. N., et al. (2019). Assessing post deletion in Sina Weibo: Multi-modal classification of hot topics. *Proceedings of the Workshop on NLP for Internet Freedom*.