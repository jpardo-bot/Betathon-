import streamlit as st
import pandas as pd
import random
from io import BytesIO

st.set_page_config(page_title="Asignador IA", layout="wide")

st.title("🤖 Asignador Inteligente de Evaluadores")

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
st.sidebar.header("⚙️ Configuración")

tipo_cruce = st.sidebar.selectbox(
    "Tipo de cruce",
    ["area", "cargo"]
)

cantidad = st.sidebar.number_input(
    "Cantidad de evaluadores",
    min_value=1,
    max_value=5,
    value=2
)

excluir_mismo_jefe = st.sidebar.checkbox(
    "Excluir mismo jefe",
    value=True
)

# -----------------------------
# SUBIR ARCHIVO
# -----------------------------
archivo = st.file_uploader(
    "📂 Sube tu archivo Excel",
    type=["xlsx"]
)

if archivo:

    df = pd.read_excel(archivo)

    st.subheader("📊 Datos cargados")
    st.dataframe(df)

    columnas_necesarias = [
        "Cedula",
        "Cedula_Jefe",
        "Cargo",
        "Area"
    ]

    if not all(col in df.columns for col in columnas_necesarias):
        st.error(
            f"El archivo debe tener estas columnas: {columnas_necesarias}"
        )
        st.stop()

    # ---------------------------------------------------
    # GENERAR EVALUADORES PARES
    # ---------------------------------------------------
    def generar_evaluaciones(df):

        resultado = []

        for _, persona in df.iterrows():

            cedula = persona["Cedula"]
            jefe = persona["Cedula_Jefe"]
            cargo = persona["Cargo"]
            area = persona["Area"]

            candidatos = df[df["Cedula"] != cedula]

            if tipo_cruce == "cargo":
                candidatos = candidatos[
                    candidatos["Cargo"] == cargo
                ]

            if tipo_cruce == "area":
                candidatos = candidatos[
                    candidatos["Area"] == area
                ]

            if excluir_mismo_jefe:
                candidatos = candidatos[
                    candidatos["Cedula_Jefe"] != jefe
                ]

            candidatos = candidatos.sample(frac=1)

            seleccionados = candidatos["Cedula"] \
                .head(cantidad) \
                .tolist()

            while len(seleccionados) < cantidad:
                seleccionados.append("")

            resultado.append([
                cedula,
                cargo,
                area,
                jefe,
                *seleccionados
            ])

        columnas = [
            "Cedula",
            "Cargo",
            "Area",
            "Jefe"
        ] + [
            f"Evaluador {i}"
            for i in range(1, cantidad + 1)
        ]

        return pd.DataFrame(resultado, columns=columnas)

    # ---------------------------------------------------
    # GENERAR EVALUACIÓN ASCENDENTE
    # ---------------------------------------------------
    def generar_ascendente(df):

        ascendente = df.copy()

        ascendente["Evaluador_Ascendente"] = ascendente["Cedula_Jefe"]

        return ascendente[
            [
                "Cedula",
                "Cargo",
                "Area",
                "Cedula_Jefe",
                "Evaluador_Ascendente"
            ]
        ]

    # ---------------------------------------------------
    # BOTÓN EVALUADORES PARES
    # ---------------------------------------------------
    if st.button("✨ Generar evaluadores"):

        df_resultado = generar_evaluaciones(df)

        st.success("Asignación completada ✅")
        st.dataframe(df_resultado)

        buffer = BytesIO()

        df_resultado.to_excel(
            buffer,
            index=False,
            engine='openpyxl'
        )

        buffer.seek(0)

        st.download_button(
            "📥 Descargar resultado",
            data=buffer,
            file_name="evaluaciones.xlsx"
        )

    # ---------------------------------------------------
    # BOTÓN EVALUACIÓN ASCENDENTE
    # ---------------------------------------------------
    if st.button("⬆️ Generar evaluación ascendente"):

        df_ascendente = generar_ascendente(df)

        st.success("Evaluación ascendente generada ✅")
        st.dataframe(df_ascendente)

        buffer = BytesIO()

        df_ascendente.to_excel(
            buffer,
            index=False,
            engine='openpyxl'
        )

        buffer.seek(0)

        st.download_button(
            "📥 Descargar ascendente",
            data=buffer,
            file_name="evaluacion_ascendente.xlsx"
        )

    # ---------------------------------------------------
    # EQUIPOS POR JEFE
    # ---------------------------------------------------
    if st.button("👥 Generar equipos por jefe"):

        equipos = df.groupby(
            "Cedula_Jefe"
        )["Cedula"].apply(
            lambda x: ", ".join(map(str, x))
        ).reset_index()

        equipos.columns = [
            "Jefe",
            "Equipo"
        ]

        st.success("La estructura de tu evaluación está lista ✅")
        st.dataframe(equipos)

        buffer = BytesIO()

        equipos.to_excel(
            buffer,
            index=False,
            engine='openpyxl'
        )

        buffer.seek(0)

        st.download_button(
            "📥 Descargar estructura",
            data=buffer,
            file_name="equipos.xlsx"
        )
