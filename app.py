import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

def main():
    st.set_page_config(page_title="Analizador de Ventas", layout="wide", page_icon="📊")

    st.title("📊 Analizador de Ventas Interactivo")
    st.write("Herramienta para analizar datos de ventas de manera visual")
    
    with st.sidebar:
        st.header("🗺️ Navegación")
        seccion = st.radio("Ir a:", 
                         ["Resumen", "Análisis de Ventas", "Distribución Geográfica", 
                          "Análisis Temporal", "Comparativas", "Explorador de Datos"])
        
        st.header("🔍 Filtros Globales")
        mostrar_filtros = st.checkbox("Mostrar filtros globales", True)
    
    archivo = st.file_uploader("📁 Sube tus datos de ventas (CSV o Excel)", type=['csv', 'xlsx']) 

    if archivo is not None:
        try:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo, encoding='utf-8')
            else:  
                df = pd.read_excel(archivo)
        except UnicodeDecodeError:
            archivo.seek(0)
            df = pd.read_csv(archivo, encoding='latin1')
    else:
        df = pd.read_csv('data/sales_data_sample.csv', encoding='latin1')
        
        st.info("Se están utilizando datos de ejemplo. Sube tu propio archivo para analizar tus datos.")  
          
        df = limpiar_datos(df)

        if mostrar_filtros:
            with st.expander("🔍 Filtros Globales", expanded=False):
                cols = st.columns(3)
                with cols[0]:
                    años = st.multiselect("Años", sorted(df["YEAR_ID"].unique()), default=sorted(df["YEAR_ID"].unique()))
                with cols[1]:
                    paises = st.multiselect("Países", sorted(df["COUNTRY"].unique()), default=sorted(df["COUNTRY"].unique()))
                with cols[2]:
                    tamanos = st.multiselect("Tamaños de venta", sorted(df["DEALSIZE"].unique()), default=sorted(df["DEALSIZE"].unique()))
            
            df = df[df["YEAR_ID"].isin(años)]
            df = df[df["COUNTRY"].isin(paises)]
            df = df[df["DEALSIZE"].isin(tamanos)]

        if seccion == "Resumen":
            mostrar_resumen(df)
        
        elif seccion == 'Análisis de Ventas':
            analisis_ventas(df)
        
        elif seccion == 'Distribución Geográfica':
            distribucion_geografica(df)
        
        elif seccion == 'Análisis Temporal':
            analisis_temporal(df)
        
        elif seccion == 'Comparativas':
            comparativas(df)
        
        elif seccion == 'Explorador de Datos':
            explorador_datos(df)

def limpiar_datos(df):

    columnas_numericas = ['QUANTITYORDERED', 'PRICEEACH', 'SALES', 'MSRP', 'QTR_ID']
    
    for col in columnas_numericas:
        if col in df.columns:
            try:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
            except Exception as e:
                st.warning(f"No se pudo convertir la columna {col} a numérico: {str(e)}")
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('[^\d.]', '', regex=True), errors='coerce')
    
    if 'ORDERDATE' in df.columns:
        try:
            df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], 
                                           format='mixed', 
                                           dayfirst=True,
                                           errors='coerce')
            
            if pd.api.types.is_datetime64_any_dtype(df['ORDERDATE']):
                df['DIA'] = df['ORDERDATE'].dt.day
                df['DIA_SEMANA'] = df['ORDERDATE'].dt.day_name()
                df['MES'] = df['ORDERDATE'].dt.month
                df['AÑO'] = df['ORDERDATE'].dt.year
        except Exception as e:
            st.warning(f"No se pudo convertir ORDERDATE a fecha: {str(e)}")
    
    if 'MONTH_ID' not in df.columns and 'MES' in df.columns:
        df['MONTH_ID'] = df['MES']
    if 'YEAR_ID' not in df.columns and 'AÑO' in df.columns:
        df['YEAR_ID'] = df['AÑO']
    
    columnas_criticas = ['ORDERNUMBER', 'CUSTOMERNAME', 'PRODUCTLINE', 'SALES']
    for col in columnas_criticas:
        if col in df.columns:
            filas_antes = len(df)
            df = df.dropna(subset=[col], how='any')
            filas_despues = len(df)
            if filas_antes != filas_despues:
                st.warning(f"Se eliminaron {filas_antes - filas_despues} filas con valores faltantes en {col}")
    
    columnas_categoricas = ['PRODUCTLINE', 'STATUS', 'DEALSIZE', 'COUNTRY', 'TERRITORY']
    for col in columnas_categoricas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    
    if 'QUANTITYORDERED' in df.columns:
        df = df[df['QUANTITYORDERED'] > 0]
    if 'SALES' in df.columns:
        df = df[df['SALES'] > 0]
    
    duplicados = df.duplicated()
    if duplicados.any():
        st.warning(f"Se eliminaron {duplicados.sum()} filas duplicadas")
        df = df[~duplicados]
    
    df = df.reset_index(drop=True)
    
    return df

def mostrar_resumen(df):
    st.subheader("📌 Resumen Ejecutivo")
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("Ventas Totales", f"${df['SALES'].sum():,.2f}")
    with cols[1]:
        st.metric("Pedidos Totales", df['ORDERNUMBER'].nunique())
    with cols[2]:
        st.metric("Clientes Únicos", df['CUSTOMERNAME'].nunique())
    with cols[3]:
        avg_order = df.groupby('ORDERNUMBER')['SALES'].sum().mean()
        st.metric("Valor Promedio Pedido", f"${avg_order:,.2f}")
    
    with st.expander("📋 Vista Previa de Datos (10 filas)", expanded=False):
        st.dataframe(df.head(10))
        
    st.subheader("📊 Distribuciones Rápidas")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names='PRODUCTLINE', title='Ventas por Línea de Producto')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(df, names='STATUS', title='Distribución por Estado de Pedido')
        st.plotly_chart(fig, use_container_width=True)

def analisis_ventas(df):
    st.subheader("📈 Análisis Detallado de Ventas")
    
    cols = st.columns(3)
    with cols[0]:
        linea_producto = st.selectbox("Línea de Producto", ["Todas"] + sorted(df["PRODUCTLINE"].unique()))
    with cols[1]:
        territorio = st.selectbox("Territorio", ["Todos"] + sorted(df["TERRITORY"].unique()))
    with cols[2]:
        estado = st.selectbox("Estado de Pedido", ["Todos"] + sorted(df["STATUS"].unique()))
    
    df_filtrado = df.copy()
    if linea_producto != "Todas":
        df_filtrado = df_filtrado[df_filtrado["PRODUCTLINE"] == linea_producto]
    if territorio != "Todos":
        df_filtrado = df_filtrado[df_filtrado["TERRITORY"] == territorio]
    if estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["STATUS"] == estado]
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("Ventas Totales", f"${df_filtrado['SALES'].sum():,.2f}")
    with cols[1]:
        st.metric("Cantidad Vendida", int(df_filtrado['QUANTITYORDERED'].sum()))
    with cols[2]:
        precio_promedio = df_filtrado['PRICEEACH'].mean() if 'PRICEEACH' in df_filtrado else df_filtrado['SALES'].sum()/df_filtrado['QUANTITYORDERED'].sum()
        st.metric("Precio Promedio", f"${precio_promedio:,.2f}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Por Producto", "En el Tiempo", "Top Clientes", "Análisis de Precios"])
    
    with tab1:
        ventas_por_producto = df_filtrado.groupby("PRODUCTCODE").agg({
            'SALES': 'sum',
            'QUANTITYORDERED': 'sum',
            'PRICEEACH': 'mean'
        }).reset_index().sort_values('SALES', ascending=False).head(20)
        
        fig = px.bar(ventas_por_producto, x="PRODUCTCODE", y="SALES", 
                    title="Productos Más Vendidos", hover_data=['QUANTITYORDERED', 'PRICEEACH'])
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        if 'MONTH_ID' in df_filtrado and 'YEAR_ID' in df_filtrado:
            agrupamiento = st.radio("Agrupamiento Temporal:", ["Mensual", "Trimestral", "Anual"])
            
            if agrupamiento == "Mensual":
                df_tiempo = df_filtrado.groupby(['YEAR_ID', 'MONTH_ID'])['SALES'].sum().reset_index()
                df_tiempo['Periodo'] = df_tiempo['YEAR_ID'].astype(str) + '-' + df_tiempo['MONTH_ID'].astype(str).str.zfill(2)
                eje_x = 'Periodo'
            elif agrupamiento == "Trimestral":
                df_tiempo = df_filtrado.groupby(['YEAR_ID', 'QTR_ID'])['SALES'].sum().reset_index()
                df_tiempo['Periodo'] = df_tiempo['YEAR_ID'].astype(str) + '-T' + df_tiempo['QTR_ID'].astype(str)
                eje_x = 'Periodo'
            else:  
                df_tiempo = df_filtrado.groupby('YEAR_ID')['SALES'].sum().reset_index()
                eje_x = 'YEAR_ID'
            
            fig = px.line(df_tiempo, x=eje_x, y="SALES", markers=True, 
                        title=f"Tendencia de Ventas ({agrupamiento})")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Datos de mes y año no disponibles para análisis temporal")
    
    with tab3:
        top_clientes = df_filtrado.groupby("CUSTOMERNAME").agg({
            'SALES': 'sum',
            'ORDERNUMBER': 'nunique'
        }).reset_index().sort_values('SALES', ascending=False).head(10)
        
        fig = px.bar(top_clientes, x="SALES", y="CUSTOMERNAME", 
                    orientation='h', hover_data=['ORDERNUMBER'],
                    title="Mejores Clientes por Ventas")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        if 'PRICEEACH' in df_filtrado and 'MSRP' in df_filtrado:
            df_filtrado['DESCUENTO'] = (df_filtrado['MSRP'] - df_filtrado['PRICEEACH']) / df_filtrado['MSRP'] * 100
            
            fig = px.scatter(df_filtrado, x="QUANTITYORDERED", y="PRICEEACH",
                            color="PRODUCTLINE", size="SALES",
                            hover_data=['PRODUCTCODE', 'DESCUENTO'],
                            title="Análisis Precio vs Cantidad")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Datos de precios no disponibles para análisis")

def distribucion_geografica(df):
    st.subheader("🌍 Distribución Geográfica de Ventas")
    
    ventas_por_pais = df.groupby("COUNTRY").agg({
        'SALES': 'sum',
        'ORDERNUMBER': 'nunique',
        'CUSTOMERNAME': 'nunique'
    }).reset_index().sort_values('SALES', ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(ventas_por_pais, values="SALES", names="COUNTRY", 
                    title="Distribución de Ventas por País")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.choropleth(ventas_por_pais, locations="COUNTRY", 
                           locationmode="country names", color="SALES",
                           hover_data=['ORDERNUMBER', 'CUSTOMERNAME'],
                           title="Mapa de Calor de Ventas por País")
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(ventas_por_pais, 
                column_order=["COUNTRY", "SALES", "ORDERNUMBER", "CUSTOMERNAME"],
                column_config={
                    "SALES": st.column_config.NumberColumn(format="$%.2f"),
                    "ORDERNUMBER": "Pedidos",
                    "CUSTOMERNAME": "Clientes"
                },
                hide_index=True, 
                use_container_width=True)

def analisis_temporal(df):
    st.subheader("⏳ Patrones Temporales de Ventas")
    
    if 'MONTH_ID' in df and 'YEAR_ID' in df:
        año_seleccionado = st.selectbox("Seleccione Año para Vista Detallada", sorted(df["YEAR_ID"].unique()))
        
        datos_mensuales = df[df['YEAR_ID'] == año_seleccionado].groupby('MONTH_ID')['SALES'].sum().reset_index()
        
        fig = px.line(datos_mensuales, x="MONTH_ID", y="SALES", markers=True,
                     title=f"Tendencia Mensual de Ventas para {año_seleccionado}")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Información de fecha no disponible para análisis temporal")

def comparativas(df):
    st.subheader("🔄 Comparativas de Ventas")
    
    col1, col2 = st.columns(2)
    with col1:
        año1 = st.selectbox("Año 1", sorted(df["YEAR_ID"].unique()))
    with col2:
        año2 = st.selectbox("Año 2", [x for x in sorted(df["YEAR_ID"].unique()) if x != año1])
    
    comparacion_productos = df[df['YEAR_ID'].isin([año1, año2])].groupby(['YEAR_ID', 'PRODUCTLINE'])['SALES'].sum().reset_index()
    
    fig = px.bar(comparacion_productos, x="PRODUCTLINE", y="SALES", color="YEAR_ID",
                barmode="group", title=f"Comparativa por Línea de Producto: {año1} vs {año2}")
    st.plotly_chart(fig, use_container_width=True)
    
    pivot_comp = comparacion_productos.pivot(index='PRODUCTLINE', columns='YEAR_ID', values='SALES').reset_index()
    pivot_comp['Crecimiento'] = (pivot_comp[año2] - pivot_comp[año1]) / pivot_comp[año1] * 100
    
    fig = px.bar(pivot_comp, x="PRODUCTLINE", y="Crecimiento", 
                title=f"Porcentaje de Crecimiento por Línea de Producto ({año1} a {año2})")
    st.plotly_chart(fig, use_container_width=True)

def explorador_datos(df):
    st.subheader("🔍 Explorador de Datos")
    
    columnas_a_mostrar = st.multiselect("Seleccione columnas a mostrar", 
                                       df.columns.tolist(), 
                                       default=['ORDERNUMBER', 'ORDERDATE', 'CUSTOMERNAME', 'COUNTRY', 'PRODUCTLINE', 'QUANTITYORDERED', 'PRICEEACH', 'SALES'])
    
    df_filtrado = df[columnas_a_mostrar]
    
    columnas_numericas = df_filtrado.select_dtypes(include=['number']).columns.tolist()
    if columnas_numericas:
        columna_num = st.selectbox("Seleccione columna numérica para análisis", columnas_numericas)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("Estadísticas Descriptivas")
            st.dataframe(df_filtrado[columna_num].describe())
        with col2:
            fig = px.histogram(df_filtrado, x=columna_num, 
                              title=f"Distribución de {columna_num}")
            st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_filtrado, use_container_width=True)

if __name__ == '__main__':
    main()