"""Motor de cálculo de EcoTrack.

Convierte una frase en español ("Hoy comí carne y viajé 20km en bus") en una
lista de actividades con su estimado de CO2e (kg). Sin dependencias externas:
todo el módulo es Python puro para que sea fácil de probar.

Los factores son aproximaciones orientativas (promedios de literatura
divulgativa); sirven para un MVP, no para reportes oficiales.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Factores de emisión (kg CO2e). Se mantienen SOLO aquí.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Factor:
    label: str
    kg_per_unit: float
    unit: str
    keywords: tuple[str, ...]


TRANSPORT: dict[str, Factor] = {
    "bus": Factor("Bus", 0.089, "km", ("bus", "buseta", "transmilenio", "autobus", "colectivo")),
    "carro": Factor("Carro", 0.171, "km", ("carro", "auto", "coche", "automovil")),
    "moto": Factor("Moto", 0.113, "km", ("moto", "motocicleta")),
    "metro": Factor("Metro / tren", 0.041, "km", ("metro", "tren")),
    "taxi": Factor("Taxi / app de transporte", 0.171, "km", ("taxi", "uber", "didi", "cabify")),
    "avion": Factor("Avión", 0.255, "km", ("avion", "vuelo", "vuele")),
    "bici": Factor("Bicicleta", 0.0, "km", ("bici", "bicicleta", "cicla", "patineta")),
    "pie": Factor("A pie", 0.0, "km", ("a pie", "camine", "caminando", "caminar", "caminata")),
}

FOOD: dict[str, Factor] = {
    "pollo": Factor("Pollo", 1.7, "ración", ("pollo", "alitas", "nuggets")),
    "cerdo": Factor("Cerdo", 2.4, "ración", ("cerdo", "tocino", "jamon", "chorizo", "chicharron", "salchicha")),
    "pescado": Factor("Pescado / mariscos", 2.0, "ración", ("pescado", "atun", "salmon", "mojarra", "trucha", "mariscos", "camarones")),
    "res": Factor("Carne de res", 6.5, "ración", ("carne", "hamburguesa", "bistec", "asado", "churrasco", "ternera", "costilla")),
    "huevo": Factor("Huevo", 0.6, "ración", ("huevo",)),
    "lacteos": Factor("Lácteos", 1.0, "ración", ("queso", "leche", "yogur", "yogurt")),
    "vegano": Factor("Comida vegana", 0.4, "ración", ("vegano", "vegana")),
    "vegetariano": Factor("Comida vegetariana", 0.5, "ración", ("vegetariano", "vegetariana", "ensalada", "verduras", "frutas", "lentejas", "frijoles", "garbanzos")),
}

# Categoría genérica -> categorías específicas que la desplazan.
# Ej.: "carne de pollo" cuenta como pollo, no como res.
FOOD_SUPPRESSED_BY = {
    "res": {"pollo", "cerdo", "pescado"},
    "vegetariano": {"vegano"},
}

ELECTRICITY = Factor("Electricidad", 0.126, "kWh", ("kwh",))

# ~0.25 kg CO2e por botella PET típica (aprox. 500 ml), fabricación + transporte.
BOTTLED_WATER = Factor("Agua embotellada", 0.25, "botella", ("agua embotellada", "botella de agua"))

# Referencia diaria aproximada por persona (kg CO2e/día), solo para comparar.
DAILY_REFERENCE_KG = 5.0

# --------------------------------------------------------------------------
# Utilidades de texto
# --------------------------------------------------------------------------

_DIST_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:km|kms|kilometros?)\b")
_KWH_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*kwh\b")
_CLAUSE_SPLIT = re.compile(
    r"(?<!\d),|,(?!\d)|\.(?!\d)|[;\n]+|\b(?:y|luego|despues|ademas|tambien)\b"
)
_QTY_WORDS = {"un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4,
              "cinco": 5, "seis": 6, "media": 0.5, "medio": 0.5}
_FILLERS = {
    "hoy", "ayer", "anoche", "manana", "tarde", "noche", "comi", "almorce", "cene",
    "desayune", "viaje", "fui", "me", "movi", "en", "el", "la", "los", "las", "de",
    "del", "un", "una", "a", "mi", "mis", "con", "por", "para", "que", "lo", "u", "o",
    "yo", "estuve", "tambien", "ademas", "luego", "despues", "hice", "tome", "consumi",
}


def normalize(text: str) -> str:
    """Minúsculas y sin tildes, para comparar sin preocuparse por acentos."""
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _to_float(raw: str) -> float:
    return float(raw.replace(",", "."))


def _kw_alternation(keywords: tuple[str, ...]) -> str:
    return "|".join(re.escape(k) + r"(?:s|es)?" for k in keywords)


def _find(keywords: tuple[str, ...], clause: str) -> re.Match | None:
    return re.search(r"\b(?:%s)\b" % _kw_alternation(keywords), clause)


def _is_filler(clause: str) -> bool:
    tokens = re.findall(r"[a-z]+", clause)
    return all(t in _FILLERS for t in tokens)


# --------------------------------------------------------------------------
# Resultado
# --------------------------------------------------------------------------


@dataclass
class Item:
    category: str   # "Transporte" | "Alimentación" | "Energía" | "Consumo"
    key: str
    label: str
    amount: float
    unit: str
    kg_co2e: float
    source: str


@dataclass
class Analysis:
    items: list[Item] = field(default_factory=list)
    unrecognized: list[str] = field(default_factory=list)

    @property
    def total_kg(self) -> float:
        return round(sum(i.kg_co2e for i in self.items), 2)

    def by_category(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for i in self.items:
            out[i.category] = round(out.get(i.category, 0.0) + i.kg_co2e, 2)
        return out

    def suggestion(self) -> str:
        if not self.items:
            return "Cuéntame qué comiste, cómo te moviste o cuánta energía usaste."
        top = max(self.items, key=lambda i: i.kg_co2e)
        if top.kg_co2e == 0:
            return "¡Huella cero en lo que registraste hoy! 🌿"
        if top.key == "res":
            saving = top.amount * (FOOD["res"].kg_per_unit - FOOD["pollo"].kg_per_unit)
            return f"Tu mayor impacto fue la carne de res. Cambiarla por pollo ahorraría ~{saving:.1f} kg CO₂e."
        if top.key in ("carro", "taxi", "moto", "avion"):
            saving = top.amount * (TRANSPORT[top.key].kg_per_unit - TRANSPORT["bus"].kg_per_unit)
            return f"Tu mayor impacto fue {top.label.lower()}. Hacer ese trayecto en bus ahorraría ~{saving:.1f} kg CO₂e."
        return f"Tu mayor fuente fue {top.label.lower()} ({top.kg_co2e:.1f} kg CO₂e)."


# --------------------------------------------------------------------------
# Análisis principal
# --------------------------------------------------------------------------


def _transport_item(key: str, km: float, source: str) -> Item:
    f = TRANSPORT[key]
    return Item("Transporte", key, f.label, km, f.unit, round(km * f.kg_per_unit, 3), source)


def apply_bottled_water(result: Analysis, count: float) -> None:
    """Suma al análisis las botellas de agua registradas en el campo de la UI."""
    if count <= 0:
        return
    f = BOTTLED_WATER
    result.items.append(
        Item(
            "Consumo",
            "agua_embotellada",
            f.label,
            count,
            f.unit,
            round(count * f.kg_per_unit, 3),
            f"{count:g} botella(s)",
        )
    )


def _food_quantity(food_key: str, clause: str) -> float:
    kws = _kw_alternation(FOOD[food_key].keywords)
    words = "|".join(_QTY_WORDS)
    pattern = (
        rf"\b(\d+(?:[.,]\d+)?|{words})\s+"
        rf"(?:(?:porcion(?:es)?|plato(?:s)?|racion(?:es)?)\s+de\s+)?"
        rf"(?:{kws})\b"
    )
    m = re.search(pattern, clause)
    if not m:
        return 1.0
    raw = m.group(1)
    return float(_QTY_WORDS[raw]) if raw in _QTY_WORDS else _to_float(raw)


def analyze(text: str) -> Analysis:
    """Interpreta `text` y devuelve las actividades detectadas y su CO2e."""
    result = Analysis()
    clauses = [c.strip() for c in _CLAUSE_SPLIT.split(normalize(text)) if c and c.strip()]
    pending: tuple[str, str] | None = None  # (transport_key, clause) esperando distancia

    for clause in clauses:
        matched = False

        # Energía
        kwh = _KWH_RE.search(clause)
        if kwh:
            amount = _to_float(kwh.group(1))
            result.items.append(Item("Energía", "electricidad", ELECTRICITY.label, amount,
                                     ELECTRICITY.unit, round(amount * ELECTRICITY.kg_per_unit, 3), clause))
            matched = True

        # Transporte
        dist = _DIST_RE.search(clause)
        t_key = next((k for k, f in TRANSPORT.items() if _find(f.keywords, clause)), None)
        if t_key:
            matched = True
            km = _to_float(dist.group(1)) if dist else 0.0
            if TRANSPORT[t_key].kg_per_unit == 0:
                result.items.append(_transport_item(t_key, km, clause))
            elif dist:
                result.items.append(_transport_item(t_key, km, clause))
                pending = None
            else:
                if pending:
                    result.unrecognized.append(f"Falta la distancia en km para: {TRANSPORT[pending[0]].label}")
                pending = (t_key, clause)
        elif dist and pending:
            result.items.append(_transport_item(pending[0], _to_float(dist.group(1)), f"{pending[1]}, {clause}"))
            pending = None
            matched = True

        # Alimentación
        found = [k for k, f in FOOD.items() if _find(f.keywords, clause)]
        for key in found:
            if FOOD_SUPPRESSED_BY.get(key, set()) & set(found):
                continue
            qty = _food_quantity(key, clause)
            f = FOOD[key]
            result.items.append(Item("Alimentación", key, f.label, qty, f.unit,
                                     round(qty * f.kg_per_unit, 3), clause))
            matched = True

        if not matched and not _is_filler(clause):
            result.unrecognized.append(clause)

    if pending:
        result.unrecognized.append(f"Falta la distancia en km para: {TRANSPORT[pending[0]].label}")
    return result
