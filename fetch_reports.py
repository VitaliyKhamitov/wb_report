import os
import json
import requests
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Авторизация Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1g6OF7IOyOnwLf5Wrxzm-mB55e-vkMe0mxNrPXYwzHOM/")
worksheet = spreadsheet.worksheet("Реализация")

# Токен Wildberries
TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwNTIwdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2ODQwOTUyOCwiaWQiOiIwMTk4MTE5My02M2RjLTdiMDEtODk0Ny0zNmM2ZGFkOTUxZTAiLCJpaWQiOjg0NTIwNzMzLCJvaWQiOjEwODM5MjMsInMiOjEwNzM3NTAwNzYsInNpZCI6IjVhN2I1ZGJmLTUxNGItNGU5Yy04MWZkLWVkZDg5MDYzNjMxNCIsInQiOmZhbHNlLCJ1aWQiOjg0NTIwNzMzfQ.Cs5LCtopYH4LmqYLUJ2a1Evy5fjfb4V1dTuGDl4YaI3-B-HgF3dtgCN20OWvlzcXfeU1meuT510aVb2xPH2rqQ"

# Получение данных
def fetch_data(date_from, date_to):
    url = "https://statistics.wildberries.ru/api/v5/supplier/reportDetailByPeriod"
    headers = {"Authorization": TOKEN}
    params = {"dateFrom": date_from, "dateTo": date_to}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    return []

# Фильтрация нужных столбцов
def filter_fields(data):
    keep_indexes = [0, 2, 3, 5, 7, 8, 9, 10, 11, 12, 15, 26, 27, 28, 29, 30,
                    31, 32, 33, 34, 35, 37, 40, 41, 42, 43, 44, 50, 51]
    header = list(data[0].keys())
    filtered_header = [header[i] for i in keep_indexes]
    filtered_data = [[str(row.get(col, "")) for col in filtered_header] for row in data]
    return [filtered_header] + filtered_data

# Загрузка в Google Таблицу
def upload_to_sheet(filtered_data):
    worksheet.clear()
    worksheet.append_rows(filtered_data, value_input_option="USER_ENTERED")

# Основной цикл по неделям
def main():
    start_date = datetime(2024, 1, 29)
    end_date = datetime.today()
    all_data = []

    while start_date < end_date:
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = (start_date + timedelta(days=6)).strftime("%Y-%m-%d")
        print(f"🔄 {date_from} — {date_to}")
        week_data = fetch_data(date_from, date_to)
        if week_data:
            all_data.extend(week_data)
        start_date += timedelta(days=7)

    if all_data:
        filtered = filter_fields(all_data)
        upload_to_sheet(filtered)
        print("✅ Готово: данные выгружены.")
    else:
        print("⚠️ Нет данных для выгрузки.")

if __name__ == "__main__":
    main()
