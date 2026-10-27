# Diccionario de datos · Variante A · `a_casos.csv`

Todos los casos son **sintéticos**: fueron redactados para esta plantilla, inspirados en patrones frecuentes de desinformación. No contienen datos personales ni mencionan a candidatos, partidos o autoridades en ejercicio.

| Campo | Significado | Valores posibles |
|---|---|---|
| `id_caso` | Identificador único del caso | A01, A02, … |
| `tema` | Tema general del contenido | salud, estafas, emergencias, clima, consumo, tecnologia, educacion, barrio, cultura |
| `formato` | Cómo circuló el contenido | texto, audio transcrito, imagen descrita, video descrito |
| `texto_viral` | El contenido tal como circularía | Texto libre |
| `afirmacion_central` | La idea principal que se puede (o no) verificar | Texto libre |
| `chequeable` | Si la afirmación se puede verificar con datos | si, no |
| `categoria_inchequeable` | Por qué no se puede verificar (solo si `chequeable` = no) | opinion, fuente_en_off, grandes_preguntas, dato_obvio, futuro, negacion, delito_sin_sentencia |
| `calificacion` | Resultado de la verificación | Verdadero, Engañoso, Falso, Sin evidencia, No chequeable |
| `explicacion` | Por qué tiene esa calificación | Texto libre |
| `senales_alerta` | Pistas en el mensaje que deberían generar duda | Texto libre |
| `fuente_url` | Fuente oficial o herramienta para verificar | URL o vacío |
| `origen_dato` | Origen del caso | sintético |

**Origen de las categorías de lo no chequeable:** adaptadas de la metodología pública de Fast Check (fastcheck.cl).

**Para agregar casos:** añadan una fila nueva respetando los valores posibles de cada columna y un `id_caso` que no se repita.
