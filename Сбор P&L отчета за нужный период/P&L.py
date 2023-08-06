import time
import pymysql.cursors
import xlsxwriter
import re

print('введи ID филиала')
s = ' ,'+', '+','
salon = int(input())
print('Введи год или годы за который\е нужна выгрузка через заяптую')
year0 = set(map(int, re.split(',| ,|, | , ', str(input()))))
year = sorted(list(year0))
config = {
    'user': '',
    'password': '',
    'host': '',
    'database': ''
}
try:
    connection = pymysql.connect(**config)
except Exception as e:
    print(f"Не удалось установить соединение с базой данных: {e}")

try:
    workbook = xlsxwriter.Workbook(f'{salon}.xlsx')
    for years in range(len(year)):
        with connection.cursor() as cursor:
            sql = f"set @year = '{year[years]}', @salon_id = {salon};"
            sql2 = f"Select CASE " \
                   f"WHEN title = 'expenses.purchase_of_consumables' THEN 'Закупка материалов'" \
                   f"WHEN title = 'expenses.purchase_of_products' THEN 'Закупка товаров'" \
                   f"WHEN title = 'expenses.salary_of_staff' THEN 'Зарплата персонала'" \
                   f"WHEN title = 'expenses.taxes_and_fees' THEN 'Налоги и сборы'" \
                   f"WHEN title = 'expenses.providing_services' THEN 'Оказание услуг'" \
                   f"WHEN title = 'expenses.sale_of_memberships' THEN 'Продажа абонементов'" \
                   f"WHEN title = 'expenses.sales_of_products' THEN 'Продажа товаров'" \
                   f"WHEN title = 'expenses.other_income' THEN 'Прочие доходы'"\
                   f"WHEN title = 'expenses.other_expenditures' THEN 'Прочие расходы'" \
                   f"WHEN title = 'expenses.refill' THEN 'Пополнение счета'" \
                   f"WHEN title = 'expenses.acquiring_fee' THEN 'Комиссия за эквайринг'" \
                   f"WHEN title = 'expenses.gift_cards_sale' THEN 'Продажа сертификатов'" \
                   f"ELSE title END 'статья платежа'," \
                   f"if(january is null, 0, january) 'Январь' , " \
                   f"if(february is null, 0, february) 'Февраль'," \
                   f"if(march is null,0, march) 'Март'," \
                   f"if(april is null, 0, april) 'Апрель'," \
                   f"if(may is null,0, may) 'Май'," \
                   f"if(june is null, 0, june) 'Июнь'," \
                   f"if(july is null, 0,july) 'Июль'," \
                   f"if(august is null, 0, august) 'Август'," \
                   f"if(september is null, 0, september) 'Сентябрь'," \
                   f"if(october is null,0,october) 'Октябрь'," \
                   f"if(november is null, 0, november) 'Ноябрь'," \
                   f"if(december is null, 0, december) 'Декабрь'," \
                   f"if(january is null,0,january)+if(february is null,0,february)+" \
                   f"if(march is null,0,march)+if(april is null,0,april)+" \
                   f"if(may is null,0,may)+if(june is null,0,june)+if(july is null,0,july)" \
                   f"+if(august is null,0,august)+" \
                   f"if(september is null,0,september)+if(october is null,0,october)" \
                   f"+if(november is null,0, november)+" \
                   f"if(december is null,0,december) 'годовой' " \
                   f"FROM expenses e " \
                   f"join expenses_salons_link esl on e.id = esl.expenses_id and esl.salon_id = @salon_id " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"if(sum(amount) is null, 0, sum(amount)) january " \
                   f"from transactions t " \
                   f"join expenses e on e.id = t.type where account_id in " \
                   f"(select id from accounts where salon_id = @salon_id)" \
                   f"AND  year(date) = @year and month(date) = '1' and cancel = 0 group by type) jan " \
                   f"on e.id = jan.type " \
                   f"left join (select t.type 'type', sum(amount) february " \
                   f"from transactions t join expenses e on e.id = t.type where account_id in " \
                   f"(select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '2' and cancel = 0 " \
                   f"group by type) feb on e.id = feb.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) march " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in " \
                   f"(select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '3' and cancel = 0 " \
                   f"group by type) march on e.id = march.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) april " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '4' and cancel = 0 " \
                   f"group by type) apr on e.id = apr.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) may " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in " \
                   f"(select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '5' and cancel = 0 " \
                   f"group by type) may on e.id = may.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) june " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '6' and cancel = 0 " \
                   f"group by type) june on e.id = june.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) july " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '7' and cancel = 0 " \
                   f"group by type) july on e.id = july.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) august " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '8' and cancel = 0 " \
                   f"group by type) aug on e.id = aug.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) september " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '9' and cancel = 0 " \
                   f"group by type) sep on e.id = sep.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) october " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '10' and cancel = 0 " \
                   f"group by type) oct on e.id = oct.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) november " \
                   f"from transactions t join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '11' and cancel = 0 " \
                   f"group by type) nov on e.id = nov.type " \
                   f"left join " \
                   f"(select t.type 'type', " \
                   f"sum(amount) december " \
                   f"from transactions t " \
                   f"join expenses e on e.id = t.type " \
                   f"where account_id in (select id from accounts where salon_id = @salon_id) " \
                   f"AND  year(date) = @year and month(date) = '12' and cancel = 0 " \
                   f"group by type) decem on e.id = decem.type " \
                   f"group by e.id; "
            cursor.execute(sql)
            cursor.execute(sql2)
            result = cursor.fetchall()
            worksheet_name = str(year[years])
            worksheet = workbook.add_worksheet(worksheet_name)
            columns = [i[0] for i in cursor.description]
            for col, column_name in enumerate(columns):
                worksheet.write(0, col, column_name)

            for row, data in enumerate(result, start=1):
                for col, value in enumerate(data):
                    worksheet.write(row, col, value)
    workbook.close()
    print(f"Результат запроса сохранен в файл '{salon}.xlsx'.")
except Exception as e:
    print(f"Не удалось выполнить запрос: {e}")
finally:

    connection.close()