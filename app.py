import pandas as pd
import streamlit as st
import plotly.express as px


df = pd.read_csv('data/sales_data_sample.csv', encoding='latin1')

#Side bar
def main():
    st.set_page_config(page_title="Gasto Mensual Visualizer", layout="wide")

    st.title("💰 Gasto Mensual Visualizer")
    st.write("Elegí como visualizar tus gastos nuestro programa de graficos de gastos: ")
    
    st.sidebar.header("🏦 Navegación rápida")
    seccion = st.sidebar.radio("Ir a la sección:", ["Inicio", "Análisis de ventas", "Local y visitante"])

    if seccion == "Inicio":
        st.subheader("🪙 Bienvenido")
        st.write("Explorá datos de partidos entre selecciones nacionales.")
        st.dataframe(df.head(10))

    st.divider()
    ############ APARTADO PARA ANÁLISIS DE VENTAS
    if seccion == 'Análisis de ventas':
        st.set_page_config(page_title="Dashboard de Ventas", layout="wide")

        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            año = st.selectbox("Año", sorted(df["YEAR_ID"].unique()))
        with col2:
            pais = st.selectbox("País", ["Todos"] + sorted(df["COUNTRY"].unique()))
        with col3:
            tamaño = st.selectbox("Tamaño de contrato", ["Todos", "Small", "Medium", "Large"])
        
        

                
        # se filtran por categoria, fecha, monto

        # Filtro por año, país y tamaño de contrato
        df_filtrado = df[df["YEAR_ID"] == año]

        if pais != "Todos":
            df_filtrado = df_filtrado[df_filtrado["COUNTRY"] == pais]

        if tamaño != "Todos":
            df_filtrado = df_filtrado[df_filtrado["DEALSIZE"] == tamaño]
            
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Ventas", f"${df_filtrado['SALES'].sum():,.2f}")
        with col2:
            st.metric("📦 Productos Vendidos", int(df_filtrado['QUANTITYORDERED'].sum()))
        with col3:
            st.metric("🧾 Ticket Promedio", f"${df_filtrado['SALES'].mean():.2f}")

        
        st.subheader("📦 Ventas por línea de producto")
        ventas_por_categoria = df_filtrado.groupby("PRODUCTLINE")["SALES"].sum().reset_index().sort_values(by="SALES", ascending=False)

        fig = px.bar(ventas_por_categoria, x="PRODUCTLINE", y="SALES", title="Ventas por categoría")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📆 Ventas por mes")
        ventas_por_mes = df_filtrado.groupby("MONTH_ID")["SALES"].sum().reset_index()

        fig2 = px.line(ventas_por_mes, x="MONTH_ID", y="SALES", markers=True, title="Ventas por mes")
        st.plotly_chart(fig2, use_container_width=True)
        
        
        st.subheader("👥 Top 10 clientes por ventas")
        top_clientes = df_filtrado.groupby("CUSTOMERNAME")["SALES"].sum().reset_index().sort_values(by="SALES", ascending=True).head(10)

        fig3 = px.bar(top_clientes, x="SALES", y="CUSTOMERNAME", title="Top clientes", orientation='h')
        st.plotly_chart(fig3, use_container_width=True)



        # archivo = st.file_uploader("📂 Subí tu archivo CSV ", type=['csv']) 

        # if archivo is not None:
        #     try:
        #         df = pd.read_csv(archivo, encoding='utf-8')
        #     except UnicodeDecodeError:
        #         archivo.seek(0)  # Reiniciar el puntero del archivo
        #         df = pd.read_csv(archivo, encoding='latin1')
        #     st.dataframe(df.head())

        #     st.dataframe(df.unique('PRODUCTLINE'))
        
if __name__ == '__main__':
    main()