import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Управление рестораном", layout="wide")

# --- ПОДКЛЮЧЕНИЕ К GOOGLE ТАБЛИЦАМ ---
def get_gspread_client():
    scope = ['https://www.googleapis.com', 'https://www.googleapis.com']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    gc = get_gspread_client()
    # ВАЖНО: Убедитесь, что ваша таблица в Google называется именно 'Restoran_DB'
    sh = gc.open('Restoran_DB')
    
    # Пытаемся открыть лист "Склад", если его нет - создаем
    try:
        worksheet = sh.worksheet("Склад")
    except:
        worksheet = sh.add_worksheet(title="Склад", rows="100", cols="20")
        worksheet.append_row(["Наименование", "Ед. изм.", "Остаток", "Цена закупки", "Цена реализации"])
except Exception as e:
    st.error(f"⚠️ Ошибка связи с Google: {e}")
    st.info("Проверьте: 1. Название таблицы 'Restoran_DB'. 2. Дали ли вы доступ для admin-sklad@...")
    st.stop()

# --- ЛОГИКА ПРИЛОЖЕНИЯ ---
st.title("👨‍🍳 Управление рестораном")

# Загружаем актуальные данные из Google
data = worksheet.get_all_records()
df = pd.DataFrame(data)

menu = st.sidebar.radio("Разделы:", ["📦 Склад", "🥗 Калькулятор блюд", "📔 Готовое Меню"])

if menu == "📦 Склад":
    st.header("📦 Товары на склад")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Наименование*")
            unit = st.selectbox("Ед. изм.*", ["кг", "л", "шт"])
        with c2:
            qty = st.number_input("Кол-во (Приход)*", min_value=0.0)
            p_buy = st.number_input("Цена закупки*", min_value=0.0)
            p_sell = st.number_input("Цена реализации*", min_value=0.0)
        
        if st.form_submit_button("На склад"):
            if name and qty > 0:
                worksheet.append_row([name, unit, qty, p_buy, p_sell])
                st.success(f"Товар '{name}' успешно записан в Google Таблицу!")
                st.rerun()

    st.subheader("📊 НА СКЛАДЕ (Данные из Google)")
    if not df.empty:
        # Считаем суммы для отчета
        df["Сумма закупки"] = df["Остаток"].astype(float) * df["Цена закупки"].astype(float)
        df["Сумма реализации"] = df["Остаток"].astype(float) * df["Цена реализации"].astype(float)
        st.dataframe(df, use_container_width=True)
        
        st.write(f"💰 **Общая стоимость склада (закупка): {df['Сумма закупки'].sum():.2f}**")
    else:
        st.write("Склад пока пуст. Добавьте первый товар!")

# Разделы Калькулятора и Меню добавим в следующем шаге, как только проверим Склад!
