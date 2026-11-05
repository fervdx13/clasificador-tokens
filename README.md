# ⚡ SYNTH-LEX | Analizador Léxico & Clasificador de Tokens

> **Proyecto Académico de Compiladores**  
> Interface Web Interactiva (Estilo Vaporwave / Cyberpunk Neon) y Motor de Análisis Léxico en Python y JavaScript.

---

## 👨‍🎓 Información del Autor

* **Alumno:** Fernando Vidal Delgado
* **Número de Control:** 2320905
* **Materia:** Lenguajes y Autómatas / Compiladores
* **Institución:** Instituto Tecnológico de Pachuca
* **Demostración Web en Vivo:** [https://fervdx13.github.io/clasificador-tokens/](https://fervdx13.github.io/clasificador-tokens/)

---

## 🔮 Características Principales

* **Reconocimiento Sintáctico de 10 Categorías:** Palabras Reservadas, Identificadores, Números Enteros, Números Decimales, Cadenas de Texto, Operadores Aritméticos, Operadores de Comparación, Operadores de Asignación, Operadores Lógicos, Delimitadores y Comentarios.
* **Manejo Explicito de Errores Léxicos:** Detección de símbolos no pertenecientes al alfabeto (`@`, `$`), identificadores con inicio numérico (`99variable`) y cadenas sin cerrar, reportando la ubicación exacta por línea y columna (`LXX:CY`).
* **Motor Dual:**
  * **Client-Side (JavaScript):** Ejecución 100% estática en el navegador sin dependencias de servidor.
  * **CLI / Test Suite (Python):** Script original `clasificador_tokens.py` con pruebas unitarias integradas.
* **Herramientas de Análisis Interactivo:**
  * Evaluador de Lexema Único en tiempo real.
  * Analizador de Código Completo editable con atajos de teclado (`Ctrl + Enter`).
  * Modal interactivo con la **Especificación Gramatical Oficial ($RegEx$)**.
  * Gráfica de **Distribución Porcentual** de categorías.
  * Exportación de reportes en formatos **CSV** y **JSON**.

---

## 📊 Especificación Gramatical ($RegEx$)

| Categoría | Expresión Regular ($RegEx$) | Color Neón | Descripción | Ejemplos |
| :--- | :--- | :--- | :--- | :--- |
| **Palabra Reservada** | `if\|else\|while\|for\|int\|float\|string...` | `#7B2CBF` | Palabras clave del lenguaje | `while`, `int`, `return` |
| **Identificador** | `^[a-zA-Z_]\w*$` | `#FFE600` | Nombres de variables y funciones | `contador_2`, `pi_const` |
| **Número Entero** | `^\d+$` | `#F15BB5` | Literales numéricas enteras | `100`, `42` |
| **Número Decimal** | `^\d+\.\d+([eE][+-]?\d+)?$` | `#F15BB5` | Literales en coma flotante | `3.14159`, `0.001` |
| **Cadena de Texto** | `^("(?:\\\.\|[^"\\])*"\|'(?:\\\.\|[^\'\\])*')$` | `#00F5D4` | Literales de texto entre comillas | `"Hola Mundo"` |
| **Operador Lógico** | `^(&&\|\|\|!)$` | `#00F5D4` | Operaciones booleanas | `&&`, `\|\|`, `!` |
| **Op. Comparación** | `^(==\|!=\|<=\|>=\|<\|>)$` | `#9B5DE5` | Comparaciones relacionales | `>=`, `!=` |
| **Op. Asignación** | `^(\+==\|-=\|\*=|\/=\|%=\|=)$` | `#FEE440` | Asignación de valores | `+=`, `=` |
| **Op. Aritmético** | `^(\+\+\|--\|\+\|-\|\*\|\/\|%)$` | `#00BBF9` | Operaciones matemáticas | `++`, `+`, `/` |
| **Delimitador** | `^[;,\(\)\{\}\[\]:\.]$` | `#A29BFE` | Símbolos de estructura | `;`, `(`, `)` |
| **Comentario** | `^(\/\*[\s\S]*?\*\/\|\/\/[^\n]*\|#[^\n]*)$` | `#5C677D` | Texto explicativo omitido | `// Comentario` |
| **Error Léxico** | *Patrón no reconocido* | `#FF0055` | Secuencias o símbolos inválidos | `@invalido`, `99variable` |

---

## 🚀 Estructura del Repositorio

```text
clasificador-tokens/
├── index.html               # Interfaz Web interactiva principal (GitHub Pages)
├── clasificador_tokens.html # Copia de respaldo sincronizada
├── clasificador_tokens.py   # Motor léxico en Python (Script CLI / Test suite)
├── casos_de_prueba.txt      # Archivo de pruebas estáticas
└── README.md                # Documentación oficial del proyecto