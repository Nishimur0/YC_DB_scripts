import time
import pymysql.cursors
import xlsxwriter

config = { #заполнить доступы к БД.
    'user': '',
    'password': '',
    'host': '',
    'database': '',
}

while True:
    try:
        connection = pymysql.connect(**config)
        break
    except Exception as e:
        print(f"Не удалось установить соединение с базой данных: {e}")
        time.sleep(3600)

try:
    with connection.cursor() as cursor:
        sql = "select  balance - sum(amount) as bal, " \
              "a.title as 'Название кассы', " \
              "a.salon_id as 'ID филиала', " \
              "a.id as 'ID кассы', " \
              "CONCAT('update accounts set balance = balance + (', balance - sum(amount), ') where id = ', a.id, ';'), "\
              "concat(current_date,' ', current_time) as 'дата запроса'" \
              "from transactions t " \
              "join accounts a on t.account_id = a.id " \
              "where salon_id in (select salon_id from salons_groups_link where group_id = 238) " \
              "and cancel = 0 " \
              "group by  account_id " \
              "having bal != 0;"
        cursor.execute(sql)
        result = cursor.fetchall()
        if not result:
            print("Результат запроса пустой.")
            time.sleep(3600)
        else:
            workbook = xlsxwriter.Workbook('result.xlsx')
            worksheet = workbook.add_worksheet()

            columns = [i[0] for i in cursor.description]
            for col, column_name in enumerate(columns):
                worksheet.write(0, col, column_name)

            for row, data in enumerate(result, start=1):
                for col, value in enumerate(data):
                    worksheet.write(row, col, value)

            workbook.close()
            print("Результат запроса сохранен в файл 'result.xlsx'.")
except Exception as e:
    print(f"Не удалось выполнить запрос: {e}")
finally:
    connection.close()