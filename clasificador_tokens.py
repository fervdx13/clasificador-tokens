#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# *******************************************************************************
# * Nombre del alumno: Fernando Vidal Delgado
# * Número de control: 2320905
# * Materia: Lenguajes y Autómatas / Compiladores
# * Proyecto: Clasificador de Tokens (Analizador Léxico)
# * Archivo: clasificador_tokens.py
# * Estilo Visual / Paleta de Colores: Vaporwave / Cyberpunk Neon
# *******************************************************************************

"""
================================================================================
SYNTH-LEX | ANALIZADOR LÉXICO (CLASIFICADOR DE TOKENS)
Paleta Visual: Vaporwave / Cyberpunk Neon
================================================================================

Este módulo implementa un analizador léxico completo, robusto y eficiente
diseñado para la materia de Lenguajes y Autómatas / Compiladores.

Capacidades principales:
1. Clasificación de lexemas individuales mediante expresiones regulares optimizadas.
2. Tokenización y análisis léxico de flujos completos de código fuente con rastreo
   de número de línea, columna y recuperación de errores sin interrupción.
3. Clasificación en 10 categorías formales con manejo específico de errores léxicos.
4. Doble interfaz visual bajo la estética estricta Vaporwave / Cyberpunk Neon:
   - CLI Neón estilizada con soporte TrueColor (24 bits) y modo interactivo REPL.
   - GUI moderna en Tkinter (si se encuentra disponible en el entorno).
   - Generador de dashboard interactivo en HTML5/CSS3 Cyberpunk.
5. Suite de pruebas unitarias automatizada para verificación exhaustiva.
"""

import sys
import os
import re
import json
import argparse
import webbrowser
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Any, Optional

# Forzar codificación UTF-8 en consolas Windows para caracteres Neón y cajas Unicode
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ==============================================================================
# SECCIÓN 1: PALETA DE COLORES VAPORWAVE / CYBERPUNK NEON
# ==============================================================================

class PaletaVaporwave:
    """
    Especificación de la paleta cromática Vaporwave / Cyberpunk Neon.
    Contiene valores hexadecimales, componentes RGB y secuencias ANSI TrueColor.
    """
    # Colores Base de la Interfaz
    FONDO_PRINCIPAL      = "#0F0C1B"  # Morado Noche Profundo
    CONTENEDOR_TARJETA   = "#1A1528"  # Violeta Oscuro
    TEXTO_PRINCIPAL      = "#E0E6ED"  # Blanco Platino
    COLOR_PRIMARIO       = "#FF007F"  # Rosa Neón / Magenta
    COLOR_SECUNDARIO     = "#00F5D4"  # Turquesa Neón

    # Colores de Tokens según especificación obligatoria
    TOKEN_RESERVADA      = "#7B2CBF"  # Violeta Eléctrico (Palabras Reservadas)
    TOKEN_CADENA         = "#00F5D4"  # Turquesa (Cadenas / Strings)
    TOKEN_NUMERO         = "#F15BB5"  # Fucsia (Números / Floats)
    TOKEN_ERROR          = "#FF0055"  # Rojo Neón (Errores Léxicos)

    # Colores Neón Armonizados para categorías complementarias
    TOKEN_IDENTIFICADOR  = "#FFE600"  # Amarillo Neón (Identificadores)
    TOKEN_OP_ARITMETICO  = "#00BBF9"  # Azul Eléctrico (Operadores Aritméticos)
    TOKEN_OP_COMPARACION = "#9B5DE5"  # Púrpura Neón (Operadores de Comparación)
    TOKEN_OP_LOGICO      = "#9B5DE5"  # Púrpura / Turquesa Neón (Operadores Lógicos)
    TOKEN_OP_ASIGNACION  = "#FEE440"  # Oro Neón (Operadores de Asignación)
    TOKEN_DELIMITADOR    = "#A29BFE"  # Lavanda Neón (Delimitadores)
    TOKEN_COMENTARIO     = "#5C677D"  # Gris Neón Atenuado (Comentarios)

    @staticmethod
    def hex_a_rgb(hex_code: str) -> Tuple[int, int, int]:
        """Convierte una cadena hexadecimal '#RRGGBB' en tupla (R, G, B)."""
        hex_code = hex_code.lstrip("#")
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

    @classmethod
    def ansi_fg(cls, hex_code: str) -> str:
        """Genera secuencia ANSI de 24 bits para color de texto (TrueColor)."""
        r, g, b = cls.hex_a_rgb(hex_code)
        return f"\033[38;2;{r};{g};{b}m"

    @classmethod
    def ansi_bg(cls, hex_code: str) -> str:
        """Genera secuencia ANSI de 24 bits para color de fondo (TrueColor)."""
        r, g, b = cls.hex_a_rgb(hex_code)
        return f"\033[48;2;{r};{g};{b}m"

    ANSI_RESET = "\033[0m"
    ANSI_BOLD  = "\033[1m"
    ANSI_DIM   = "\033[2m"


# ==============================================================================
# SECCIÓN 2: DEFINICIÓN DE CATEGORÍAS Y ESTRUCTURAS DE DATOS
# ==============================================================================

class CategoriaToken(str, Enum):
    """Enumeración formal de las categorías de tokens reconocidas por el analizador."""
    PALABRA_RESERVADA = "Palabra Reservada"
    IDENTIFICADOR     = "Identificador"
    NUMERO_ENTERO     = "Número Entero"
    NUMERO_DECIMAL    = "Número Decimal"
    CADENA            = "Cadena de Texto"
    OP_ARITMETICO     = "Operador Aritmético"
    OP_COMPARACION    = "Operador de Comparación"
    OP_ASIGNACION     = "Operador de Asignación"
    OP_LOGICO         = "Operador Lógico"
    DELIMITADOR       = "Delimitador"
    COMENTARIO        = "Comentario"
    ERROR_LEXICO      = "Error Léxico / No Reconocido"


@dataclass
class Token:
    """
    Representa una unidad léxica detectada en el código fuente.
    
    Atributos:
        categoria: Categoría formal del token (Enum CategoriaToken).
        lexema: Secuencia exacta de caracteres que coinciden con el patrón.
        linea: Número de línea (1-indexado).
        columna: Número de columna (1-indexado).
        color_hex: Color de la paleta Vaporwave asignado para su visualización.
        descripcion: Detalle informativo de la regla que reconoció al token.
    """
    categoria: CategoriaToken
    lexema: str
    linea: int = 1
    columna: int = 1
    color_hex: str = PaletaVaporwave.TEXTO_PRINCIPAL
    descripcion: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el token a un diccionario legible."""
        return {
            "categoria": self.categoria.value,
            "lexema": self.lexema,
            "linea": self.linea,
            "columna": self.columna,
            "color_hex": self.color_hex,
            "descripcion": self.descripcion,
            "es_error": self.categoria == CategoriaToken.ERROR_LEXICO
        }


# ==============================================================================
# SECCIÓN 3: MOTOR DEL ANALIZADOR LÉXICO
# ==============================================================================

class AnalizadorLexico:
    """
    Motor del analizador léxico basado en expresiones regulares y teoría de autómatas.
    Reconoce tokens eficientemente en tiempo lineal O(N) sin estructuras if-else redundantes.
    """

    # Conjunto canónico de palabras reservadas en lenguajes estructurados / de compiladores
    PALABRAS_RESERVADAS = {
        "if", "else", "while", "for", "do", "return", "int", "float",
        "double", "char", "void", "bool", "string", "true", "false",
        "break", "continue", "switch", "case", "default", "struct",
        "class", "public", "private", "protected", "static", "const",
        "main", "print", "println", "input", "import", "def", "null"
    }

    # Asignación de colores por categoría (estricta paleta Vaporwave / Cyberpunk)
    MAPA_COLORES: Dict[CategoriaToken, str] = {
        CategoriaToken.PALABRA_RESERVADA: PaletaVaporwave.TOKEN_RESERVADA,
        CategoriaToken.CADENA:            PaletaVaporwave.TOKEN_CADENA,
        CategoriaToken.NUMERO_ENTERO:     PaletaVaporwave.TOKEN_NUMERO,
        CategoriaToken.NUMERO_DECIMAL:    PaletaVaporwave.TOKEN_NUMERO,
        CategoriaToken.ERROR_LEXICO:      PaletaVaporwave.TOKEN_ERROR,
        CategoriaToken.IDENTIFICADOR:     PaletaVaporwave.TOKEN_IDENTIFICADOR,
        CategoriaToken.OP_ARITMETICO:     PaletaVaporwave.TOKEN_OP_ARITMETICO,
        CategoriaToken.OP_COMPARACION:    PaletaVaporwave.TOKEN_OP_COMPARACION,
        CategoriaToken.OP_ASIGNACION:     PaletaVaporwave.TOKEN_OP_ASIGNACION,
        CategoriaToken.OP_LOGICO:         PaletaVaporwave.TOKEN_OP_LOGICO,
        CategoriaToken.DELIMITADOR:       PaletaVaporwave.TOKEN_DELIMITADOR,
        CategoriaToken.COMENTARIO:        PaletaVaporwave.TOKEN_COMENTARIO,
    }

    # --------------------------------------------------------------------------
    # Reglas para clasificar un lexema individual completo (fullmatch)
    # --------------------------------------------------------------------------
    REGLAS_LEXEMA_INDIVIDUAL: List[Tuple[CategoriaToken, str, str]] = [
        # (Categoria, Expresión Regular Anclada, Descripción)
        (
            CategoriaToken.COMENTARIO,
            r"^(//.*|#.*|/\*[\s\S]*\*/)$",
            "Comentario (línea o bloque)"
        ),
        (
            CategoriaToken.CADENA,
            r'^("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')$',
            "Cadena de texto delimitada por comillas"
        ),
        (
            CategoriaToken.NUMERO_DECIMAL,
            r"^\d+\.\d+([eE][+-]?\d+)?$",
            "Número de punto flotante / decimal"
        ),
        (
            CategoriaToken.NUMERO_ENTERO,
            r"^\d+$",
            "Número entero sin signo"
        ),
        (
            CategoriaToken.OP_LOGICO,
            r"^(&&|\|\||!|&|\|)$",
            "Operador lógico booleano"
        ),
        (
            CategoriaToken.OP_COMPARACION,
            r"^(==|!=|<=|>=|<|>)$",
            "Operador relacional de comparación"
        ),
        (
            CategoriaToken.OP_ASIGNACION,
            r"^(\+=|-=|\*=|/=|%=|=)$",
            "Operador de asignación (simple o compuesto)"
        ),
        (
            CategoriaToken.OP_ARITMETICO,
            r"^(\+\+|--|\+|-|\*|/|%)$",
            "Operador aritmético"
        ),
        (
            CategoriaToken.DELIMITADOR,
            r"^[;,\(\)\{\}\[\]:\.]$",
            "Símbolo delimitador sintáctico"
        ),
        (
            CategoriaToken.IDENTIFICADOR,
            r"^[a-zA-Z_]\w*$",
            "Identificador o palabra reservada"
        ),
    ]

    # --------------------------------------------------------------------------
    # Reglas para el Scanner de flujo continuo (Tokenizador)
    # --------------------------------------------------------------------------
    REGLAS_SCANNER: List[Tuple[str, str]] = [
        ("COMENTARIO",             r"/\*[\s\S]*?\*/|//[^\n]*|#[^\n]*"),
        ("CADENA",                 r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''),
        ("CADENA_SIN_CERRAR",      r'"(?:\\.|[^"\\\n])*|\'(?:\\.|[^\'\\\n])*'),
        ("NUMERO_DECIMAL",         r"\b\d+\.\d+([eE][+-]?\d+)?\b"),
        ("IDENTIFICADOR_INVALIDO", r"\b\d+[a-zA-Z_]\w*\b"),
        ("NUMERO_ENTERO",          r"\b\d+\b"),
        ("OP_LOGICO",              r"&&|\|\||!(?!=)"),
        ("OP_COMPARACION",         r"==|!=|<=|>=|<|>"),
        ("OP_ASIGNACION",          r"\+=|-=|\*=|/=|%=|="),
        ("OP_ARITMETICO",          r"\+\+|--|\+|-|\*|/|%"),
        ("DELIMITADOR",            r"[;,\(\)\{\}\[\]:\.]"),
        ("IDENTIFICADOR",          r"\b[a-zA-Z_]\w*\b"),
        ("NUEVALINEA",             r"\n"),
        ("ESPACIO",                r"[^\S\n]+"),
        ("ERROR_DESCONOCIDO",      r"."),
    ]

    def __init__(self):
        """Compila las expresiones regulares maestras una sola vez para máxima eficiencia."""
        patron_maestro = "|".join(f"(?P<{nombre}>{patron})" for nombre, patron in self.REGLAS_SCANNER)
        self._scanner_compilado = re.compile(patron_maestro)

    def clasificar_lexema(self, lexema: str, linea: int = 1, columna: int = 1) -> Token:
        """
        Recibe un lexema individual aislado y determina su categoría correspondiente.
        No utiliza condiciones individuales por caso; evalúa reglas estructuradas con `re`.
        """
        lexema_limpio = lexema.strip()

        if not lexema_limpio:
            return Token(
                categoria=CategoriaToken.ERROR_LEXICO,
                lexema=lexema,
                linea=linea,
                columna=columna,
                color_hex=self.MAPA_COLORES[CategoriaToken.ERROR_LEXICO],
                descripcion="Lexema vacío o compuesto solo por espacios en blanco"
            )

        # Evaluación sobre la lista estructurada de reglas
        for cat_candidata, patron, desc in self.REGLAS_LEXEMA_INDIVIDUAL:
            if re.match(patron, lexema_limpio):
                # Distinción entre Palabra Reservada e Identificador
                if cat_candidata == CategoriaToken.IDENTIFICADOR:
                    if lexema_limpio in self.PALABRAS_RESERVADAS:
                        return Token(
                            categoria=CategoriaToken.PALABRA_RESERVADA,
                            lexema=lexema_limpio,
                            linea=linea,
                            columna=columna,
                            color_hex=self.MAPA_COLORES[CategoriaToken.PALABRA_RESERVADA],
                            descripcion=f"Palabra clave reservada del lenguaje ({lexema_limpio})"
                        )
                    else:
                        return Token(
                            categoria=CategoriaToken.IDENTIFICADOR,
                            lexema=lexema_limpio,
                            linea=linea,
                            columna=columna,
                            color_hex=self.MAPA_COLORES[CategoriaToken.IDENTIFICADOR],
                            descripcion=f"Identificador válido de variable o función ({lexema_limpio})"
                        )
                # Demás categorías coincidentes
                return Token(
                    categoria=cat_candidata,
                    lexema=lexema_limpio,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[cat_candidata],
                    descripcion=desc
                )

        # Si ninguna regla estructurada coincidió -> Error Léxico
        return Token(
            categoria=CategoriaToken.ERROR_LEXICO,
            lexema=lexema_limpio,
            linea=linea,
            columna=columna,
            color_hex=self.MAPA_COLORES[CategoriaToken.ERROR_LEXICO],
            descripcion=f"Error léxico: El patrón '{lexema_limpio}' no pertenece al alfabeto ni a la sintaxis del lenguaje"
        )

    def analizar_codigo(self, codigo_fuente: str, incluir_comentarios: bool = True) -> List[Token]:
        """
        Analiza un texto o archivo de código fuente completo.
        Devuelve la lista ordenada de tokens reconocidos con sus posiciones (línea, columna).
        """
        tokens: List[Token] = []
        linea = 1
        columna_inicio_linea = 0

        for match in self._scanner_compilado.finditer(codigo_fuente):
            tipo = match.lastgroup
            lexema = match.group(tipo)
            inicio = match.start()
            columna = inicio - columna_inicio_linea + 1

            if tipo == "NUEVALINEA":
                linea += 1
                columna_inicio_linea = match.end()
                continue

            elif tipo == "ESPACIO":
                continue

            elif tipo == "COMENTARIO":
                if incluir_comentarios:
                    tokens.append(Token(
                        categoria=CategoriaToken.COMENTARIO,
                        lexema=lexema,
                        linea=linea,
                        columna=columna,
                        color_hex=self.MAPA_COLORES[CategoriaToken.COMENTARIO],
                        descripcion="Comentario explicativo (ignorado en fases posteriores)"
                    ))
                saltos = lexema.count("\n")
                if saltos > 0:
                    linea += saltos
                    ultimo_salto = lexema.rfind("\n")
                    columna_inicio_linea = match.start() + ultimo_salto + 1

            elif tipo == "CADENA":
                tokens.append(Token(
                    categoria=CategoriaToken.CADENA,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.CADENA],
                    descripcion="Literal de cadena de texto entre comillas"
                ))

            elif tipo == "CADENA_SIN_CERRAR":
                tokens.append(Token(
                    categoria=CategoriaToken.ERROR_LEXICO,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.ERROR_LEXICO],
                    descripcion="Error léxico: Cadena de texto abierta sin comilla de cierre en la línea"
                ))

            elif tipo == "NUMERO_DECIMAL":
                tokens.append(Token(
                    categoria=CategoriaToken.NUMERO_DECIMAL,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.NUMERO_DECIMAL],
                    descripcion="Constante numérica de punto flotante"
                ))

            elif tipo == "NUMERO_ENTERO":
                tokens.append(Token(
                    categoria=CategoriaToken.NUMERO_ENTERO,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.NUMERO_ENTERO],
                    descripcion="Constante numérica entera"
                ))

            elif tipo == "IDENTIFICADOR_INVALIDO":
                tokens.append(Token(
                    categoria=CategoriaToken.ERROR_LEXICO,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.ERROR_LEXICO],
                    descripcion=f"Error léxico: Identificador inválido '{lexema}'. No puede iniciar con dígito"
                ))

            elif tipo == "OP_LOGICO":
                tokens.append(Token(
                    categoria=CategoriaToken.OP_LOGICO,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.OP_LOGICO],
                    descripcion="Operador lógico booleano"
                ))

            elif tipo == "OP_COMPARACION":
                tokens.append(Token(
                    categoria=CategoriaToken.OP_COMPARACION,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.OP_COMPARACION],
                    descripcion="Operador relacional de comparación"
                ))

            elif tipo == "OP_ASIGNACION":
                tokens.append(Token(
                    categoria=CategoriaToken.OP_ASIGNACION,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.OP_ASIGNACION],
                    descripcion="Operador de asignación (simple o aritmético)"
                ))

            elif tipo == "OP_ARITMETICO":
                tokens.append(Token(
                    categoria=CategoriaToken.OP_ARITMETICO,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.OP_ARITMETICO],
                    descripcion="Operador aritmético binario o unario"
                ))

            elif tipo == "DELIMITADOR":
                tokens.append(Token(
                    categoria=CategoriaToken.DELIMITADOR,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.DELIMITADOR],
                    descripcion="Símbolo delimitador / separador sintáctico"
                ))

            elif tipo == "IDENTIFICADOR":
                if lexema in self.PALABRAS_RESERVADAS:
                    tokens.append(Token(
                        categoria=CategoriaToken.PALABRA_RESERVADA,
                        lexema=lexema,
                        linea=linea,
                        columna=columna,
                        color_hex=self.MAPA_COLORES[CategoriaToken.PALABRA_RESERVADA],
                        descripcion=f"Palabra clave reservada del lenguaje ({lexema})"
                    ))
                else:
                    tokens.append(Token(
                        categoria=CategoriaToken.IDENTIFICADOR,
                        lexema=lexema,
                        linea=linea,
                        columna=columna,
                        color_hex=self.MAPA_COLORES[CategoriaToken.IDENTIFICADOR],
                        descripcion="Identificador de usuario (variable, función, clase)"
                    ))

            elif tipo == "ERROR_DESCONOCIDO":
                tokens.append(Token(
                    categoria=CategoriaToken.ERROR_LEXICO,
                    lexema=lexema,
                    linea=linea,
                    columna=columna,
                    color_hex=self.MAPA_COLORES[CategoriaToken.ERROR_LEXICO],
                    descripcion=f"Error léxico: Carácter no permitido '{lexema}' (Código ASCII: {ord(lexema)})"
                ))

        return tokens

    @staticmethod
    def obtener_estadisticas(tokens: List[Token]) -> Dict[str, Any]:
        """Calcula métricas globales de la sesión de análisis."""
        total = len(tokens)
        errores = sum(1 for t in tokens if t.categoria == CategoriaToken.ERROR_LEXICO)
        validos = total - errores
        conteo_categorias: Dict[str, int] = {}

        for t in tokens:
            cat = t.categoria.value
            conteo_categorias[cat] = conteo_categorias.get(cat, 0) + 1

        tasa_validez = (validos / total * 100) if total > 0 else 100.0

        return {
            "total_tokens": total,
            "tokens_validos": validos,
            "errores_lexicos": errores,
            "tasa_validez": round(tasa_validez, 2),
            "desglose": conteo_categorias
        }


# ==============================================================================
# SECCIÓN 4: INTERFAZ VISUAL CLI CYBERPUNK NEON (TrueColor)
# ==============================================================================

class InterfazCyberpunkCLI:
    """Renderiza la salida de consola con la paleta estricta Vaporwave / Cyberpunk Neon."""

    P = PaletaVaporwave

    @classmethod
    def banner(cls) -> str:
        """Genera el encabezado ASCII Art estilizado con metadatos del estudiante."""
        magenta = cls.P.ansi_fg(cls.P.COLOR_PRIMARIO)
        turquesa = cls.P.ansi_fg(cls.P.COLOR_SECUNDARIO)
        blanco = cls.P.ansi_fg(cls.P.TEXTO_PRINCIPAL)
        reset = cls.P.ANSI_RESET
        bold = cls.P.ANSI_BOLD

        return f"""
{magenta}{bold}███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗    ██╗     ███████╗██╗  ██╗
██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝██║  ██║    ██║     ██╔════╝╚██╗██╔╝
███████╗ ╚████╔╝ ██╔██╗ ██║   ██║   ███████║    ██║     █████╗   ╚███╔╝ 
╚════██║  ╚██╔╝  ██║╚██╗██║   ██║   ██╔══██║    ██║     ██╔══╝   ██╔██╗ 
███████║   ██║   ██║ ╚████║   ██║   ██║  ██║    ███████╗███████╗██╔╝ ██╗
╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝    ╚══════╝╚══════╝╚═╝  ╚═╝{reset}
{turquesa}┌────────────────────────────────────────────────────────────────────────┐
│  {bold}PROYECTO: CLASIFICADOR DE TOKENS (ANALIZADOR LÉXICO){reset}{turquesa}                 │
│  {blanco}Alumno: {bold}Fernando Vidal Delgado{reset}{turquesa}   │  No. Control: {bold}2320905{reset}{turquesa}               │
│  {blanco}Materia: {bold}Lenguajes y Autómatas / Compiladores{reset}{turquesa}                            │
│  {blanco}Estilo Visual: {magenta}Vaporwave / Cyberpunk Neon{reset}{turquesa}                             │
└────────────────────────────────────────────────────────────────────────┘{reset}
"""

    @classmethod
    def imprimir_tabla_tokens(cls, tokens: List[Token]) -> None:
        """Imprime una tabla de tokens con formato neón y badges coloreados."""
        if not tokens:
            print(f"{cls.P.ansi_fg(cls.P.TOKEN_ERROR)}[!] No se encontraron tokens para mostrar.{cls.P.ANSI_RESET}")
            return

        magenta = cls.P.ansi_fg(cls.P.COLOR_PRIMARIO)
        turquesa = cls.P.ansi_fg(cls.P.COLOR_SECUNDARIO)
        blanco = cls.P.ansi_fg(cls.P.TEXTO_PRINCIPAL)
        gris = cls.P.ansi_fg(cls.P.TOKEN_COMENTARIO)
        reset = cls.P.ANSI_RESET
        bold = cls.P.ANSI_BOLD

        ancho_idx = 4
        ancho_pos = 9
        ancho_cat = 26
        ancho_lex = 24
        ancho_desc = 36

        # Encabezado
        linea_sep = f"{turquesa}┌{'─' * ancho_idx}┬{'─' * ancho_pos}┬{'─' * ancho_cat}┬{'─' * ancho_lex}┬{'─' * ancho_desc}┐{reset}"
        linea_mid = f"{turquesa}├{'─' * ancho_idx}┼{'─' * ancho_pos}┼{'─' * ancho_cat}┼{'─' * ancho_lex}┼{'─' * ancho_desc}┤{reset}"
        linea_fin = f"{turquesa}└{'─' * ancho_idx}┴{'─' * ancho_pos}┴{'─' * ancho_cat}┴{'─' * ancho_lex}┴{'─' * ancho_desc}┘{reset}"

        print(linea_sep)
        print(f"{turquesa}│ {bold}{'#':<{ancho_idx-2}}{reset}{turquesa} │ {bold}{'LÍNEA:COL':<{ancho_pos-2}}{reset}{turquesa} │ {bold}{'CATEGORÍA':<{ancho_cat-2}}{reset}{turquesa} │ {bold}{'LEXEMA':<{ancho_lex-2}}{reset}{turquesa} │ {bold}{'DESCRIPCIÓN':<{ancho_desc-2}}{reset}{turquesa} │{reset}")
        print(linea_mid)

        for i, t in enumerate(tokens, start=1):
            color_token = cls.P.ansi_fg(t.color_hex)
            pos_str = f"L{t.linea:02d}:C{t.columna:02d}"
            lex_visible = t.lexema.replace("\n", "\\n").replace("\t", "\\t")
            if len(lex_visible) > ancho_lex - 3:
                lex_visible = lex_visible[:ancho_lex - 6] + "..."

            desc_visible = t.descripcion
            if len(desc_visible) > ancho_desc - 3:
                desc_visible = desc_visible[:ancho_desc - 6] + "..."

            badge_cat = f"{color_token}{bold}{t.categoria.value:<{ancho_cat-2}}{reset}"
            badge_lex = f"{color_token}{lex_visible:<{ancho_lex-2}}{reset}"

            print(f"{turquesa}│{reset} {gris}{i:<{ancho_idx-2}}{reset} {turquesa}│{reset} {blanco}{pos_str:<{ancho_pos-2}}{reset} {turquesa}│{reset} {badge_cat} {turquesa}│{reset} {badge_lex} {turquesa}│{reset} {blanco}{desc_visible:<{ancho_desc-2}}{reset} {turquesa}│{reset}")

        print(linea_fin)

    @classmethod
    def imprimir_tarjetas_metricas(cls, stats: Dict[str, Any]) -> None:
        """Muestra tarjetas estadísticas en el panel de control Vaporwave."""
        magenta = cls.P.ansi_fg(cls.P.COLOR_PRIMARIO)
        turquesa = cls.P.ansi_fg(cls.P.COLOR_SECUNDARIO)
        fucsia = cls.P.ansi_fg(cls.P.TOKEN_NUMERO)
        rojo = cls.P.ansi_fg(cls.P.TOKEN_ERROR)
        blanco = cls.P.ansi_fg(cls.P.TEXTO_PRINCIPAL)
        reset = cls.P.ANSI_RESET
        bold = cls.P.ANSI_BOLD

        total = stats["total_tokens"]
        validos = stats["tokens_validos"]
        errores = stats["errores_lexicos"]
        tasa = stats["tasa_validez"]

        color_tasa = turquesa if errores == 0 else rojo

        print(f"\n{magenta}{bold}═══ RESUMEN DE EJECUCIÓN DEL ANALIZADOR ═══{reset}")
        print(f"{turquesa}╔══════════════════╦══════════════════╦══════════════════╦══════════════════╗{reset}")
        print(f"{turquesa}║{reset}  TOTAL TOKENS    {turquesa}║{reset}  TOKENS VÁLIDOS  {turquesa}║{reset}  ERRORES LÉXICOS {turquesa}║{reset}  PRECISIÓN LÉXICA {turquesa}║{reset}")
        print(f"{turquesa}╠══════════════════╬══════════════════╬══════════════════╬══════════════════╣{reset}")
        print(f"{turquesa}║{reset}   {fucsia}{bold}{total:^12}{reset}   {turquesa}║{reset}   {turquesa}{bold}{validos:^12}{reset}   {turquesa}║{reset}   {rojo}{bold}{errores:^12}{reset}   {turquesa}║{reset}   {color_tasa}{bold}{f'{tasa}%':^12}{reset}   {turquesa}║{reset}")
        print(f"{turquesa}╚══════════════════╩══════════════════╩══════════════════╩══════════════════╝{reset}")

        # Gráfico de barras de categorías
        print(f"\n{turquesa}{bold}Distribución por Categoría:{reset}")
        desglose = stats["desglose"]
        max_cuenta = max(desglose.values()) if desglose else 1

        for cat_nombre, cuenta in sorted(desglose.items(), key=lambda x: x[1], reverse=True):
            barra_len = int((cuenta / max_cuenta) * 28)
            barra = "█" * barra_len
            color_barra = cls.P.ansi_fg(
                PaletaVaporwave.TOKEN_ERROR if "Error" in cat_nombre else
                PaletaVaporwave.TOKEN_RESERVADA if "Reservada" in cat_nombre else
                PaletaVaporwave.TOKEN_CADENA if "Cadena" in cat_nombre else
                PaletaVaporwave.TOKEN_NUMERO if "Número" in cat_nombre else
                PaletaVaporwave.TOKEN_IDENTIFICADOR
            )
            print(f"  {blanco}{cat_nombre:<28}{reset} {color_barra}{barra} {cls.P.ANSI_BOLD}{cuenta}{reset}")


# ==============================================================================
# ==============================================================================
# SECCIÓN 5: GENERADOR DE DASHBOARD WEB CYBERPUNK (HTML5/CSS3) - GITHUB PAGES
# ==============================================================================

def generar_reporte_html(tokens: Optional[List[Token]] = None, codigo_original: Optional[str] = None, ruta_salida: Optional[str] = None) -> str:
    """
    Genera el archivo HTML5 interactivo y dinámico (index.html / clasificador_tokens.html)
    con el Evaluador de Lexema Único y el Analizador de Código Dinámico en tiempo real,
    manteniendo estrictamente la paleta Vaporwave / Cyberpunk Neon.
    """
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    if ruta_salida is None:
        ruta_salida = os.path.join(directorio_script, "index.html")

    ruta_index_existente = os.path.join(directorio_script, "index.html")
    if os.path.exists(ruta_index_existente) and os.path.abspath(ruta_salida) != os.path.abspath(ruta_index_existente):
        with open(ruta_index_existente, "r", encoding="utf-8") as f_in:
            contenido_html = f_in.read()
        with open(ruta_salida, "w", encoding="utf-8") as f_out:
            f_out.write(contenido_html)
    elif os.path.exists(ruta_index_existente):
        with open(ruta_index_existente, "r", encoding="utf-8") as f:
            contenido_html = f.read()
    else:
        contenido_html = "<!DOCTYPE html><html><head><title>SYNTH-LEX</title></head><body>Consulte index.html</body></html>"
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(contenido_html)

    # Sincronizar clasificador_tokens.html para compatibilidad
    ruta_tokens_html = os.path.join(directorio_script, "clasificador_tokens.html")
    try:
        with open(ruta_tokens_html, "w", encoding="utf-8") as f_sync:
            f_sync.write(contenido_html)
    except Exception:
        pass

    return os.path.abspath(ruta_salida)

# SECCIÓN 6: INTERFAZ GRÁFICA DE USUARIO EN TKINTER (CYBERPUNK NEON GUI)
# ==============================================================================

def iniciar_interfaz_grafica():
    """
    Inicia la interfaz gráfica moderna en Tkinter bajo la estética Cyberpunk Neon.
    Si Tkinter no está presente o falla en el entorno, lo notifica e inicia el modo CLI.
    """
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
    except (ImportError, ModuleNotFoundError) as err:
        print(f"\n{PaletaVaporwave.ansi_fg(PaletaVaporwave.TOKEN_ERROR)}[!] Error: Tkinter no está configurado en este entorno de Python ({err}).{PaletaVaporwave.ANSI_RESET}")
        print(f"{PaletaVaporwave.ansi_fg(PaletaVaporwave.COLOR_SECUNDARIO)}Iniciando automáticamente en modo CLI Cyberpunk Neón con TrueColor...{PaletaVaporwave.ANSI_RESET}\n")
        iniciar_modo_interactivo()
        return

    # Iniciar ventana principal
    root = tk.Tk()
    root.title("SYNTH-LEX | Analizador Léxico Cyberpunk Neon")
    root.geometry("1180x760")
    root.configure(bg=PaletaVaporwave.FONDO_PRINCIPAL)
    root.minsize(980, 640)

    analizador = AnalizadorLexico()

    # Estilos ttk
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=PaletaVaporwave.CONTENEDOR_TARJETA,
        foreground=PaletaVaporwave.TEXTO_PRINCIPAL,
        fieldbackground=PaletaVaporwave.CONTENEDOR_TARJETA,
        rowheight=26,
        font=("Fira Code", 9)
    )
    style.configure(
        "Treeview.Heading",
        background="#140F22",
        foreground=PaletaVaporwave.COLOR_SECUNDARIO,
        font=("Segoe UI", 10, "bold")
    )
    style.map(
        "Treeview",
        background=[("selected", PaletaVaporwave.COLOR_PRIMARIO)],
        foreground=[("selected", "#FFFFFF")]
    )

    # ---------------- ENCABEZADO ----------------
    frame_header = tk.Frame(root, bg=PaletaVaporwave.FONDO_PRINCIPAL, pady=10)
    frame_header.pack(fill=tk.X, padx=20)

    lbl_titulo = tk.Label(
        frame_header,
        text="SYNTH-LEX  //  CLASIFICADOR DE TOKENS",
        font=("Segoe UI", 20, "bold"),
        fg=PaletaVaporwave.COLOR_SECUNDARIO,
        bg=PaletaVaporwave.FONDO_PRINCIPAL
    )
    lbl_titulo.pack(anchor="w")

    lbl_meta = tk.Label(
        frame_header,
        text="Alumno: Fernando Vidal Delgado  |  No. Control: 2320905  |  Materia: Lenguajes y Autómatas / Compiladores",
        font=("Segoe UI", 10),
        fg=PaletaVaporwave.COLOR_PRIMARIO,
        bg=PaletaVaporwave.FONDO_PRINCIPAL
    )
    lbl_meta.pack(anchor="w", pady=(2, 0))

    # ---------------- TARJETAS DE MÉTRICAS ----------------
    frame_cards = tk.Frame(root, bg=PaletaVaporwave.FONDO_PRINCIPAL)
    frame_cards.pack(fill=tk.X, padx=20, pady=(5, 10))

    var_total = tk.StringVar(value="0")
    var_validos = tk.StringVar(value="0")
    var_errores = tk.StringVar(value="0")
    var_precision = tk.StringVar(value="100%")

    def crear_tarjeta(parent, titulo, var_val, color_borde):
        card = tk.Frame(parent, bg=PaletaVaporwave.CONTENEDOR_TARJETA, bd=1, relief=tk.SOLID, padx=15, pady=8)
        card.configure(highlightbackground=color_borde, highlightcolor=color_borde, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(card, text=titulo, font=("Segoe UI", 8, "bold"), fg="#8E9AA8", bg=PaletaVaporwave.CONTENEDOR_TARJETA).pack(anchor="w")
        tk.Label(card, textvariable=var_val, font=("Segoe UI", 16, "bold"), fg=color_borde, bg=PaletaVaporwave.CONTENEDOR_TARJETA).pack(anchor="w")

    crear_tarjeta(frame_cards, "TOTAL TOKENS", var_total, PaletaVaporwave.COLOR_PRIMARIO)
    crear_tarjeta(frame_cards, "TOKENS VÁLIDOS", var_validos, PaletaVaporwave.COLOR_SECUNDARIO)
    crear_tarjeta(frame_cards, "ERRORES LÉXICOS", var_errores, PaletaVaporwave.TOKEN_ERROR)
    crear_tarjeta(frame_cards, "PRECISIÓN LÉXICA", var_precision, PaletaVaporwave.TOKEN_NUMERO)

    # ---------------- CONTENEDOR PRINCIPAL DIVIDIDO ----------------
    paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg=PaletaVaporwave.FONDO_PRINCIPAL, sashwidth=4)
    paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    # Panel Izquierdo: Editor de Código
    frame_editor = tk.Frame(paned, bg=PaletaVaporwave.CONTENEDOR_TARJETA, padx=10, pady=10)
    paned.add(frame_editor, minsize=420)

    tk.Label(
        frame_editor,
        text="⚡ Código Fuente / Entrada de Lexemas:",
        font=("Segoe UI", 11, "bold"),
        fg=PaletaVaporwave.COLOR_PRIMARIO,
        bg=PaletaVaporwave.CONTENEDOR_TARJETA
    ).pack(anchor="w", pady=(0, 6))

    text_codigo = tk.Text(
        frame_editor,
        wrap=tk.NONE,
        bg="#0B0814",
        fg=PaletaVaporwave.TEXTO_PRINCIPAL,
        insertbackground=PaletaVaporwave.COLOR_SECUNDARIO,
        font=("Fira Code", 10),
        relief=tk.FLAT,
        padx=10,
        pady=10
    )
    scroll_text_y = tk.Scrollbar(frame_editor, command=text_codigo.yview)
    text_codigo.configure(yscrollcommand=scroll_text_y.set)

    scroll_text_y.pack(side=tk.RIGHT, fill=tk.Y)
    text_codigo.pack(fill=tk.BOTH, expand=True)

    # Configuración de tags de sintaxis Neón en el editor
    text_codigo.tag_config("reservada", foreground=PaletaVaporwave.TOKEN_RESERVADA, font=("Fira Code", 10, "bold"))
    text_codigo.tag_config("cadena",    foreground=PaletaVaporwave.TOKEN_CADENA)
    text_codigo.tag_config("numero",    foreground=PaletaVaporwave.TOKEN_NUMERO, font=("Fira Code", 10, "bold"))
    text_codigo.tag_config("error",     foreground=PaletaVaporwave.TOKEN_ERROR, underline=True)
    text_codigo.tag_config("id",        foreground=PaletaVaporwave.TOKEN_IDENTIFICADOR)

    # Panel Derecho: Tabla de Tokens
    frame_tabla = tk.Frame(paned, bg=PaletaVaporwave.CONTENEDOR_TARJETA, padx=10, pady=10)
    paned.add(frame_tabla, minsize=520)

    tk.Label(
        frame_tabla,
        text="🔮 Tokens Reconocidos & Clasificación:",
        font=("Segoe UI", 11, "bold"),
        fg=PaletaVaporwave.COLOR_SECUNDARIO,
        bg=PaletaVaporwave.CONTENEDOR_TARJETA
    ).pack(anchor="w", pady=(0, 6))

    cols = ("num", "pos", "categoria", "lexema", "desc")
    tree = ttk.Treeview(frame_tabla, columns=cols, show="headings")
    tree.heading("num", text="#")
    tree.heading("pos", text="Posición")
    tree.heading("categoria", text="Categoría")
    tree.heading("lexema", text="Lexema")
    tree.heading("desc", text="Descripción")

    tree.column("num", width=36, anchor="center")
    tree.column("pos", width=75, anchor="center")
    tree.column("categoria", width=160)
    tree.column("lexema", width=140)
    tree.column("desc", width=220)

    scroll_tree_y = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scroll_tree_y.set)
    scroll_tree_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(fill=tk.BOTH, expand=True)

    # ---------------- ACCIONES Y EVENTOS ----------------
    tokens_actuales: List[Token] = []

    def ejecutar_analisis():
        nonlocal tokens_actuales
        codigo = text_codigo.get("1.0", tk.END).rstrip("\n")
        tokens_actuales = analizador.analizar_codigo(codigo)

        # Limpiar tabla
        for item in tree.get_children():
            tree.delete(item)

        # Poblar tabla
        for idx, t in enumerate(tokens_actuales, 1):
            pos = f"L{t.linea:02d}:C{t.columna:02d}"
            lex = t.lexema.replace("\n", "\\n")
            tag = "error" if t.categoria == CategoriaToken.ERROR_LEXICO else "normal"
            tree.insert("", tk.END, values=(idx, pos, t.categoria.value, lex, t.descripcion), tags=(tag,))

        tree.tag_configure("error", foreground=PaletaVaporwave.TOKEN_ERROR)
        tree.tag_configure("normal", foreground=PaletaVaporwave.TEXTO_PRINCIPAL)

        # Actualizar métricas
        stats = analizador.obtener_estadisticas(tokens_actuales)
        var_total.set(str(stats["total_tokens"]))
        var_validos.set(str(stats["tokens_validos"]))
        var_errores.set(str(stats["errores_lexicos"]))
        var_precision.set(f"{stats['tasa_validez']}%")

    def cargar_ejemplo(tipo: str):
        text_codigo.delete("1.0", tk.END)
        if tipo == "c_programa":
            codigo = """// Programa demostrativo Cyberpunk en C/Java
int main() {
    float radio = 3.14159;
    string saludo = "Neo Tokyo 2084";
    if (radio >= 1.0) {
        radio += 2.5;
    } else {
        radio = radio * 0.5;
    }
    return 0;
}"""
        elif tipo == "errores":
            codigo = """// Demostración de manejo estricto de errores léxicos
int 99invalido = 100;
@variable_rara = $precio;
string sin_cerrar = "Esta cadena no cierra;
float num = 45.67;
~simbolo_extraño;"""
        elif tipo == "todas_categorias":
            codigo = """/* Demostración completa de las 10 categorías */
int a = 42;                    // Entero y asignación
float b = 3.1416;              // Decimal
string msj = 'Cyberpunk Neon'; // Cadena
if (a >= 10 && b != 0.0) {     // Reservada y comparación
    a += 5;                    // Asignación compuesta
    b = a * 2.0;               // Aritmético
}
# Delimitadores probados: ;, (), {}, []
int matriz[5] = {1, 2, 3, 4, 5};
@error_lexico_simbolo;         // Error léxico fuera de regla"""
        text_codigo.insert("1.0", codigo)
        ejecutar_analisis()

    def exportar_html_gui():
        codigo = text_codigo.get("1.0", tk.END)
        tokens = analizador.analizar_codigo(codigo)
        ruta = generar_reporte_html(tokens, codigo)
        webbrowser.open(f"file://{ruta}")
        messagebox.showinfo("Reporte Exportado", f"El dashboard HTML Cyberpunk ha sido generado con éxito en:\n{ruta}")

    def limpiar_todo():
        text_codigo.delete("1.0", tk.END)
        for item in tree.get_children():
            tree.delete(item)
        var_total.set("0")
        var_validos.set("0")
        var_errores.set("0")
        var_precision.set("100%")

    # ---------------- BARRA DE HERRAMIENTAS INFERIOR ----------------
    frame_footer = tk.Frame(root, bg=PaletaVaporwave.FONDO_PRINCIPAL, pady=12)
    frame_footer.pack(fill=tk.X, padx=20)

    btn_analizar = tk.Button(
        frame_footer,
        text="⚡ ANALIZAR TOKENS",
        command=ejecutar_analisis,
        bg=PaletaVaporwave.COLOR_PRIMARIO,
        fg="#FFFFFF",
        activebackground="#D6006B",
        activeforeground="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        relief=tk.FLAT,
        padx=18,
        pady=6,
        cursor="hand2"
    )
    btn_analizar.pack(side=tk.LEFT, padx=(0, 10))

    btn_ejemplo1 = tk.Button(
        frame_footer,
        text="📂 Ejemplo Completo",
        command=lambda: cargar_ejemplo("todas_categorias"),
        bg=PaletaVaporwave.CONTENEDOR_TARJETA,
        fg=PaletaVaporwave.COLOR_SECUNDARIO,
        relief=tk.GROOVE,
        padx=12,
        pady=6,
        cursor="hand2"
    )
    btn_ejemplo1.pack(side=tk.LEFT, padx=5)

    btn_ejemplo2 = tk.Button(
        frame_footer,
        text="⚠️ Probar Errores",
        command=lambda: cargar_ejemplo("errores"),
        bg=PaletaVaporwave.CONTENEDOR_TARJETA,
        fg=PaletaVaporwave.TOKEN_ERROR,
        relief=tk.GROOVE,
        padx=12,
        pady=6,
        cursor="hand2"
    )
    btn_ejemplo2.pack(side=tk.LEFT, padx=5)

    btn_exportar = tk.Button(
        frame_footer,
        text="🌐 Ver Dashboard HTML",
        command=exportar_html_gui,
        bg=PaletaVaporwave.CONTENEDOR_TARJETA,
        fg=PaletaVaporwave.TOKEN_NUMERO,
        relief=tk.GROOVE,
        padx=12,
        pady=6,
        cursor="hand2"
    )
    btn_exportar.pack(side=tk.LEFT, padx=5)

    btn_limpiar = tk.Button(
        frame_footer,
        text="🗑️ Limpiar",
        command=limpiar_todo,
        bg=PaletaVaporwave.CONTENEDOR_TARJETA,
        fg="#A0AEC0",
        relief=tk.FLAT,
        padx=12,
        pady=6,
        cursor="hand2"
    )
    btn_limpiar.pack(side=tk.RIGHT)

    # Cargar ejemplo por defecto
    cargar_ejemplo("todas_categorias")

    root.mainloop()


# ==============================================================================
# SECCIÓN 7: MODO INTERACTIVO REPL (LÍNEA DE COMANDOS)
# ==============================================================================

def iniciar_modo_interactivo():
    """
    Inicia una consola REPL interactiva Cyberpunk donde el usuario puede escribir
    lexemas aislados o bloques de código y ver su clasificación en tiempo real.
    """
    analizador = AnalizadorLexico()
    P = PaletaVaporwave
    magenta = P.ansi_fg(P.COLOR_PRIMARIO)
    turquesa = P.ansi_fg(P.COLOR_SECUNDARIO)
    blanco = P.ansi_fg(P.TEXTO_PRINCIPAL)
    reset = P.ANSI_RESET
    bold = P.ANSI_BOLD

    print(InterfazCyberpunkCLI.banner())
    print(f"{turquesa}MODO INTERACTIVO // REPL CYBERPUNK ACTIVADO{reset}")
    print(f"{blanco}Instrucciones:{reset}")
    print(f"  • Escribe un {bold}lexema individual{reset} o una {bold}línea de código{reset} y presiona Enter.")
    print(f"  • Comandos especiales: {magenta}:test{reset} (ejecutar tests), {magenta}:ejemplo{reset} (código demo), {magenta}:html{reset} (generar reporte), {magenta}:salir{reset} (terminar).")
    print(f"{turquesa}{'─' * 74}{reset}\n")

    while True:
        try:
            prompt = f"{magenta}SYNTH-LEX{reset} {turquesa}❯{reset} "
            entrada = input(prompt).strip()

            if not entrada:
                continue

            if entrada in (":salir", ":exit", "quit", "exit"):
                print(f"\n{turquesa}Sesión finalizada. ¡Hasta pronto!{reset}")
                break

            elif entrada == ":test":
                ejecutar_suite_pruebas()
                continue

            elif entrada == ":html":
                codigo_demo = """int main() {
    float x = 10.5;
    string msg = "Reporte Cyberpunk";
    if (x > 5.0) { x += 1; }
    return 0;
}"""
                tokens = analizador.analizar_codigo(codigo_demo)
                ruta = generar_reporte_html(tokens, codigo_demo)
                print(f"{turquesa}[✓] Dashboard HTML generado en: {blanco}{ruta}{reset}")
                continue

            elif entrada == ":ejemplo":
                codigo_demo = "float temp = 98.6; if (temp >= 100.0) { alert('Alerta'); } else { temp += 1.5; }"
                print(f"{turquesa}Analizando código de demostración:{reset}\n{blanco}{codigo_demo}{reset}\n")
                tokens = analizador.analizar_codigo(codigo_demo)
                InterfazCyberpunkCLI.imprimir_tabla_tokens(tokens)
                InterfazCyberpunkCLI.imprimir_tarjetas_metricas(analizador.obtener_estadisticas(tokens))
                continue

            # Determinación de modo de análisis:
            # Si contiene espacios o operadores compuestos que sugieren múltiples tokens, se analiza como flujo
            contiene_delimitadores = bool(re.search(r"[;\(\)\{\}\s]", entrada))
            
            if contiene_delimitadores:
                tokens = analizador.analizar_codigo(entrada)
                InterfazCyberpunkCLI.imprimir_tabla_tokens(tokens)
                InterfazCyberpunkCLI.imprimir_tarjetas_metricas(analizador.obtener_estadisticas(tokens))
            else:
                # Lexema individual estricto
                token = analizador.clasificar_lexema(entrada)
                InterfazCyberpunkCLI.imprimir_tabla_tokens([token])

        except (KeyboardInterrupt, EOFError):
            print(f"\n{turquesa}Interrupción recibida. Saliendo...{reset}")
            break


# ==============================================================================
# SECCIÓN 8: SUITE DE PRUEBAS AUTOMATIZADA
# ==============================================================================

def ejecutar_suite_pruebas() -> bool:
    """
    Ejecuta un conjunto completo de casos de prueba verificando cada categoría
    especificada y el manejo formal de errores léxicos.
    """
    analizador = AnalizadorLexico()
    P = PaletaVaporwave
    verde = P.ansi_fg(P.COLOR_SECUNDARIO)
    rojo = P.ansi_fg(P.TOKEN_ERROR)
    blanco = P.ansi_fg(P.TEXTO_PRINCIPAL)
    magenta = P.ansi_fg(P.COLOR_PRIMARIO)
    reset = P.ANSI_RESET
    bold = P.ANSI_BOLD

    print(f"\n{magenta}{bold}╔════════════════════════════════════════════════════════════════════╗{reset}")
    print(f"{magenta}{bold}║        EJECUTANDO SUITE COMPLETA DE PRUEBAS DE VALIDACIÓN          ║{reset}")
    print(f"{magenta}{bold}╚════════════════════════════════════════════════════════════════════╝{reset}\n")

    casos_unitarios: List[Tuple[str, CategoriaToken, str]] = [
        # Categoría 1: Palabras Reservadas
        ("if",      CategoriaToken.PALABRA_RESERVADA, "Palabra reservada if"),
        ("else",    CategoriaToken.PALABRA_RESERVADA, "Palabra reservada else"),
        ("while",   CategoriaToken.PALABRA_RESERVADA, "Palabra reservada while"),
        ("for",     CategoriaToken.PALABRA_RESERVADA, "Palabra reservada for"),
        ("return",  CategoriaToken.PALABRA_RESERVADA, "Palabra reservada return"),
        ("int",     CategoriaToken.PALABRA_RESERVADA, "Tipo de dato int"),
        ("float",   CategoriaToken.PALABRA_RESERVADA, "Tipo de dato float"),
        ("void",    CategoriaToken.PALABRA_RESERVADA, "Tipo de dato void"),

        # Categoría 2: Identificadores
        ("contador",     CategoriaToken.IDENTIFICADOR, "Identificador estándar"),
        ("_variable",    CategoriaToken.IDENTIFICADOR, "Identificador con guion bajo inicial"),
        ("x1",           CategoriaToken.IDENTIFICADOR, "Identificador con número final"),
        ("suma_total2",  CategoriaToken.IDENTIFICADOR, "Identificador compuesto"),

        # Categoría 3: Números Enteros
        ("0",      CategoriaToken.NUMERO_ENTERO, "Entero cero"),
        ("42",     CategoriaToken.NUMERO_ENTERO, "Entero positivo de dos dígitos"),
        ("9999",   CategoriaToken.NUMERO_ENTERO, "Entero grande"),

        # Categoría 4: Números Decimales
        ("3.14159", CategoriaToken.NUMERO_DECIMAL, "Decimal pi"),
        ("0.05",    CategoriaToken.NUMERO_DECIMAL, "Decimal menor a uno"),
        ("10.5e2",  CategoriaToken.NUMERO_DECIMAL, "Decimal en notación científica"),

        # Categoría 5: Cadenas de Texto
        ('"hola"',                    CategoriaToken.CADENA, "Cadena con comillas dobles"),
        ("'mundo'",                   CategoriaToken.CADENA, "Cadena con comillas simples"),
        ('"Texto con \\"escape\\""',   CategoriaToken.CADENA, "Cadena con comillas escapadas"),

        # Categoría 6: Operadores Aritméticos
        ("+",  CategoriaToken.OP_ARITMETICO, "Operador suma"),
        ("-",  CategoriaToken.OP_ARITMETICO, "Operador resta"),
        ("*",  CategoriaToken.OP_ARITMETICO, "Operador multiplicación"),
        ("/",  CategoriaToken.OP_ARITMETICO, "Operador división"),
        ("%",  CategoriaToken.OP_ARITMETICO, "Operador módulo"),
        ("++", CategoriaToken.OP_ARITMETICO, "Operador incremento"),

        # Categoría: Operadores Lógicos
        ("&&", CategoriaToken.OP_LOGICO, "Operador lógico AND"),
        ("||", CategoriaToken.OP_LOGICO, "Operador lógico OR"),
        ("!",  CategoriaToken.OP_LOGICO, "Operador lógico NOT"),

        # Categoría 7: Operadores de Comparación
        ("==", CategoriaToken.OP_COMPARACION, "Operador igual que"),
        ("!=", CategoriaToken.OP_COMPARACION, "Operador no igual que"),
        ("<",  CategoriaToken.OP_COMPARACION, "Operador menor que"),
        (">",  CategoriaToken.OP_COMPARACION, "Operador mayor que"),
        ("<=", CategoriaToken.OP_COMPARACION, "Operador menor o igual que"),
        (">=", CategoriaToken.OP_COMPARACION, "Operador mayor o igual que"),

        # Categoría 8: Operadores de Asignación
        ("=",  CategoriaToken.OP_ASIGNACION, "Asignación simple"),
        ("+=", CategoriaToken.OP_ASIGNACION, "Asignación con suma"),
        ("-=", CategoriaToken.OP_ASIGNACION, "Asignación con resta"),
        ("*=", CategoriaToken.OP_ASIGNACION, "Asignación con multiplicación"),
        ("/=", CategoriaToken.OP_ASIGNACION, "Asignación con división"),

        # Categoría 9: Delimitadores
        (";", CategoriaToken.DELIMITADOR, "Punto y coma"),
        (",", CategoriaToken.DELIMITADOR, "Coma separadora"),
        ("(", CategoriaToken.DELIMITADOR, "Paréntesis de apertura"),
        (")", CategoriaToken.DELIMITADOR, "Paréntesis de cierre"),
        ("{", CategoriaToken.DELIMITADOR, "Llave de apertura"),
        ("}", CategoriaToken.DELIMITADOR, "Llave de cierre"),
        ("[", CategoriaToken.DELIMITADOR, "Corchete de apertura"),
        ("]", CategoriaToken.DELIMITADOR, "Corchete de cierre"),

        # Categoría 10: Error Léxico / No Reconocido
        ("@invalido",    CategoriaToken.ERROR_LEXICO, "Símbolo arroba no permitido"),
        ("$precio",      CategoriaToken.ERROR_LEXICO, "Símbolo dólar no permitido"),
        ("123variable",  CategoriaToken.ERROR_LEXICO, "Identificador iniciando con dígito"),
        ("~",            CategoriaToken.ERROR_LEXICO, "Tilde no reconocida"),
    ]

    exitos = 0
    fallos = 0

    for lexema, cat_esperada, desc in casos_unitarios:
        token = analizador.clasificar_lexema(lexema)
        color_cat = P.ansi_fg(token.color_hex)
        if token.categoria == cat_esperada:
            exitos += 1
            print(f"  {verde}[PASS]{reset} {blanco}{lexema:<26}{reset} -> {color_cat}{token.categoria.value:<26}{reset} ({desc})")
        else:
            fallos += 1
            print(f"  {rojo}[FAIL]{reset} {blanco}{lexema:<26}{reset} -> Obtenido: {token.categoria.value} | Esperado: {cat_esperada.value}")

    # Prueba de código fuente continuo con todas las categorías
    print(f"\n{magenta}{bold}--- Prueba de Análisis de Flujo de Código Completo ---{reset}")
    codigo_completo = """// Bloque de prueba integral
int calcular_area() {
    float radio = 5.25;
    string etiqueta = "Radio calculado";
    if (radio >= 1.0) {
        radio *= 2;
    } else {
        radio = radio + 0.1;
    }
    @simbolo_invalido;
    return 0;
}"""

    tokens_stream = analizador.analizar_codigo(codigo_completo)
    stats_stream = analizador.obtener_estadisticas(tokens_stream)

    print(f"  Total tokens encontrados en flujo: {stats_stream['total_tokens']}")
    print(f"  Tokens válidos: {stats_stream['tokens_validos']}")
    print(f"  Errores léxicos detectados: {stats_stream['errores_lexicos']}")

    total_pruebas = exitos + fallos
    print(f"\n{magenta}════════════════════════════════════════════════════════════════════{reset}")
    if fallos == 0:
        print(f"{verde}{bold}✓ TODAS LAS PRUEBAS ({exitos}/{total_pruebas}) PASARON EXITOSAMENTE.{reset}\n")
        return True
    else:
        print(f"{rojo}{bold}✗ SE DETECTARON {fallos} FALLOS DE {total_pruebas} PRUEBAS.{reset}\n")
        return False


# ==============================================================================
# SECCIÓN 9: PUNTO DE ENTRADA PRINCIPAL Y DESPACHADOR CLI
# ==============================================================================

def main():
    """Analizador de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="SYNTH-LEX: Clasificador de Tokens (Analizador Léxico) - Estilo Vaporwave / Cyberpunk Neon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python clasificador_tokens.py                  (Inicia modo interactivo REPL)
  python clasificador_tokens.py --gui            (Inicia interfaz gráfica Tkinter)
  python clasificador_tokens.py --test           (Ejecuta suite de pruebas unitarias)
  python clasificador_tokens.py --cli "int x=5;" (Analiza el texto proporcionado)
  python clasificador_tokens.py --file code.txt  (Analiza archivo externo)
  python clasificador_tokens.py --html           (Genera y abre dashboard HTML)
        """
    )

    parser.add_argument("--gui", action="store_true", help="Lanza la interfaz gráfica de usuario en Tkinter")
    parser.add_argument("--test", action="store_true", help="Ejecuta la suite de pruebas unitarias automatizada")
    parser.add_argument("--cli", type=str, help="Analiza una cadena de código o lexema directamente")
    parser.add_argument("--file", type=str, help="Lee y analiza un archivo fuente externo")
    parser.add_argument("--html", action="store_true", help="Genera y abre un dashboard HTML interactivo")
    parser.add_argument("--json", action="store_true", help="Emite el resultado en formato JSON")

    args = parser.parse_args()

    # Opción 1: Ejecutar suite de pruebas
    if args.test:
        print(InterfazCyberpunkCLI.banner())
        exito = ejecutar_suite_pruebas()
        sys.exit(0 if exito else 1)

    # Opción 2: Modo GUI Tkinter
    if args.gui:
        iniciar_interfaz_grafica()
        sys.exit(0)

    # Opción 3: Analizar archivo externo
    if args.file:
        if not os.path.exists(args.file):
            print(f"{PaletaVaporwave.ansi_fg(PaletaVaporwave.TOKEN_ERROR)}[!] Error: El archivo '{args.file}' no existe.{PaletaVaporwave.ANSI_RESET}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        analizador = AnalizadorLexico()
        tokens = analizador.analizar_codigo(contenido)

        if args.json:
            print(json.dumps([t.to_dict() for t in tokens], indent=2, ensure_ascii=False))
        else:
            print(InterfazCyberpunkCLI.banner())
            InterfazCyberpunkCLI.imprimir_tabla_tokens(tokens)
            InterfazCyberpunkCLI.imprimir_tarjetas_metricas(analizador.obtener_estadisticas(tokens))
            if args.html:
                ruta = generar_reporte_html(tokens, contenido)
                webbrowser.open(f"file://{ruta}")
        sys.exit(0)

    # Opción 4: Analizar cadena directa desde CLI
    if args.cli:
        analizador = AnalizadorLexico()
        # Si no tiene espacios ni delimitadores, clasifica como lexema individual
        if not re.search(r"[;\(\)\{\}\s]", args.cli):
            tokens = [analizador.clasificar_lexema(args.cli)]
        else:
            tokens = analizador.analizar_codigo(args.cli)

        if args.json:
            print(json.dumps([t.to_dict() for t in tokens], indent=2, ensure_ascii=False))
        else:
            print(InterfazCyberpunkCLI.banner())
            InterfazCyberpunkCLI.imprimir_tabla_tokens(tokens)
            InterfazCyberpunkCLI.imprimir_tarjetas_metricas(analizador.obtener_estadisticas(tokens))
            if args.html:
                ruta = generar_reporte_html(tokens, args.cli)
                webbrowser.open(f"file://{ruta}")
        sys.exit(0)

    # Opción 5: Generar HTML con ejemplo
    if args.html:
        analizador = AnalizadorLexico()
        demo = """// Demostración Cyberpunk Neon
int main() {
    float pi = 3.14159;
    string saludo = "Neo Tokyo";
    if (pi > 3.0) {
        pi += 1.0;
    }
    return 0;
}"""
        tokens = analizador.analizar_codigo(demo)
        ruta = generar_reporte_html(tokens, demo)
        print(f"{PaletaVaporwave.ansi_fg(PaletaVaporwave.COLOR_SECUNDARIO)}[✓] Dashboard HTML generado en: {PaletaVaporwave.ansi_fg(PaletaVaporwave.TEXTO_PRINCIPAL)}{ruta}{PaletaVaporwave.ANSI_RESET}")
        webbrowser.open(f"file://{ruta}")
        sys.exit(0)

    # Por defecto: Iniciar Modo Interactivo REPL
    iniciar_modo_interactivo()


if __name__ == "__main__":
    main()
