"""EcoTrack: interfaz Streamlit. Ejecuta con: streamlit run app.py"""
import pandas as pd
import streamlit as st

from ecotrack.calculator import DAILY_REFERENCE_KG, analyze, apply_bottled_water

st.set_page_config(page_title="EcoTrack", page_icon="🌱", layout="centered")

EXAMPLES = [
    "Hoy comí carne y viajé 20km en bus",
    "Almorcé 2 porciones de pollo, fui 8 km en carro y gasté 3 kWh",
    "Desayuné huevo y ensalada, y fui en bici al trabajo",
]

if "texto" not in st.session_state:
    st.session_state["texto"] = EXAMPLES[0]
if "historial" not in st.session_state:
    st.session_state["historial"] = []


def _use_example(text: str) -> None:
    st.session_state["texto"] = text


st.title("🌱 EcoTrack")
st.caption("Cuéntame tu día en lenguaje natural y estimo tu huella de carbono.")

st.text_area("¿Qué hiciste hoy?", key="texto", height=110)

botellas = st.number_input(
    "¿Cuántas veces tomaste agua embotellada?",
    min_value=0,
    step=1,
    value=0,
    help="Cada botella suma ~0.25 kg CO₂e (aproximación).",
)

st.write("Prueba con un ejemplo:")
cols = st.columns(len(EXAMPLES))
for col, ex in zip(cols, EXAMPLES):
    col.button(ex, on_click=_use_example, args=(ex,), width="stretch")

if st.button("Calcular mi huella", type="primary"):
    res = analyze(st.session_state["texto"])
    apply_bottled_water(res, botellas)

    if not res.items:
        st.warning("No pude identificar actividades. Prueba con algo como: 'comí pollo y viajé 10 km en bus'.")
    else:
        st.session_state["historial"].append((st.session_state["texto"], res.total_kg))

        c1, c2 = st.columns(2)
        c1.metric("Huella estimada", f"{res.total_kg:.2f} kg CO₂e")
        c2.metric("Vs. referencia diaria", f"{res.total_kg / DAILY_REFERENCE_KG * 100:.0f} %",
                  help=f"Referencia aproximada: {DAILY_REFERENCE_KG:.0f} kg CO₂e por persona al día.")
        st.progress(min(res.total_kg / DAILY_REFERENCE_KG, 1.0))
        st.success(res.suggestion())

        st.subheader("Detalle")
        st.dataframe(
            pd.DataFrame(
                [{"Categoría": i.category, "Actividad": i.label,
                  "Cantidad": f"{i.amount:g} {i.unit}", "kg CO₂e": round(i.kg_co2e, 2)}
                 for i in res.items]
            ),
            hide_index=True,
            width="stretch",
        )
        st.bar_chart(pd.Series(res.by_category(), name="kg CO₂e"))

    if res.unrecognized:
        st.info("No pude interpretar: " + "; ".join(res.unrecognized))

if st.session_state["historial"]:
    with st.expander("Historial de esta sesión"):
        for texto, kg in reversed(st.session_state["historial"]):
            st.write(f"**{kg:.2f} kg** — {texto}")

st.divider()
st.caption("Los factores de emisión son aproximaciones para un MVP, no cifras oficiales.")
