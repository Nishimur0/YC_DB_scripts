import time
import pymysql.cursors
import copy
from datetime import  datetime
import tkinter as tk
from tkinter import scrolledtext
from tkcalendar import DateEntry
import os
from babel import numbers

#Надо не забыть креды спрятать, если буду переносить в flusk
config = {
    'user': 'tech_support_ro',
    'password': '8maIo&tF@q0lQ9',
    'host': 'bi.yclients.cloud',
    'database': 'salon'
}

#Подруба к БД (Работает только при подключенном офисном ВПН
try:
    connection = pymysql.connect(**config)
except Exception as e:
    print(f"Не удалось установить соединение с базой данных: {e}")

records_with_resources_str = []
records_from_google_list = ''
invoice_records_list = []
invoice_records_list_str = ''
order_id_record_invoices_str =''
order_id_record_invoices_list =[]
transactions = []
transactions_amount_tup = ''
records_from_google_list_str = ''
visit_ids_str =''
medicine_appontment_str = ''
medicine_appontment_list = []
resources_custom_fields_values_list = []
resources_custom_fields_values_str = ''
custom_fields_values_id_str = ''
cfv_id =[]
def validate_date(date):
    try:
        new_date = datetime.strptime(date, '%Y-%m-%d').date()
        return str(new_date)
    except ValueError:
        console_text.insert(tk.END, "Некорректная дата \n")
        raise ValueError('Некорректная дата')


class Records:
    #Создание экземпляра класса. Дата создания и пользователь могут быть пустыми.
    #Их буду использовать только если требуется удаление всех записей конкретного пользователя
    #Или созданные в конкретное время
    def __init__(self, date_from, date_to, salon_id, deleted, cdate_from=None, cdate_to = None, user_id = None):
        self.__date_from  = validate_date(date_from)
        self.__date_to = validate_date(date_to)
        self.__salon_id = int(salon_id)
        self.__deleted = [1, 0] if deleted == '-1' else (['1'] if deleted == '1' else [0])
        self.__cdate_from = validate_date(cdate_from) if cdate_from not in '' else None
        self.__cdate_to = validate_date(cdate_to)  if cdate_to not in '' else None
        self.__user_id = user_id if user_id not in '' else None
        self.__tt_record_ids_global = []
        self.__visit_ids_global = []
        self.__master_tips_ids_list = []
        self.__master_tips_ids = None
        self.__tips_invoice_ids_list = []
        self.__tips_invoice_ids = None
        self.__documents_list = []
        self.__documents_ids = None
        self.__gt_cerificates_ids = None
        self.__gt_certificates_list = []
        self.__gt_abonements_ids = None
        self.__gt_abonements_list = []
        self.__goods_transactions_list = []
        self.__goods_transactions_ids = None
        self.__records_list = None
        self.__recordsWithResources = []
        self.__gt_certificates_ids = None

    def delete_standart(self):

        # Создаю папки. Мы же культурные б..ть. А поскольку всегда начинаем с этого метода. Они создаются тут
        deleters_folder_path = 'deleters'
        backups_folder_path = 'backups'
        os.makedirs(deleters_folder_path, exist_ok=True)
        os.makedirs(backups_folder_path, exist_ok=True)

        #Здесь Собираю запрос только по Датам записей. Без условий пользователя и создания записи
        try:
            with connection.cursor() as cursor:

                #Для поиска записей только по дате записи
                sql_simple = f'select id from tt_records where date >= "{self.__date_from} 00:00:00" ' \
                             f'and date <= "{self.__date_to} 23:59:59" ' \
                             f'and salon_id = {self.__salon_id} ' \
                             f'and deleted in ({", ".join(str(n) for n in self.__deleted)}) '

                #Для поиска по дате записи и пользователю
                sql_simple_user_filter = f'select id from tt_records where date >= "{self.__date_from} 00:00:00" ' \
                                         f'and date <= "{self.__date_to} 23:59:59" ' \
                                         f'and salon_id = {self.__salon_id} and user_id = {self.__user_id} ' \
                                         f'and deleted in ({", ".join(str(n) for n in self.__deleted)})'

                #Для поиска по дате записи и дате создания
                sql_with_cdate = f'select id from tt_records where date >= "{self.__date_from} 00:00:00" ' \
                                 f'and date <= "{self.__date_to} 23:59:59" ' \
                                 f'and salon_id = {self.__salon_id} ' \
                                 f'and cdate >= "{self.__cdate_from} 00:00:00" ' \
                                 f'and cdate <= "{self.__cdate_to} 23:59:59" ' \
                                 f'and deleted in ({", ".join(str(n) for n in self.__deleted)});'

                #Дата записи, дата создания и пользователь
                sql_with_cdate_and_user = f'select id from tt_records where date >= "{self.__date_from} 00:00:00" ' \
                                          f'and date <= "{self.__date_to} 23:59:59" ' \
                                          f'and salon_id = {self.__salon_id} ' \
                                          f'and cdate >= "{self.__cdate_from} 00:00:00" ' \
                                          f'and cdate <= "{self.__cdate_to} 23:59:59" ' \
                                          f'and user_id = {self.__user_id} ' \
                                          f'and deleted in ({", ".join(str(n) for n in self.__deleted)});'

                if self.__user_id is None and self.__cdate_from is None and self.__cdate_to is None:
                    cursor.execute(sql_simple)
                    console_text.insert(tk.END, sql_simple, '\n')
                elif self.__user_id is not None and self.__cdate_from is None and self.__cdate_to is None:
                    cursor.execute(sql_simple_user_filter)
                    console_text.insert(tk.END, sql_simple_user_filter, '\n')
                elif self.__user_id is None and self.__cdate_from is not None and self.__cdate_to is not None:
                    cursor.execute(sql_with_cdate)
                    console_text.insert(tk.END, sql_with_cdate, '\n')
                elif self.__user_id is not None and self.__cdate_from is not None and self.__cdate_to is not None:
                    cursor.execute(sql_with_cdate_and_user)
                    console_text.insert(tk.END, sql_with_cdate_and_user, '\n')

                result = cursor.fetchall()
                time.sleep(2)
                if not result:
                    console_text.insert(tk.END,"\nРезультат пустой. Проверь запрос снова\n")

                else:
                    ids = [item[0] for item in result]
                    self.__tt_record_ids_global = copy.deepcopy(ids)
                    self.__records_list = ', '.join([f'"{val}"' for val in ids])
                    with open('deleters/tt_records_delete.sql', 'a') as tr_file:
                        if len(ids) > 5000:
                            for i in range (len(ids)//5000 +1):
                                print('DELETE FROM tt_records WHERE id in ( ', file=tr_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=tr_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=tr_file)
                                        break
                        else:
                            print('DELETE FROM tt_records WHERE id in ( ', file=tr_file)
                            for i in range(len(ids)):
                                if i != len(ids)-1:
                                    print(ids[i], ', ', file=tr_file)
                                else:
                                    print(ids[i], ');', file=tr_file)
                    console_text.insert(tk.END, 'tt_records готов\n')
        finally:
            cursor.close()

    def tt_records_backup(self):
        #Собираю Бэкап по списку ID записей которые собрали для удаления.
        try:
            with connection.cursor() as cursor:
                if len(self.__tt_record_ids_global) >=1:
                    values_str = ', '.join([f'"{val}"' for val in self.__tt_record_ids_global])
                    sql = f'select * from tt_records ' \
                          f'where id IN ({values_str});'
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    time.sleep(2)
                    with open('backups/tt_records_backup.sql', 'a', encoding='utf-8') as tr_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO tt_records (id,created_user_id,first_client_id,salon_id,master_id,service_id,'
                                      'user_id,client_id,comer_id,cdate,date,comment,fictive_client_name,fictive_client_email,'
                                      'fictive_client_phone,length,lastchange,cost,discount,slot_id,deleted,confirmed,sms_before,'
                                      'sms_now,sms_now_text,email_now,notified,uid_deleter,type,partner_id,partner_record_id,bookform_id,'
                                      'autopayment_status,master_request,api_id,ya_type,from_url,review_requested,visit_attendance,'
                                      'GCal_id,master_google_cal,hash,is_mobile,paid_full,custom_color,token,activity_id,prepaid_status,'
                                      'visit_id,clients_count) VALUES', file=tr_backup)
                                print(f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]}, '
                                      f'\'{row[9]}\',\'{row[10]}\',\'{row[11]}\',\'{row[12]}\',\'{row[13]}\', '
                                      f'\'{row[14]}\',{row[15]},\'{row[16]}\',{row[17]}, '
                                      f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},\'{row[24]}\',{row[25]},{row[26]}, '
                                      f'{row[27]},{row[28]},{row[29]},\'{row[30]}\',{row[31]},{row[32]},{row[33]},\'{row[34]}\',\'{row[35]}\', '
                                      f'\'{row[36]}\',{row[37]},{row[38]},\'{row[39]}\',\'{row[40]}\',\'{row[41]}\',{row[42]},{row[43]}, '
                                      f'\'{row[44]}\','
                                      f'\'{row[45]}\',{row[46]},{row[47]},{row[48]},{row[49]}),', file=tr_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result)-1:
                                print(f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]}, '
                                      f'\'{row[9]}\',\'{row[10]}\',\'{row[11]}\',\'{row[12]}\',\'{row[13]}\', '
                                      f'\'{row[14]}\',{row[15]},\'{row[16]}\',{row[17]}, '
                                      f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},\'{row[24]}\',{row[25]},{row[26]}, '
                                      f'{row[27]},{row[28]},{row[29]},\'{row[30]}\',{row[31]},{row[32]},{row[33]},\'{row[34]}\',\'{row[35]}\', '
                                      f'\'{row[36]}\',{row[37]},{row[38]},\'{row[39]}\',\'{row[40]}\',\'{row[41]}\',{row[42]},{row[43]}, '
                                      f'\'{row[44]}\','
                                      f'\'{row[45]}\',{row[46]},{row[47]},{row[48]},{row[49]});', file=tr_backup)
                                counter = 0
                            else:
                                print(f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]}, '
                                      f'\'{row[9]}\',\'{row[10]}\',\'{row[11]}\',\'{row[12]}\',\'{row[13]}\', '
                                      f'\'{row[14]}\',{row[15]},\'{row[16]}\',{row[17]}, '
                                      f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},\'{row[24]}\',{row[25]},{row[26]}, '
                                      f'{row[27]},{row[28]},{row[29]},\'{row[30]}\',{row[31]},{row[32]},{row[33]},\'{row[34]}\',\'{row[35]}\', '
                                      f'\'{row[36]}\',{row[37]},{row[38]},\'{row[39]}\',\'{row[40]}\',\'{row[41]}\',{row[42]},{row[43]}, '
                                      f'\'{row[44]}\','
                                      f'\'{row[45]}\',{row[46]},{row[47]},{row[48]},{row[49]}),', file=tr_backup)
                                counter += 1
                        console_text.insert(tk.END, 'tt_records_bakcup готов \n')
                else:
                    console_text.insert(tk.END, "Нет записей\n")
        finally:
            cursor.close()

#Собираю файл client_visits
    def client_visits_delete(self):
        global visit_ids_str
        try:
            with connection.cursor() as cursor:
                if len(self.__tt_record_ids_global) >=1:
                    values_str = ', '.join([f'"{val}"' for val in self.__tt_record_ids_global])
                query_visit = f'SELECT visit_id from tt_records where id in ({values_str}) and visit_id != 0 and ' \
                              f'deleted = 0 and salon_id = {self.__salon_id};'
                cursor.execute(query_visit)
                visit_ids_tuple = cursor.fetchall()

                if not visit_ids_tuple:
                    console_text.insert(tk.END,'Результат пустой\n')
                else:
                    visit_ids_list = [i[0] for i in visit_ids_tuple]
                    visit_ids_str = ', '.join([f'"{val}"' for val in visit_ids_list])
                    query_visit_check = f'SELECT id FROM client_visits WHERE id IN ({visit_ids_str})'
                    cursor.execute(query_visit_check)
                    visit_ids_tuple = cursor.fetchall()
                    visit_ids_list = [i[0] for i in visit_ids_tuple]
                    self.__visit_ids_global = copy.deepcopy(visit_ids_list)
                    with open('deleters/clients_visits_delete.sql', 'a') as cv_file:
                        if len(visit_ids_list) > 5000:
                            for i in range (len(visit_ids_list)//5000 +1):
                                print('DELETE FROM client_visits WHERE id in ( ', file=cv_file)
                                for j in range(5000):
                                    id = visit_ids_list.pop(0)
                                    print(id, ', ', file=cv_file)
                                    if len(visit_ids_list) == 1 or j == 4999:
                                        id = visit_ids_list.pop(0)
                                        print(id, ');', file=cv_file)
                                        break
                        else:
                            print('DELETE FROM client_visits WHERE id in ( ', file=cv_file)
                            for i in range(len(visit_ids_list)):
                                if i != len(visit_ids_list)-1:
                                    print(visit_ids_list[i], ', ', file=cv_file)
                                else:
                                    print(visit_ids_list[i], ');', file=cv_file)
        finally:
            console_text.insert(tk.END,'client_visits готов \n')
            cursor.close()

    def client_visits_backup(self):
        if len(self.__visit_ids_global) >= 1:
            with connection.cursor() as cursor:
                values_str = ', '.join([f'"{val}"' for val in self.__visit_ids_global])
                sql = f'select * from client_visits ' \
                      f'where id IN ({values_str});'
                cursor.execute(sql)
                result = cursor.fetchall()
                time.sleep(2)
                cursor.close()
                with open('backups/client_visits_backup.sql', 'a', encoding='utf-8') as cv_backup:
                    counter = 0
                    for row in result:
                        row = tuple('null' if x is None else x for x in row)
                        if counter == 0:
                            print('insert into client_visits (id, client_id, date, spent_money, attendance, '
                                  'discount, comment, moderation, sms_hours_accept, sms_sended, sms_text, email_hours_accept, '
                                  'email_sended) VALUES', file=cv_backup)
                            print(f'({row[0]},{row[1]},\'{row[2]}\',{row[3]},{row[4]},{row[5]},\'{row[6]}\',{row[7]},{row[8]}, '
                                  f'{row[9]},\'{row[10]}\',{row[11]},{row[12]}),', file=cv_backup)
                            counter += 1
                        elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                            print(f'({row[0]},{row[1]},\'{row[2]}\',{row[3]},{row[4]},{row[5]},\'{row[6]}\',{row[7]},{row[8]}, '
                                  f'{row[9]},\'{row[10]}\',{row[11]},{row[12]});', file=cv_backup)
                            counter = 0
                        else:
                            print(f'({row[0]},{row[1]},\'{row[2]}\',{row[3]},{row[4]},{row[5]},\'{row[6]}\',{row[7]},{row[8]}, '
                                  f'{row[9]},\'{row[10]}\',{row[11]},{row[12]}),', file=cv_backup)
                            counter += 1
                    console_text.insert(tk.END,'clievnts_visit_backup готов \n')


    def tt_services_delete(self):
        if len(self.__tt_record_ids_global) >= 1:
            with connection.cursor() as cursor:
                records_list = copy.deepcopy(self.__tt_record_ids_global)
                record_ids = ', '.join([f'{val}' for val in records_list])
                query = f'SELECT * FROM tt_services WHERE record_id IN ({record_ids});'
                cursor.execute(query)
                result_ts = cursor.fetchall()
                cursor.close()
                if not result_ts:
                    console_text.insert(tk.END, "Нет услуг в записях\n")
                else:
                    ids = [item[0] for item in result_ts]
                    with open('deleters/tt_services_delete.sql', 'a') as ts_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM tt_services WHERE id in ( ', file=ts_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=ts_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=ts_file)
                                        break
                        else:
                            print('DELETE FROM tt_services WHERE id in ( ', file=ts_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=ts_file)
                                else:
                                    print(ids[i], ');', file=ts_file)
        else:
            console_text.insert(tk.END, 'Нет строк в tt_services\n')

    def tt_services_backup(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, "Нет строк в tt_services\n")
        else:
            with connection.cursor() as cursor:
                records_list = copy.deepcopy(self.__tt_record_ids_global)
                record_ids = ', '.join([f'{val}' for val in records_list])
                query = f'SELECT * FROM tt_services WHERE record_id IN ({record_ids});'
                cursor.execute(query)
                result_ts = cursor.fetchall()
                cursor.close()
                if not result_ts:
                    console_text.insert(tk.END, "Нет услуг в записях\n")
                else:
                    with open('backups/tt_services_backup.sql', 'a', encoding='utf-8') as ts_backup:
                        counter = 0
                        for row in result_ts:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('insert into tt_services (id, record_id, service_id, salon_service_id, '
                                      'technological_card_id, amount, first_cost, cost, discount, master_salary, '
                                      'manual_cost, amount_cut_cost_loyalty_discount, amount_cut_cost_loyalty_bonus, '
                                      'amount_cut_cost_loyalty_certificat, amount_cut_cost_loyalty_abonement, '
                                      'amount_cut_cost_deposits)'
                                      ' VALUES', file=ts_backup)
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]}, '
                                    f'{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}),', file=ts_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result_ts) - 1:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]}, '
                                    f'{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]});', file=ts_backup)
                                counter = 0
                            else:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]}, '
                                    f'{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}),', file=ts_backup)
                                counter += 1
                        console_text.insert(tk.END, 'tt_services_backup готов \n')

    def master_tips(self):
        if len(self.__tt_record_ids_global) >= 1:
            with connection.cursor() as cursor:
                records_list = copy.deepcopy(self.__tt_record_ids_global)
                record_ids = ', '.join([f'{val}' for val in records_list])
                query = f'SELECT * FROM master_tips WHERE record_id IN ({record_ids});'
                cursor.execute(query)
                result_mt = cursor.fetchall()
                self.__master_tips_ids_list = [item[0] for item in result_mt]
                self.__master_tips_ids = ', '.join([f'{val}' for val in self.__master_tips_ids_list])
                cursor.close()
                if not result_mt:
                    console_text.insert(tk.END, "Нет чаевых в записях\n")
                else:
                    ids = [item[0] for item in result_mt]
                    with open('deleters/master_tips_delete.sql', 'a') as mt_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM master_tips WHERE id in ( ', file=mt_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=mt_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=mt_file)
                                        break
                        else:
                            print('DELETE FROM master_tips WHERE id in ( ', file=mt_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=mt_file)
                                else:
                                    print(ids[i], ');', file=mt_file)
        else:
            console_text.insert(tk.END, 'Нет строк в master_tips\n')
    def master_tips_backup(self):
        if len(self.__master_tips_ids_list) == 0:
            console_text.insert(tk.END, "Нет Записей для удаления\n")
        else:
            with connection.cursor() as cursor:
                records_list = copy.deepcopy(self.__tt_record_ids_global)
                record_ids = ', '.join([f'{val}' for val in records_list])
                query = f'SELECT * FROM master_tips WHERE record_id IN ({record_ids});'
                cursor.execute(query)
                result_mt = cursor.fetchall()
                cursor.close()

                if not result_mt:
                    console_text.insert(tk.END, "Нет чаевых в записях\n")
                else:
                    with open('backups/master_tips_backup.sql', 'a', encoding='utf-8') as mt_backup:
                        counter = 0
                        for row in result_mt:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO '
                                      'master_tips (id, record_id, master_id, tips_amount, tips_currency_id, '
                                      'commission_percent, is_client_paying_commission, sender_name) '
                                      'VALUES', file=mt_backup)
                                if row[7] == 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},'
                                        f'{row[7]}),', file=mt_backup)
                                    counter += 1
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},'
                                        f'\'{row[7]}\'),', file=mt_backup)
                                    counter += 1
                            elif counter == 5000 or counter == len(result_mt) - 1:
                                if row[7] == 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},'
                                        f'{row[7]});', file=mt_backup)
                                    counter = 0
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},'
                                        f'\'{row[7]}\');', file=mt_backup)
                                    counter = 0
                            else:
                                if row[7] == 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},'
                                        f'{row[6]},{row[7]}),', file=mt_backup)
                                    counter += 1
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},'
                                        f'{row[6]},\'{row[7]}\'),', file=mt_backup)
                                    counter += 1
                        console_text.insert(tk.END, 'master_tips_backup готов \n')


    def master_tips_invoices(self):
        if len(self.__master_tips_ids_list) >= 1:
            with connection.cursor() as cursor:
                #Собираю инвойсы для дальнейшего шага
                query = f'SELECT invoice_id FROM master_tips_invoices_links WHERE master_tips_id ' \
                        f'IN ({self.__master_tips_ids});'
                cursor.execute(query)
                invoices = cursor.fetchall()
                self.__tips_invoice_ids_list = [item[0] for item in invoices]
                self.__tips_invoice_ids = ', '.join([f'{val}' for val in self.__tips_invoice_ids_list])

                #Собираю целевые ID
                query2 = f'SELECT id FROM master_tips_invoices_links WHERE master_tips_id ' \
                        f'IN ({self.__master_tips_ids});'
                cursor.execute(query2)
                invoices_mt = cursor.fetchall()
                cursor.close()
                if not invoices_mt:
                    console_text.insert(tk.END, "Нет чаевых в записях\n")
                else:
                    ids = [item[0] for item in invoices_mt]
                    with open('deleters/master_tips_invoices_links.sql', 'a') as mtil_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM master_tips_invoices_links WHERE id in ( ', file=mtil_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=mtil_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=mtil_file)
                                        break
                        else:
                            print('DELETE FROM master_tips_invoices_links WHERE id in ( ', file=mtil_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=mtil_file)
                                else:
                                    print(ids[i], ');', file=mtil_file)
        else:
            console_text.insert(tk.END, 'Нет строк в master_tips_invoices_links\n')


    def master_tips_invoices_backup(self):
        if len(self.__master_tips_ids_list) == 0:
            console_text.insert(tk.END, "Нет строк в aster_tips_invoices_links\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM master_tips_invoices_links WHERE master_tips_id ' \
                        f'IN ({self.__master_tips_ids});'
                cursor.execute(query)
                result_mt = cursor.fetchall()
                cursor.close()

                if not result_mt:
                    console_text.insert(tk.END, "Нет услуг в записях\n")
                else:
                    with open('backups/master_tips_invoices_backup.sql', 'a', encoding='utf-8') as mtb_backup:
                        counter = 0
                        for row in result_mt:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO master_tips_invoices_links '
                                      '(id, master_tips_id, invoice_id, redirect_prefix) '
                                      'VALUES', file=mtb_backup)
                                print(
                                    f'({row[0]},{row[1]},{row[2]},\'{row[3]}\'),', file=mtb_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result_mt) - 1:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},\'{row[3]}\');', file=mtb_backup)
                                counter = 0
                            else:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},\'{row[3]}\'),', file=mtb_backup)
                                counter += 1
                        console_text.insert(tk.END, 'master_tips_invoices_backup готов \n')


    def tips_invoces(self):
        if len(self.__tips_invoice_ids_list) >= 1:
            with connection.cursor() as cursor:
                query = f'SELECT id FROM invoice WHERE id IN ({self.__tips_invoice_ids});'
                cursor.execute(query)
                invoices_mt = cursor.fetchall()
                cursor.close()
                if not invoices_mt:
                    console_text.insert(tk.END, "Нет чаевых в записях\n")
                else:
                    ids = [item[0] for item in invoices_mt]
                    with open('deleters/invoices(tips).sql', 'a') as mti_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM invoice WHERE id in ( ', file=mti_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=mti_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=mti_file)
                                        break
                        else:
                            print('DELETE FROM invoice WHERE id in ( ', file=mti_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=mti_file)
                                else:
                                    print(ids[i], ');', file=mti_file)
        else:
            console_text.insert(tk.END, 'Нет строк в master_tips_invoices_links\n')

    def invoices_tips_backup(self):
        if len(self.__tips_invoice_ids_list) == 0:
            console_text.insert(tk.END, "Нет Записей для удаления\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM invoice WHERE id IN ({self.__tips_invoice_ids});'
                cursor.execute(query)
                result_mt = cursor.fetchall()
                cursor.close()
                if not result_mt:
                    console_text.insert(tk.END, "Нет строк для бэкапа\n")
                else:
                    with open('backups/invoices(tips)_backup.sql', 'a', encoding='utf-8') as mti_backup:
                        counter = 0
                        for row in result_mt:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO invoice '
                                      '(id, salon_id, status, payment_system_id, payment_type_id, order_id, ps_transaction_id, '
                                      'sum, ps_sum, payout_sum, currency_id, currency_rate, client_id, ps_account_id, is_test, '
                                      'date_create, date_ps_payment, date_payout, title, comment) '
                                      'VALUES', file=mti_backup)
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},\'{row[15]}\', '
                                    f'\'{row[16]}\',\'{row[17]}\',\'{row[18]}\', \'{row[19]}\'),', file=mti_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result_mt) - 1:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},\'{row[15]}\', '
                                    f'\'{row[16]}\',\'{row[17]}\',\'{row[18]}\', \'{row[19]}\');', file=mti_backup)
                                counter = 0
                            else:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},\'{row[15]}\', '
                                    f'\'{row[16]}\',\'{row[17]}\',\'{row[18]}\', \'{row[19]}\'),', file=mti_backup)
                                counter += 1
                        console_text.insert(tk.END, 'invoces(tips) backup готов \n')

    def documents_delete(self):
        try:
            with connection.cursor() as cursor:
                if len(self.__tt_record_ids_global) >=1 and len(self.__visit_ids_global) >=1:
                    records = ', '.join([f'"{val}"' for val in self.__tt_record_ids_global])
                    visits = ', '.join([f'"{val}"' for val in self.__visit_ids_global])
                    sql = f'select * from documents ' \
                          f'where record_id IN ({records}) OR visit_id IN ({visits});'
                    cursor.execute(sql)
                    result = cursor.fetchall()
                elif len(self.__tt_record_ids_global) >=1 and len(self.__visit_ids_global) ==0:
                    records = ', '.join([f'"{val}"' for val in self.__tt_record_ids_global])
                    sql = f'select * from documents ' \
                          f'where record_id IN ({records});'
                    cursor.execute(sql)
                    result = cursor.fetchall()
                else:
                    console_text.insert(tk.END, 'Нет документов для удаления\n')

                if len(self.__tt_record_ids_global) ==0 and len(self.__visit_ids_global) ==0:
                    console_text.insert(tk.END, 'Завершение команды\n')
                else:
                    self.__documents_list = [item[0] for item in result]
                    self.__documents_ids = ', '.join([f'"{val}"' for val in self.__documents_list])
                    ids = copy.deepcopy(self.__documents_list)
                    with open('deleters/documents_delete.sql', 'a') as documents_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM documents WHERE id in ( ', file=documents_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=documents_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=documents_file)
                                        break
                        else:
                            print('DELETE FROM documents WHERE id in ( ', file=documents_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=documents_file)
                                else:
                                    print(ids[i], ');', file=documents_file)
        finally:
            cursor.close()
            console_text.insert(tk.END, 'Documents_delete.sql собран\n')

    def documents_backup(self):
        if len(self.__documents_list) == 0:
            console_text.insert(tk.END, "Нет документов для удаления\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM documents WHERE id IN ({self.__documents_ids});'
                cursor.execute(query)
                result_mt = cursor.fetchall()
                cursor.close()
                if not result_mt:
                    console_text.insert(tk.END, "Нет строк для бэкапа\n")
                else:
                    with open('backups/documents_backup.sql', 'a', encoding='utf-8') as documents_backup:
                        counter = 0
                        for row in result_mt:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO documents (id, user_id, salon_id, type, comment, date_create, '
                                      'date, storage_id, category_id, visit_id, record_id, deleted, number, '
                                      'services_count, goods_count, consumables_count, bill_print_status) '
                                      'VALUES', file=documents_backup)

                                if str(row[4]) != 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]}),', file=documents_backup)
                                    counter += 1
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]}),', file=documents_backup)
                                    counter += 1
                            elif counter == 5000 or counter == len(result_mt) - 1:
                                if str(row[4]) != 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]});', file=documents_backup)
                                    counter = 0
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]});', file=documents_backup)
                                    counter = 0
                            else:
                                if str(row[4]) != 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]}),', file=documents_backup)
                                    counter += 1
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]}),', file=documents_backup)
                                    counter += 1
                        console_text.insert(tk.END, 'documents_backup готов \n')

    def transactions_delete(self):
        if len(self.__documents_list) >= 1:
            global transactions, transactions_amount_tup
            with connection.cursor() as cursor:
                query = f'SELECT id FROM transactions WHERE document_id IN ({self.__documents_ids});'
                cursor.execute(query)
                transactions = cursor.fetchall()
                query2 = f'SELECT SUM(amount), account_id FROM transactions ' \
                         f'where document_id IN ({self.__documents_ids}) ' \
                         f'AND cancel = 0 ' \
                         f'GROUP BY account_id'
                cursor.execute(query2)
                transactions_amount_tup = cursor.fetchall()
                cursor.close()
                if not transactions:
                    console_text.insert(tk.END, "Нет транзакций в записях\n")
                else:
                    ids = [item[0] for item in transactions]
                    with open('deleters/transactions.sql', 'a') as transactions_file:

                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM transactions WHERE id in ( ', file=transactions_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=transactions_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=transactions_file)
                                        break
                        else:
                            print('DELETE FROM transactions WHERE id in ( ', file=transactions_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=transactions_file)
                                else:
                                    print(ids[i], ');', file=transactions_file)

                        if not transactions_amount_tup:
                            console_text.insert(tk.END, 'Что то пошло не так. \nНет суммы транзакций\n')
                        else:
                            for row in transactions_amount_tup:
                                amount = float(row[0])
                                account_id = int(row[1])
                                if float(amount) > 0:
                                    print(f'UPDATE accounts '
                                          f'SET balance = balance - ({abs(amount)}) '
                                          f'WHERE id = {account_id};', file=transactions_file)
                                elif float(amount) < 0:
                                    print(f'UPDATE accounts '
                                          f'SET balance = balance + ({abs(amount)}) '
                                          f'WHERE id = {account_id};', file=transactions_file)
                                else:
                                    continue

                        console_text.insert(tk.END, 'Транзакции собраны\n')
        else:
            console_text.insert(tk.END, 'Нет строк в transactions\n')

    def transactions_backup(self):
        if len(self.__documents_list) == 0:
            console_text.insert(tk.END, "Нет транзакций для удаления\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM transactions WHERE document_id IN ({self.__documents_ids});'
                cursor.execute(query)
                result_mt = cursor.fetchall()
                cursor.close()
                if not result_mt:
                    console_text.insert(tk.END, "Нет строк для бэкапа\n")
                else:
                    with open('backups/transactions_backup.sql', 'a', encoding='utf-8') as transactions_backup:
                        counter = 0
                        for row in result_mt:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO transactions (id, account_id, user_id, amount, date, '
                                      'date_create, supplier_id, client_id, master_id, visit_id, record_id, type, '
                                      'document_id, cancel, cancel_user_id, real_money, comment, account_balance, move, '
                                      'sold_item_id, sold_item_service_type, real_record_id, is_prepaid, '
                                      'item_salon_service_id, commission_transaction_id, commission_percent, '
                                      'date_last_change) VALUES ', file=transactions_backup)

                                if str(row[16]) != 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',{row[6]},{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'\'{row[16]}\',{row[17]}, '
                                        f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},{row[24]},{row[25]}, '
                                        f'\'{row[26]}\'),', file=transactions_backup)
                                    counter += 1
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',{row[6]},{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]},{row[17]}, '
                                        f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},{row[24]},{row[25]}, '
                                        f'\'{row[26]}\'),', file=transactions_backup)
                                    counter += 1
                            elif counter == 5000 or counter == len(result_mt) - 1:
                                if str(row[16]) != 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',{row[6]},{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'\'{row[16]}\',{row[17]}, '
                                        f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},{row[24]},{row[25]}, '
                                        f'\'{row[26]}\');', file=transactions_backup)
                                    counter = 0
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',{row[6]},{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]},{row[17]}, '
                                        f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},{row[24]},{row[25]}, '
                                        f'\'{row[26]}\');', file=transactions_backup)
                                    counter = 0
                            else:
                                if str(row[16]) != 'null':
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',{row[6]},{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'\'{row[16]}\',{row[17]}, '
                                        f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},{row[24]},{row[25]}, '
                                        f'\'{row[26]}\'),', file=transactions_backup)
                                    counter += 1
                                else:
                                    print(
                                        f'({row[0]},{row[1]},{row[2]},{row[3]},\'{row[4]}\',\'{row[5]}\',{row[6]},{row[7]}, '
                                        f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]}, '
                                        f'{row[16]},{row[17]}, '
                                        f'{row[18]},{row[19]},{row[20]},{row[21]},{row[22]},{row[23]},{row[24]},{row[25]}, '
                                        f'\'{row[26]}\'),', file=transactions_backup)
                                    counter += 1

                        if not transactions_amount_tup:
                            console_text.insert(tk.END, 'Что то пошло не так. \nНет суммы транзакций\n')
                        else:
                            for row in transactions_amount_tup:
                                amount = float(row[0])
                                account_id = int(row[1])
                                if float(amount) > 0:
                                    print(f'UPDATE accounts '
                                          f'SET balance = balance + ({abs(amount)}) '
                                          f'WHERE id = {account_id};', file=transactions_backup)
                                elif float(amount) < 0:
                                    print(f'UPDATE accounts '
                                          f'SET balance = balance - ({abs(amount)}) '
                                          f'WHERE id = {account_id};', file=transactions_backup)
                                else:
                                    continue
                        console_text.insert(tk.END, 'transactions_backup готов \n')

    def goods_transactions_delete(self):
        if len(self.__documents_list) >= 1:
            with connection.cursor() as cursor:
                query = f'SELECT id, loyalty_certificate_id, loyalty_abonement_id ' \
                        f'FROM goods_transactions ' \
                        f'WHERE document_id ' \
                        f'IN ({self.__documents_ids});'
                cursor.execute(query)
                goods_transactions_table = cursor.fetchall()
                cursor.close()
                if not goods_transactions_table:
                    console_text.insert(tk.END, "Нет складских операций в записях\n")
                else:
                    self.__goods_transactions_list = [item[0] for item in goods_transactions_table]
                    ids = copy.deepcopy(self.__goods_transactions_list)
                    self.__goods_transactions_ids = ', '.join([f'{val}' for val in self.__goods_transactions_list])

                    #Здесь же собрал продажи лояльности в визите
                    self.__gt_certificates_list = [item[1] for item in goods_transactions_table if item[1] != 0]
                    if len(self.__gt_certificates_list) >= 1:
                        self.__gt_certificates_ids = ', '.join(f'{val}' for val in self.__gt_certificates_list)
                    else:
                        console_text.insert(tk.END, 'В записях нет продаж сертификатов\n')
                    self.__gt_abonements_list = [item[2] for item in goods_transactions_table if item[2] != 0]
                    if len(self.__gt_abonements_list) >= 1:
                        self.__gt_abonements_ids = ', '.join(f'{val}' for val in self.__gt_abonements_list)
                    else:
                        console_text.insert(tk.END, 'В записях нет продаж абонементов\n')

                    with open('deleters/goods_transactions.sql', 'a') as goods_transactions_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM goods_transactions WHERE id in ( ', file=goods_transactions_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=goods_transactions_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=goods_transactions_file)
                                        break
                        else:
                            print('DELETE FROM goods_transactions WHERE id in ( ', file=goods_transactions_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=goods_transactions_file)
                                else:
                                    print(ids[i], ');', file=goods_transactions_file)
        else:
            console_text.insert(tk.END, 'Нет строк в goods_transactions\n')

    def goods_transactions_backup(self):
        if len(self.__goods_transactions_list) == 0:
            console_text.insert(tk.END, "Нет товарных транзакций для удаления\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM goods_transactions WHERE id IN ({self.__goods_transactions_ids});'
                cursor.execute(query)
                result_gt = cursor.fetchall()
                cursor.close()
                if not result_gt:
                    console_text.insert(tk.END, "Нет строк для бэкапа\n")
                else:
                    with open('backups/goods_transactions_backup.sql', 'a', encoding='utf-8') as goods_transactions_backup_file:
                        counter = 0
                        for row in result_gt:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO goods_transactions '
                                      '(id, salon_id, good_id, amount, sale_amount, service_amount, unit_id, '
                                      'sale_unit_id, service_unit_id, operation_unit_type, cost_per_unit, storage_id, '
                                      'supplier_id, create_date, date_in_salon_local_timezone, timezone, '
                                      'create_date_original, type, document_id, goods_receipt_id, visit_id, record_id, '
                                      'client_id, service_id, comment, deleted, move, user_id, master_id, price, '
                                      'discount, cost, manual_cost, pkg_amount, cancel_user_id, cancel_date, '
                                      'not_real_deleted, loyalty_certificate_id, loyalty_abonement_id, '
                                      'amount_cut_cost_loyalty_discount, amount_cut_cost_loyalty_bonus, '
                                      'amount_cut_cost_loyalty_certificat, amount_cut_cost_loyalty_abonement, '
                                      'amount_cut_cost_deposits, date_last_change) '
                                      'VALUES ', file=goods_transactions_backup_file)
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},\'{row[13]}\',\'{row[14]}\',{row[15]}, '
                                    f'\'{row[16]}\',{row[17]}, {row[18]},{row[19]},{row[20]},{row[21]},{row[22]},'
                                    f'{row[23]},\'{row[24]}\',{row[25]}, {row[26]}, {row[27]},{row[28]},{row[29]},'
                                    f'{row[30]}, {row[31]},{row[32]}, {row[33]},{row[34]},\'{row[35]}\',{row[36]},'
                                    f'{row[37]},{row[38]},{row[39]},{row[40]}, {row[41]},{row[42]},'
                                    f'{row[43]}, \'{row[44]}\' ),', file=goods_transactions_backup_file)
                                counter += 1
                            elif counter == 5000 or counter == len(result_gt) - 1:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},\'{row[13]}\',\'{row[14]}\',{row[15]}, '
                                    f'\'{row[16]}\',{row[17]}, {row[18]},{row[19]},{row[20]},{row[21]},{row[22]},'
                                    f'{row[23]},\'{row[24]}\',{row[25]}, {row[26]}, {row[27]},{row[28]},{row[29]},'
                                    f'{row[30]}, {row[31]},{row[32]}, {row[33]},{row[34]},\'{row[35]}\',{row[36]},'
                                    f'{row[37]},{row[38]},{row[39]},{row[40]}, {row[41]},{row[42]},'
                                    f'{row[43]}, \'{row[44]}\');', file=goods_transactions_backup_file)
                                counter = 0
                            else:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},\'{row[13]}\',\'{row[14]}\',{row[15]}, '
                                    f'\'{row[16]}\',{row[17]}, {row[18]},{row[19]},{row[20]},{row[21]},{row[22]},'
                                    f'{row[23]},\'{row[24]}\',{row[25]}, {row[26]}, {row[27]},{row[28]},{row[29]},'
                                    f'{row[30]}, {row[31]},{row[32]}, {row[33]},{row[34]},\'{row[35]}\',{row[36]},'
                                    f'{row[37]},{row[38]},{row[39]},{row[40]}, {row[41]},{row[42]},'
                                    f'{row[43]}, \'{row[44]}\'),', file=goods_transactions_backup_file)
                                counter += 1

                        console_text.insert(tk.END, 'goods_transactions_backup готов \n')

    def record_resourse_link(self):
        if len(self.__tt_record_ids_global) <= 0:
            console_text.insert(tk.END, 'Выборка не содержит записей c ресурсами\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT DISTINCT(record_id) ' \
                        f'FROM record_resource_instances_link ' \
                        f'WHERE record_id ' \
                        f'IN ({self.__records_list});'
                cursor.execute(query)
                records_with_resources = cursor.fetchall()
                cursor.close()
                if not records_with_resources:
                    console_text.insert(tk.END, "Нет ресурсов в записях\n")
                else:
                    self.__recordsWithResources = [item[0] for item in records_with_resources]
                    ids = [item[0] for item in records_with_resources]
                    with open('deleters/record_resource_instances_link.sql', 'a') as record_resource_instances_link_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM record_resource_instances_link WHERE record_id in ( ', file=record_resource_instances_link_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=record_resource_instances_link_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=record_resource_instances_link_file)
                                        break
                        else:
                            print('DELETE FROM record_resource_instances_link WHERE record_id in ( ', file=record_resource_instances_link_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=record_resource_instances_link_file)
                                else:
                                    print(ids[i], ');', file=record_resource_instances_link_file)

                        console_text.insert(tk.END, 'Удаление ресурсов в записях собраны\n')

    def record_resource_instances_link_backup(self):
        if len(self.__recordsWithResources) == 0:
            console_text.insert(tk.END, "Нет записей с ресурсами для удаления\n")
        else:
            with connection.cursor() as cursor:
                if len(self.__recordsWithResources) >=1:
                    values_str = ', '.join([f'"{val}"' for val in self.__recordsWithResources])
                else:
                    console_text.insert(tk.END, 'Говорил же, что нет записей с ресурсами')
                query = f'SELECT * FROM record_resource_instances_link WHERE ' \
                        f'record_id IN ({values_str});'
                cursor.execute(query)
                result_record_resource_instances_link = cursor.fetchall()
                cursor.close()
                if not result_record_resource_instances_link:
                    console_text.insert(tk.END, "Нет строк для бэкапа\n")
                else:
                    with open('backups/result_record_resource_instances_link_backup.sql', 'a', encoding='utf-8') as result_record_resource_instances_link_backup:
                        counter = 0
                        for row in result_record_resource_instances_link:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO record_resource_instances_link '
                                      '(record_id, resource_instance_id, service_id, salon_service_id) '
                                      'VALUES', file=result_record_resource_instances_link_backup)
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]} ),', file=result_record_resource_instances_link_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result_record_resource_instances_link) - 1:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]});', file=result_record_resource_instances_link_backup)
                                counter = 0
                            elif counter == 0 and len(result_record_resource_instances_link) == 1:
                                print('INSERT INTO record_resource_instances_link '
                                      '(record_id, resource_instance_id, service_id, salon_service_id) '
                                      'VALUES', file=result_record_resource_instances_link_backup)
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]});',
                                    file=result_record_resource_instances_link_backup)
                            else:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]}),', file=result_record_resource_instances_link_backup)
                                counter += 1
                        console_text.insert(tk.END, 'result_record_resource_instances_link_backup готов \n')


    def tt_resources_occupation(self):
        global records_with_resources_str
        if len(self.__recordsWithResources) <= 0:
            console_text.insert(tk.END, 'Выборка не содержит записей c ресурсами\n')
        else:
            records_with_resources_str = ', '.join([f'"{val}"' for val in self.__recordsWithResources])
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM tt_resources_occupation ' \
                        f'WHERE source_id ' \
                        f'IN ({records_with_resources_str}) ' \
                        f'AND source_type = \'record\';'
                cursor.execute(query)
                records_with_resources = cursor.fetchall()
                cursor.close()
                if not records_with_resources:
                    console_text.insert(tk.END, "Нет ресурсов в записях\n")
                else:
                    self.__recordsWithResources = [item[0] for item in records_with_resources]
                    ids = [item[0] for item in records_with_resources]
                    with open('deleters/tt_resources_occupation.sql', 'a') as tt_resources_occupation_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM tt_resources_occupation WHERE id in ( ', file=tt_resources_occupation_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=tt_resources_occupation_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=tt_resources_occupation_file)
                                        break
                        else:
                            print('DELETE FROM tt_resources_occupation WHERE id in ( ', file=tt_resources_occupation_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=tt_resources_occupation_file)
                                else:
                                    print(ids[i], ');', file=tt_resources_occupation_file)

                        console_text.insert(tk.END, 'Удаление ресурсов в записях собраны\n')

    def tt_resources_occupation_backup(self):
        if len(self.__recordsWithResources) <= 0:
            console_text.insert(tk.END, "Нет записей с ресурсами для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM tt_resources_occupation WHERE ' \
                        f'source_id IN ({records_with_resources_str}) ' \
                        f'AND source_type = \'record\';'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет строк для бэкапа\n")
                else:
                    with open('backups/tt_resources_occupation_backup.sql', 'a', encoding='utf-8') as tt_resources_occupation_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO tt_resources_occupation '
                                      '(id, source_type, source_id, resource_instance_id, resource_id, dt_from, dt_to) '
                                      'VALUES', file=tt_resources_occupation_backup)
                                print(
                                    f'({row[0]},\'{row[1]}\',{row[2]},{row[3]},{row[4]}, \'{row[5]}\', \'{row[6]}\' ),', file=tt_resources_occupation_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]},\'{row[1]}\',{row[2]},{row[3]},{row[4]}, \'{row[5]}\', \'{row[6]}\');', file=tt_resources_occupation_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO tt_resources_occupation '
                                      '(id, source_type, source_id, resource_instance_id, resource_id, dt_from, dt_to) '
                                      'VALUES', file=tt_resources_occupation_backup)
                                print(
                                    f'({row[0]},\'{row[1]}\',{row[2]},{row[3]},{row[4]}, \'{row[5]}\', \'{row[6]}\' );',
                                    file=tt_resources_occupation_backup)
                            else:
                                print(
                                    f'({row[0]},\'{row[1]}\',{row[2]},{row[3]},{row[4]}, \'{row[5]}\', \'{row[6]}\'),', file=tt_resources_occupation_backup)
                                counter += 1
                        console_text.insert(tk.END, 'tt_resources_occupation_backup готов \n')

    def google_booking_records(self):
        global records_from_google_list
        global records_from_google_list_str
        if len(self.__tt_record_ids_global) <= 0:
            console_text.insert(tk.END, 'Выборка не содержит записей через google\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM google_booking_records ' \
                        f'WHERE record_id_as_booking_id ' \
                        f'IN ({self.__records_list});'
                cursor.execute(query)
                records_from_google = cursor.fetchall()
                cursor.close()
                if not records_from_google:
                    console_text.insert(tk.END, "Нет записей из google\n")
                else:
                    records_from_google_list = [item[0] for item in records_from_google]
                    records_from_google_list_str = ', '.join([f'"{val}"' for val in records_from_google_list])
                    ids = [item[0] for item in records_from_google]
                    with open('deleters/google_booking_records.sql', 'a') as records_from_google_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM google_booking_records WHERE id in ( ', file=records_from_google_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=records_from_google_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=records_from_google_file)
                                        break
                        else:
                            print('DELETE FROM google_booking_records WHERE id in ( ', file=records_from_google_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=records_from_google_file)
                                else:
                                    print(ids[i], ');', file=records_from_google_file)

                        console_text.insert(tk.END, 'Удаление записей из google собраны\n')

    def google_booking_records_backup(self):
        if len(records_from_google_list) == 0:
            console_text.insert(tk.END, "Нет записей google для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM google_booking_records WHERE ' \
                        f'id IN ({records_from_google_list_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей google для бэкапа\n")
                else:
                    with open('backups/google_booking_records_backup.sql', 'a', encoding='utf-8') as records_from_google_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO google_booking_records '
                                      '(id, partner_id, google_user_id, idempotency_token, record_id_as_booking_id, '
                                      'client_id, user_id, date_create, is_sandbox) '
                                      'VALUES ', file=records_from_google_backup)
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\', \'{row[3]}\', '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,{row[8]}'
                                    f' ),', file=records_from_google_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\', \'{row[3]}\', '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,{row[8]} '
                                    f');', file=records_from_google_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO google_booking_records '
                                      '(id, partner_id, google_user_id, idempotency_token, record_id_as_booking_id, '
                                      'client_id, user_id, date_create, is_sandbox) '
                                      'VALUES ', file=records_from_google_backup)
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\', \'{row[3]}\', '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,{row[8]} '
                                    f');',
                                    file=records_from_google_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\', \'{row[3]}\', '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,{row[8]} '
                                    f'),', file=records_from_google_backup)
                                counter += 1
                        console_text.insert(tk.END, 'records_from_google_backup готов \n')

    def invoice_record_links(self):
        global invoice_records_list
        global invoice_records_list_str
        global order_id_record_invoices_str
        global order_id_record_invoices_list
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит записей\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id, order_id ' \
                        f'FROM invoice_record_links ' \
                        f'WHERE record_id ' \
                        f'IN ({self.__records_list});'
                cursor.execute(query)
                invoice_records = cursor.fetchall()
                cursor.close()
                if not invoice_records:
                    console_text.insert(tk.END, "Нет инвойсов по записям\n")
                else:
                    invoice_records_list = [item[0] for item in invoice_records]
                    invoice_records_list_str = ', '.join([f'"{val}"' for val in invoice_records_list])
                    order_id_record_invoices_list = [f"'{item[1]}'" for item in invoice_records]
                    order_id_record_invoices_str = ', '.join([val for val in order_id_record_invoices_list])
                    ids = [item[0] for item in invoice_records]
                    with open('deleters/invoice_record_links.sql', 'a') as invoice_record_links_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM invoice_record_links WHERE id in ( ',
                                      file=invoice_record_links_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=invoice_record_links_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=invoice_record_links_file)
                                        break
                        else:
                            print('DELETE FROM invoice_record_links WHERE id in ( ', file=invoice_record_links_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=invoice_record_links_file)
                                else:
                                    print(ids[i], ');', file=invoice_record_links_file)

                        console_text.insert(tk.END, 'Удаление записей invoice_record_links собраны\n')

    def invoice_record_links_backup(self):
        if len(records_from_google_list) == 0:
            console_text.insert(tk.END, "Нет записей invoice_record_links бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM invoice_record_links WHERE ' \
                        f'id IN ({invoice_records_list_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей invoice_records_list_str для бэкапа\n")
                else:
                    with open('backups/invoice_record_links(google_records)_backup.sql', 'a',
                              encoding='utf-8') as invoice_record_links_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO invoice_record_links '
                                      '(id, order_id, record_id, item_type, item_id, item_catalog_id, '
                                      'cost, redirect_prefix, source_slug) '
                                      'VALUES ', file=invoice_record_links_backup)
                                print(
                                    f'({row[0]}, \'{row[1]}\', {row[2]}, {row[3]}, '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,\'{row[8]}\''
                                    f' ),', file=invoice_record_links_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, \'{row[1]}\', {row[2]}, {row[3]}, '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,\'{row[8]}\' '
                                    f');', file=invoice_record_links_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO invoice_record_links '
                                      '(id, order_id, record_id, item_type, item_id, item_catalog_id, '
                                      'cost, redirect_prefix, source_slug) '
                                      'VALUES ', file=invoice_record_links_backup)
                                print(
                                    f'({row[0]}, \'{row[1]}\', {row[2]}, {row[3]}, '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,\'{row[8]}\' '
                                    f');',
                                    file=invoice_record_links_backup)
                            else:
                                print(
                                    f'({row[0]}, \'{row[1]}\', {row[2]}, {row[3]}, '
                                    f'{row[4]}, {row[5]}, {row[6]}, \'{row[7]}\' ,\'{row[8]}\' '
                                    f'),', file=invoice_record_links_backup)
                                counter += 1
                        console_text.insert(tk.END, 'invoice_record_links_backup готов \n')

    def invoces_record(self):
        if len(order_id_record_invoices_list) >= 1:
            with connection.cursor() as cursor:
                query = f'SELECT id FROM invoice WHERE order_id IN ({order_id_record_invoices_str});'
                cursor.execute(query)
                invoices_mt = cursor.fetchall()
                cursor.close()
                if not invoices_mt:
                    console_text.insert(tk.END, "Нет чаевых в записях\n")
                else:
                    ids = [item[0] for item in invoices_mt]
                    with open('deleters/invoices(invoice_records_link).sql', 'a') as invoices_records_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM invoice WHERE id in ( ', file=invoices_records_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=invoices_records_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=invoices_records_file)
                                        break
                        else:
                            print('DELETE FROM invoice WHERE id in ( ', file=invoices_records_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=invoices_records_file)
                                else:
                                    print(ids[i], ');', file=invoices_records_file)
        else:
            console_text.insert(tk.END, 'Нет строк в invoices  по записям\n')

    def invoices_records_backup(self):
        if len(order_id_record_invoices_list) == 0:
            console_text.insert(tk.END, "Нет инвойсов Записей для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM invoice WHERE order_id IN ({order_id_record_invoices_str});'
                cursor.execute(query)
                result_mt = cursor.fetchall()
                cursor.close()
                if not result_mt:
                    console_text.insert(tk.END, "Нет строк для бэкапа\n")
                else:
                    with open('backups/invoices(invoice_records_link)_backup.sql', 'a', encoding='utf-8') as invoices_record_backup:
                        counter = 0
                        for row in result_mt:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0:
                                print('INSERT INTO invoice '
                                      '(id, salon_id, status, payment_system_id, payment_type_id, order_id, ps_transaction_id, '
                                      'sum, ps_sum, payout_sum, currency_id, currency_rate, client_id, ps_account_id, is_test, '
                                      'date_create, date_ps_payment, date_payout, title, comment) '
                                      'VALUES', file=invoices_record_backup)
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},\'{row[15]}\', '
                                    f'\'{row[16]}\',\'{row[17]}\',\'{row[18]}\', \'{row[19]}\'),', file=invoices_record_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result_mt) - 1:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},\'{row[15]}\', '
                                    f'\'{row[16]}\',\'{row[17]}\',\'{row[18]}\', \'{row[19]}\');', file=invoices_record_backup)
                                counter = 0
                            else:
                                print(
                                    f'({row[0]},{row[1]},{row[2]},{row[3]},{row[4]},\'{row[5]}\',\'{row[6]}\',{row[7]}, '
                                    f'{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},\'{row[15]}\', '
                                    f'\'{row[16]}\',\'{row[17]}\',\'{row[18]}\', \'{row[19]}\'),', file=invoices_record_backup)
                                counter += 1
                        console_text.insert(tk.END, 'invoices_record_backup backup готов \n')

    def presetted_record_links(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит записей\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM presetted_record_links ' \
                        f'WHERE tt_record_id ' \
                        f'IN ({self.__records_list});'
                cursor.execute(query)
                presetted_record_links_rows = cursor.fetchall()
                cursor.close()
                if not presetted_record_links_rows:
                    console_text.insert(tk.END, "Нет записей в presetted_record_links\n")
                else:
                    ids = [item[0] for item in presetted_record_links_rows]
                    with open('deleters/presetted_record_links.sql', 'a') as presetted_record_links_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM presetted_record_links WHERE id in ( ',
                                      file=presetted_record_links_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=presetted_record_links_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=presetted_record_links_file)
                                        break
                        else:
                            print('DELETE FROM presetted_record_links WHERE id in ( ', file=presetted_record_links_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=presetted_record_links_file)
                                else:
                                    print(ids[i], ');', file=presetted_record_links_file)

                        console_text.insert(tk.END, 'Удаление записей в presetted_record_links собраны\n')

    def presetted_record_links_backup(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, "Нет записей presetted_record_links бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM presetted_record_links WHERE ' \
                        f'tt_record_id IN ({self.__records_list});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей presetted_record_links для бэкапа\n")
                else:
                    with open('backups/presetted_record_links_backup.sql', 'a',
                              encoding='utf-8') as presetted_record_links_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO presetted_record_links '
                                      '(id, salon_id, tt_record_id) '
                                      'VALUES', file=presetted_record_links_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f' ),', file=presetted_record_links_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f');', file=presetted_record_links_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO presetted_record_links '
                                      '(id, salon_id, tt_record_id) '
                                      'VALUES', file=presetted_record_links_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f');',
                                    file=presetted_record_links_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f'),', file=presetted_record_links_backup)
                                counter += 1
                        console_text.insert(tk.END, 'presetted_record_links_backup готов \n')

    def reception_qr_record_bind(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит записей\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM reception_qr_record_bind ' \
                        f'WHERE record_id ' \
                        f'IN ({self.__records_list});'
                cursor.execute(query)
                reception_qr_record_bind_rows = cursor.fetchall()
                cursor.close()
                if not reception_qr_record_bind_rows:
                    console_text.insert(tk.END, "Нет записей в presetted_record_links\n")
                else:
                    ids = [item[0] for item in reception_qr_record_bind_rows]
                    with open('deleters/reception_qr_record_bind.sql', 'a') as reception_qr_record_bind_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM reception_qr_record_bind WHERE id in ( ',
                                      file=reception_qr_record_bind_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=reception_qr_record_bind_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=reception_qr_record_bind_file)
                                        break
                        else:
                            print('DELETE FROM reception_qr_record_bind WHERE id in ( ', file=reception_qr_record_bind_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=reception_qr_record_bind_file)
                                else:
                                    print(ids[i], ');', file=reception_qr_record_bind_file)

                        console_text.insert(tk.END, 'Удаление записей в reception_qr_record_bind собраны\n')

    def reception_qr_record_bind_backup(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, "Нет записей reception_qr_record_bind для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM reception_qr_record_bind WHERE ' \
                        f'record_id IN ({self.__records_list});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей reception_qr_record_bind для бэкапа\n")
                else:
                    with open('backups/reception_qr_record_bind_backup.sql', 'a',
                              encoding='utf-8') as reception_qr_record_bind_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO reception_qr_record_bind '
                                      '(id, salon_id, record_id, activation_datetime, is_active) '
                                      'VALUES ', file=reception_qr_record_bind_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, \'{row[3]}\', {row[4]}'
                                    f' ),', file=reception_qr_record_bind_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, \'{row[3]}\', {row[4]}'
                                    f');', file=reception_qr_record_bind_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO reception_qr_record_bind '
                                      '(id, salon_id, record_id, activation_datetime, is_active) '
                                      'VALUES ', file=reception_qr_record_bind_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, \'{row[3]}\', {row[4]}'
                                    f');',
                                    file=reception_qr_record_bind_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, \'{row[3]}\', {row[4]}'
                                    f'),', file=reception_qr_record_bind_backup)
                                counter += 1
                        console_text.insert(tk.END, 'reception_qr_record_bind_backup готов \n')

    def records_labels_link(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит записей\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT record_id ' \
                        f'FROM records_labels_link ' \
                        f'WHERE record_id ' \
                        f'IN ({self.__records_list});'
                cursor.execute(query)
                records_labels_link_rows = cursor.fetchall()
                cursor.close()
                if not records_labels_link_rows:
                    console_text.insert(tk.END, "Нет записей в presetted_record_links\n")
                else:
                    ids = [item[0] for item in records_labels_link_rows]
                    with open('deleters/records_labels_link.sql', 'a') as records_labels_link_rows_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM records_labels_link WHERE record_id in ( ',
                                      file=records_labels_link_rows_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=records_labels_link_rows_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=records_labels_link_rows_file)
                                        break
                        else:
                            print('DELETE FROM records_labels_link WHERE record_id in ( ', file=records_labels_link_rows_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=records_labels_link_rows_file)
                                else:
                                    print(ids[i], ');', file=records_labels_link_rows_file)

                        console_text.insert(tk.END, 'Удаление записей в records_labels_link_rows собраны\n')

    def records_labels_link_backup(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, "Нет записей records_labels_link бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM records_labels_link WHERE ' \
                        f'record_id IN ({self.__records_list});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей records_labels_link для бэкапа\n")
                else:
                    with open('backups/records_labels_link_backup.sql', 'a',
                              encoding='utf-8') as records_labels_link_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO records_labels_link '
                                      '(record_id, label_id, position_id) '
                                      'VALUES', file=records_labels_link_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f' ),', file=records_labels_link_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f');', file=records_labels_link_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO records_labels_link '
                                      '(record_id, label_id, position_id) '
                                      'VALUES', file=records_labels_link_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f');',
                                    file=records_labels_link_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f'),', file=records_labels_link_backup)
                                counter += 1
                        console_text.insert(tk.END, 'records_labels_link_backup готов \n')


    def loyalty_group_clients_referral_links(self):
        if len(self.__visit_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит визитов\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM loyalty_group_clients_referral_links ' \
                        f'WHERE visit_id ' \
                        f'IN ({visit_ids_str});'
                cursor.execute(query)
                lgcrl_rows = cursor.fetchall()
                cursor.close()
                if not lgcrl_rows:
                    console_text.insert(tk.END, "Нет записей в loyalty_group_clients_referral_links\n")
                else:
                    ids = [item[0] for item in lgcrl_rows]
                    with open('deleters/loyalty_group_clients_referral_links.sql', 'a') as loyalty_group_clients_referral_links_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM loyalty_group_clients_referral_links WHERE id in ( ',
                                      file=loyalty_group_clients_referral_links_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=loyalty_group_clients_referral_links_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=loyalty_group_clients_referral_links_file)
                                        break
                        else:
                            print('DELETE FROM loyalty_group_clients_referral_links '
                                  'WHERE id in ( ', file=loyalty_group_clients_referral_links_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=loyalty_group_clients_referral_links_file)
                                else:
                                    print(ids[i], ');', file=loyalty_group_clients_referral_links_file)

                        console_text.insert(tk.END, 'Удаление записей в loyalty_group_clients_referral_links собраны\n')

    def loyalty_group_clients_referral_links_backup(self):
        if len(self.__visit_ids_global) == 0:
            console_text.insert(tk.END, "Нет записей визитов для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM loyalty_group_clients_referral_links WHERE ' \
                        f'visit_id IN ({visit_ids_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет строк в loyalty_group_clients_referral_links для бэкапа\n")
                else:
                    with open('backups/loyalty_group_clients_referral_links_backup.sql', 'a',
                              encoding='utf-8') as loyalty_group_clients_referral_links_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO loyalty_group_clients_referral_links '
                                      '(id, salon_group_id, visit_id, referrer_phone, referral_phone, document_id) '
                                      'VALUES', file=loyalty_group_clients_referral_links_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f' ),', file=loyalty_group_clients_referral_links_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f');', file=loyalty_group_clients_referral_links_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO records_labels_link '
                                      '(record_id, label_id, position_id) '
                                      'VALUES', file=loyalty_group_clients_referral_links_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f');',
                                    file=loyalty_group_clients_referral_links_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'),', file=loyalty_group_clients_referral_links_backup)
                                counter += 1
                        console_text.insert(tk.END, 'loyalty_group_clients_referral_links_backup готов \n')

    def visit_notification(self):
        if len(self.__visit_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит визитов\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM visit_notification ' \
                        f'WHERE visit_id ' \
                        f'IN ({visit_ids_str});'
                cursor.execute(query)
                visit_notification_rows = cursor.fetchall()
                cursor.close()
                if not visit_notification_rows:
                    console_text.insert(tk.END, "Нет записей в visit_notification\n")
                else:
                    ids = [item[0] for item in visit_notification_rows]
                    with open('deleters/visit_notification.sql', 'a') as visit_notification_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM visit_notification WHERE id in ( ',
                                      file=visit_notification_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=visit_notification_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=visit_notification_file)
                                        break
                        else:
                            print('DELETE FROM visit_notification '
                                  'WHERE id in ( ', file=visit_notification_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=visit_notification_file)
                                else:
                                    print(ids[i], ');', file=visit_notification_file)

                        console_text.insert(tk.END, 'Удаление записей в visit_notification собраны\n')

    def visit_notification_backup(self):
        if len(self.__visit_ids_global) == 0:
            console_text.insert(tk.END, "Нет строк в visit_notification для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM visit_notification WHERE ' \
                        f'visit_id IN ({visit_ids_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет строк в visit_notification для бэкапа\n")
                else:
                    with open('backups/visit_notification_backup.sql', 'a',
                              encoding='utf-8') as visit_notification_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO visit_notification '
                                      '(id, client_id, visit_id, salon_id, service_id, salon_service_id, '
                                      'record_id, notification_time, status, cdate) '
                                      'VALUES', file=visit_notification_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\', {row[8]}, \'{row[9]}\''
                                    f' ),', file=visit_notification_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\', {row[8]}, \'{row[9]}\''
                                    f');', file=visit_notification_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO visit_notification '
                                      '(id, client_id, visit_id, salon_id, service_id, salon_service_id, '
                                      'record_id, notification_time, status, cdate) '
                                      'VALUES', file=visit_notification_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\', {row[8]}, \'{row[9]}\''
                                    f');',
                                    file=visit_notification_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\', {row[8]}, \'{row[9]}\''
                                    f'),', file=visit_notification_backup)
                                counter += 1
                        console_text.insert(tk.END, 'visit_notification_backup готов \n')

    def visit_notification_setting(self):
        if len(self.__visit_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит визитов\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM visit_notification_setting ' \
                        f'WHERE visit_id ' \
                        f'IN ({visit_ids_str});'
                cursor.execute(query)
                visit_notification_rows = cursor.fetchall()
                cursor.close()
                if not visit_notification_rows:
                    console_text.insert(tk.END, "Нет записей в visit_notification_setting\n")
                else:
                    ids = [item[0] for item in visit_notification_rows]
                    with open('deleters/visit_notification_setting.sql', 'a') as visit_notification_setting_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM visit_notification_setting WHERE id in ( ',
                                      file=visit_notification_setting_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=visit_notification_setting_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=visit_notification_setting_file)
                                        break
                        else:
                            print('DELETE FROM visit_notification_setting '
                                  'WHERE id in ( ', file=visit_notification_setting_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=visit_notification_setting_file)
                                else:
                                    print(ids[i], ');', file=visit_notification_setting_file)

                        console_text.insert(tk.END, 'Удаление записей в visit_notification_setting собраны\n')

    def visit_notification_setting_backup(self):
        if len(self.__visit_ids_global) == 0:
            console_text.insert(tk.END, "Нет строк в visit_notification_setting для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM visit_notification_setting WHERE ' \
                        f'visit_id IN ({visit_ids_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет строк в visit_notification_setting для бэкапа\n")
                else:
                    with open('backups/visit_notification_setting_backup.sql', 'a',
                              encoding='utf-8') as visit_notification_setting_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO visit_notification_setting '
                                      '(id, visit_id, record_id, salon_id, service_id, '
                                      'salon_service_id, repeat_days_step, cdate) '
                                      'VALUES', file=visit_notification_setting_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\''
                                    f' ),', file=visit_notification_setting_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\''
                                    f');', file=visit_notification_setting_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO visit_notification_setting '
                                      '(id, visit_id, record_id, salon_id, service_id, '
                                      'salon_service_id, repeat_days_step, cdate) '
                                      'VALUES', file=visit_notification_setting_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\''
                                    f');',
                                    file=visit_notification_setting_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}'
                                    f'{row[6]}, \'{row[7]}\''
                                    f'),', file=visit_notification_setting_backup)
                                counter += 1
                        console_text.insert(tk.END, 'visit_notification_setting_backup готов \n')

    def medicine_appointments(self):
        global medicine_appontment_str, medicine_appontment_list
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит записей\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM medicine_appointments ' \
                        f'WHERE record_id ' \
                        f'IN ({self.__records_list});'
                cursor.execute(query)
                records_labels_link_rows = cursor.fetchall()
                cursor.close()
                if not records_labels_link_rows:
                    console_text.insert(tk.END, "Нет записей в medicine_appointments\n")
                else:
                    ids = [item[0] for item in records_labels_link_rows]
                    medicine_appontment_str = ', '.join([f'"{val}"' for val in ids])
                    medicine_appontment_list = copy.deepcopy(ids)
                    with open('deleters/medicine_appointments.sql', 'a') as medicine_appointments_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM medicine_appointments WHERE id in ( ',
                                      file=medicine_appointments_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=medicine_appointments_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=medicine_appointments_file)
                                        break
                        else:
                            print('DELETE FROM medicine_appointments WHERE id in ( ', file=medicine_appointments_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=medicine_appointments_file)
                                else:
                                    print(ids[i], ');', file=medicine_appointments_file)

                        console_text.insert(tk.END, 'Удаление записей в medicine_appointments собраны\n')

    def medicine_appointments_backup(self):
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, "Нет записей для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM medicine_appointments WHERE ' \
                        f'record_id IN ({self.__records_list});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей medicine_appointments для бэкапа\n")
                else:
                    with open('backups/medicine_appointments_backup.sql', 'a',
                              encoding='utf-8') as medicine_appointments_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO medicine_appointments '
                                      '(id, salon_id, record_id) '
                                      'VALUES', file=medicine_appointments_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f' ),', file=medicine_appointments_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f');', file=medicine_appointments_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO medicine_appointments '
                                      '(id, salon_id, record_id) '
                                      'VALUES', file=medicine_appointments_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f');',
                                    file=medicine_appointments_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]}'
                                    f'),', file=medicine_appointments_backup)
                                counter += 1
                        console_text.insert(tk.END, 'medicine_appointments_backup готов \n')

    def medicine_appointment_field_values(self):
        if len(medicine_appontment_list) == 0:
            console_text.insert(tk.END, 'Выборка не содержит записей\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id ' \
                        f'FROM medicine_appointment_field_values ' \
                        f'WHERE medicine_appointment_id ' \
                        f'IN ({medicine_appontment_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей в medicine_appointment_field_values\n")
                else:
                    ids = [item[0] for item in result]
                    with open('deleters/medicine_appointment_field_values.sql', 'a') as medicine_appointment_field_values_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM medicine_appointment_field_values WHERE id in ( ',
                                      file=medicine_appointment_field_values_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=medicine_appointment_field_values_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=medicine_appointment_field_values_file)
                                        break
                        else:
                            print('DELETE FROM medicine_appointment_field_values WHERE id in ( ', file=medicine_appointment_field_values_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=medicine_appointment_field_values_file)
                                else:
                                    print(ids[i], ');', file=medicine_appointment_field_values_file)

                        console_text.insert(tk.END, 'Удаление записей в medicine_appointment_field_values собраны\n')

    def medicine_appointment_field_values_backup(self):
        if len(medicine_appontment_list) == 0:
            console_text.insert(tk.END, "Нет записей для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM medicine_appointment_field_values WHERE medicine_appointment_id ' \
                        f'IN ({medicine_appontment_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей medicine_appointment_field_values для бэкапа\n")
                else:
                    with open('backups/medicine_appointment_field_values_backup.sql', 'a',
                              encoding='utf-8') as medicine_appointment_field_values_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO medicine_appointment_field_values '
                                      '(id, salon_id, medicine_appointment_id, medicine_appointment_salon_field_id, value) '
                                      'VALUES', file=medicine_appointment_field_values_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},{row[3]}, \'{row[4]}\''
                                    f' ),', file=medicine_appointment_field_values_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},{row[3]}, \'{row[4]}\''
                                    f');', file=medicine_appointment_field_values_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO medicine_appointment_field_values '
                                      '(id, salon_id, medicine_appointment_id, medicine_appointment_salon_field_id, value) '
                                      'VALUES', file=medicine_appointment_field_values_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},{row[3]}, \'{row[4]}\''
                                    f');',
                                    file=medicine_appointment_field_values_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},{row[3]}, \'{row[4]}\''
                                    f'),', file=medicine_appointment_field_values_backup)
                                counter += 1
                        console_text.insert(tk.END, 'medicine_appointment_field_values_backup готов \n')

    def resources_custom_fields_values(self):
        global resources_custom_fields_values_list, resources_custom_fields_values_str, custom_fields_values_id_str, cfv_id
        if len(self.__tt_record_ids_global) == 0:
            console_text.insert(tk.END, 'Выборка не содержит записей\n')
        else:
            with connection.cursor() as cursor:
                query = f'SELECT id, custom_fields_values_id ' \
                        f'FROM resources_custom_fields_values ' \
                        f'WHERE resource_id IN ({self.__records_list}) ' \
                        f'AND resource_slug = \'record\';'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей в resources_custom_fields_values\n")
                else:
                    ids = [item[0] for item in result]
                    resources_custom_fields_values_list = copy.deepcopy(ids)
                    resources_custom_fields_values_str = ', '.join([f'"{val}"' for val in resources_custom_fields_values_list])
                    cfv_id = [item[1] for item in result]
                    custom_fields_values_id_str = ', '.join([f"'{val}'" for val in cfv_id])
                    with open('deleters/resources_custom_fields_values.sql', 'a') as resources_custom_fields_values_file:
                        if len(ids) > 5000:
                            for i in range(len(ids) // 5000 + 1):
                                print('DELETE FROM resources_custom_fields_values WHERE id in ( ',
                                      file=resources_custom_fields_values_file)
                                for j in range(5000):
                                    id = ids.pop(0)
                                    print(id, ', ', file=resources_custom_fields_values_file)
                                    if len(ids) == 1 or j == 4999:
                                        id = ids.pop(0)
                                        print(id, ');', file=resources_custom_fields_values_file)
                                        break
                        else:
                            print('DELETE FROM resources_custom_fields_values WHERE id in ( ', file=resources_custom_fields_values_file)
                            for i in range(len(ids)):
                                if i != len(ids) - 1:
                                    print(ids[i], ', ', file=resources_custom_fields_values_file)
                                else:
                                    print(ids[i], ');', file=resources_custom_fields_values_file)

                        console_text.insert(tk.END, 'Удаление записей в resources_custom_fields_values собраны\n')

    def resources_custom_fields_values_backup(self):
        if len(resources_custom_fields_values_list) == 0:
            console_text.insert(tk.END, "Нет записей resources_custom_fields_values для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM resources_custom_fields_values WHERE id ' \
                        f'IN ({resources_custom_fields_values_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей resources_custom_fields_values для бэкапа\n")
                else:
                    with open('backups/resources_custom_fields_values_backup.sql', 'a',
                              encoding='utf-8') as resources_custom_fields_values_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO resources_custom_fields_values (id, resource_id, '
                                      'resource_slug, custom_fields_salon_resource_id, custom_fields_values_id) '
                                      'VALUES', file=resources_custom_fields_values_backup)
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\',{row[3]}, {row[4]}'
                                    f' ),', file=resources_custom_fields_values_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\',{row[3]}, {row[4]}'
                                    f');', file=resources_custom_fields_values_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO resources_custom_fields_values (id, resource_id, '
                                      'resource_slug, custom_fields_salon_resource_id, custom_fields_values_id) '
                                      'VALUES', file=resources_custom_fields_values_backup)
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\',{row[3]}, {row[4]}'
                                    f');',
                                    file=resources_custom_fields_values_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, \'{row[2]}\',{row[3]}, {row[4]}'
                                    f'),', file=resources_custom_fields_values_backup)
                                counter += 1
                        console_text.insert(tk.END, 'resources_custom_fields_values_backup готов \n')

    def custom_fields_values(self):
        if len(cfv_id) == 0:
            console_text.insert(tk.END, 'Выборка не содержит доп.полей\n')
        else:
            ids = copy.deepcopy(cfv_id)
            with open('deleters/custom_fields_values.sql', 'a') as custom_fields_values_file:
                if len(ids) > 5000:
                    for i in range(len(ids) // 5000 + 1):
                        print('DELETE FROM custom_fields_values WHERE id in ( ', file=custom_fields_values_file)
                        for j in range(5000):
                            id = ids.pop(0)
                            print(id, ', ', file=custom_fields_values_file)
                            if len(ids) == 1 or j == 4999:
                                id = ids.pop(0)
                                print(id, ');', file=custom_fields_values_file)
                                break
                else:
                    print('DELETE FROM custom_fields_values WHERE id in ( ', file=custom_fields_values_file)
                    for i in range(len(ids)):
                        if i != len(ids) - 1:
                            print(ids[i], ', ', file=custom_fields_values_file)
                        else:
                            print(ids[i], ');', file=custom_fields_values_file)
                console_text.insert(tk.END, 'Удаление записей в custom_fields_values собраны\n')

    def custom_fields_values_backup(self):
        if len(cfv_id) == 0:
            console_text.insert(tk.END, "Нет записей custom_fields_values для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM custom_fields_values WHERE id ' \
                        f'IN ({custom_fields_values_id_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей custom_fields_values для бэкапа\n")
                else:
                    with open('backups/custom_fields_values_backup.sql', 'a',
                              encoding='utf-8') as custom_fields_values_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO custom_fields_values (id, custom_fields_type_id, '
                                      'user_id, date_create) '
                                      'VALUES', file=custom_fields_values_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},\'{row[3]}\''
                                    f' ),', file=custom_fields_values_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},\'{row[3]}\''
                                    f');', file=custom_fields_values_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO custom_fields_values (id, custom_fields_type_id, '
                                      'user_id, date_create) '
                                      'VALUES', file=custom_fields_values_backup)
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},\'{row[3]}\''
                                    f');',
                                    file=custom_fields_values_backup)
                            else:
                                print(
                                    f'({row[0]}, {row[1]}, {row[2]},\'{row[3]}\''
                                    f'),', file=custom_fields_values_backup)
                                counter += 1
                        console_text.insert(tk.END, 'custom_fields_values готов \n')

    def custom_fields_scalar_values(self):
        if len(cfv_id) == 0:
            console_text.insert(tk.END, 'Выборка не содержит доп.полей\n')
        else:
            ids = copy.deepcopy(cfv_id)
            with open('deleters/custom_fields_scalar_values.sql', 'a') as custom_fields_scalar_values_file:
                if len(ids) > 5000:
                    for i in range(len(ids) // 5000 + 1):
                        print('DELETE FROM custom_fields_scalar_values WHERE custom_fields_values_id in ( ', file=custom_fields_scalar_values_file)
                        for j in range(5000):
                            id = ids.pop(0)
                            print(id, ', ', file=custom_fields_scalar_values_file)
                            if len(ids) == 1 or j == 4999:
                                id = ids.pop(0)
                                print(id, ');', file=custom_fields_scalar_values_file)
                                break
                else:
                    print('DELETE FROM custom_fields_scalar_values WHERE custom_fields_values_id in ( ', file=custom_fields_scalar_values_file)
                    for i in range(len(ids)):
                        if i != len(ids) - 1:
                            print(ids[i], ', ', file=custom_fields_scalar_values_file)
                        else:
                            print(ids[i], ');', file=custom_fields_scalar_values_file)
                console_text.insert(tk.END, 'Удаление записей в custom_fields_scalar_values собраны\n')

    def custom_fields_scalar_values_backup(self):
        if len(cfv_id) == 0:
            console_text.insert(tk.END, "Нет записей custom_fields_scalar_values для бэкапа\n")
        else:
            with connection.cursor() as cursor:
                query = f'SELECT * FROM custom_fields_scalar_values WHERE custom_fields_values_id ' \
                        f'IN ({custom_fields_values_id_str});'
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                if not result:
                    console_text.insert(tk.END, "Нет записей custom_fields_scalar_values для бэкапа\n")
                else:
                    with open('backups/custom_fields_scalar_values_backup.sql', 'a',
                              encoding='utf-8') as custom_fields_scalar_values_backup:
                        counter = 0
                        for row in result:
                            row = tuple('null' if x is None else x for x in row)
                            if counter == 0 and len(result) > 1:
                                print('INSERT INTO custom_fields_scalar_values '
                                      '(custom_fields_values_id, value) '
                                      'VALUES', file=custom_fields_scalar_values_backup)
                                print(
                                    f'({row[0]}, \'{row[1]}\''
                                    f' ),', file=custom_fields_scalar_values_backup)
                                counter += 1
                            elif counter == 5000 or counter == len(result) - 1 and len(result) != 1:
                                print(
                                    f'({row[0]}, \'{row[1]}\''
                                    f');', file=custom_fields_scalar_values_backup)
                                counter = 0
                            elif counter == 0 and len(result) == 1:
                                print('INSERT INTO custom_fields_scalar_values '
                                      '(custom_fields_values_id, value) '
                                      'VALUES', file=custom_fields_scalar_values_backup)
                                print(
                                    f'({row[0]}, \'{row[1]}\''
                                    f');',
                                    file=custom_fields_scalar_values_backup)
                            else:
                                print(
                                    f'({row[0]}, \'{row[1]}\''
                                    f'),', file=custom_fields_scalar_values_backup)
                                counter += 1
                        console_text.insert(tk.END, 'custom_fields_scalar_values_backup готов \n')



def start_application():
    # Собираю входные значения для ЭК
    date_from = date_from_entry.get()
    date_to = date_to_entry.get()
    salon_id = salon_id_entry.get()
    cdate_from = cdate_from_entry.get()
    cdate_to = cdate_to_entry.get()
    user_id = user_id_entry.get()
    deleted = selected_option.get()

    # Создаю ЭК
    records = Records(date_from, date_to, salon_id, deleted, cdate_from, cdate_to, user_id)

    # Вызываю все методы по порядку
    # Вывожу информацию в консоль
    console_text.insert(tk.END, "Начало выполнения методов...\n")



    # Вызываю все методы по порядку и вывожу информацию в консоль
    records.delete_standart()
    records.tt_records_backup()
    if deleted != '1':
        records.client_visits_delete()
        records.client_visits_backup()
    records.tt_services_delete()
    records.tt_services_backup()
    records.master_tips()
    records.master_tips_backup()
    records.master_tips_invoices()
    records.master_tips_invoices_backup()
    records.tips_invoces()
    records.invoices_tips_backup()
    records.documents_delete()
    records.documents_backup()
    records.transactions_delete()
    records.transactions_backup()
    records.goods_transactions_delete()
    records.goods_transactions_backup()
    records.record_resourse_link()
    records.record_resource_instances_link_backup()
    records.tt_resources_occupation()
    records.tt_resources_occupation_backup()
    records.google_booking_records()
    records.google_booking_records_backup()
    records.invoice_record_links()
    records.invoice_record_links_backup()
    records.invoces_record()
    records.invoices_records_backup()
    records.presetted_record_links()
    records.presetted_record_links_backup()
    records.reception_qr_record_bind()
    records.reception_qr_record_bind_backup()
    records.records_labels_link()
    records.records_labels_link_backup()
    records.loyalty_group_clients_referral_links()
    records.loyalty_group_clients_referral_links_backup()
    records.medicine_appointments()
    records.medicine_appointments_backup()
    records.medicine_appointment_field_values()
    records.medicine_appointment_field_values_backup()
    records.resources_custom_fields_values()
    records.resources_custom_fields_values_backup()
    records.custom_fields_values()
    records.custom_fields_values_backup()
    records.custom_fields_scalar_values()
    records.custom_fields_scalar_values_backup()
    console_text.insert(tk.END, "Готово! Проверь данные!")

    # Очистить входные поля после завершения сборки
    date_from_entry.delete(0, tk.END)
    date_to_entry.delete(0, tk.END)
    salon_id_entry.delete(0, tk.END)
    cdate_from_entry.delete(0, tk.END)
    cdate_to_entry.delete(0, tk.END)
    user_id_entry.delete(0, tk.END)

# Главное окно
window = tk.Tk()
window.title("Запросы на удаление записей")

# Входные поля
date_from_label = tk.Label(window, text="Дата визита от:")
date_from_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")
date_from_entry = DateEntry(window, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
date_from_entry.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")

date_to_label = tk.Label(window, text="Дата визита до:")
date_to_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="e")
date_to_entry = DateEntry(window, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
date_to_entry.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="w")

salon_id_label = tk.Label(window, text="введи ID филиала:")
salon_id_label.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="e")
salon_id_entry = tk.Entry(window)
salon_id_entry.grid(row=2, column=1, padx=(0, 10), pady=10, sticky="w")

cdate_from_label = tk.Label(window, text="Дата создания от\nНапример 1970-01-01. Иначе оставь пустым: ")
cdate_from_label.grid(row=3, column=0, padx=(10, 5), pady=10, sticky="e")
cdate_from_entry = tk.Entry(window)
cdate_from_entry.grid(row=3, column=1, padx=(0, 10), pady=10, sticky="w")


cdate_to_label = tk.Label(window, text="Дата создания до\nНапример 1970-01-01. Иначе оставь пустым: ")
cdate_to_label.grid(row=4, column=0, padx=(10, 5), pady=5, sticky="e")
cdate_to_entry = tk.Entry(window)
cdate_to_entry.grid(row=4, column=1, padx=(0, 10), pady=5, sticky="w")

user_id_label = tk.Label(window, text="Введи ID пользователя который создал записи. \nИначе оставь пустым:")
user_id_label.grid(row=5, column=0, padx=(10, 5), pady=5, sticky="e")
user_id_entry = tk.Entry(window)
user_id_entry.grid(row=5, column=1, padx=(0, 10), pady=5, sticky="w")

options = ['-1', '0', '1']
selected_option = tk.StringVar(value=options[0])
del_label = tk.Label(window, text="-1 - удаленные и не удаленные, \n0 - не удаленные записи, 1 - удаленные записи:")
del_label.grid(row=6, column=0, padx=(10, 5), pady=5, sticky="e")
select = tk.OptionMenu(window,  selected_option, *options)
select.grid(row=6, column=1, padx=(0, 10), pady=5, sticky="w")

# Стартер
start_button = tk.Button(window, text="Запустить", command=start_application)
start_button.grid(row=7,column=0, padx=0, pady=10, sticky="e")

# Консоль
console_text = scrolledtext.ScrolledText(window, height=15, width=60)
console_text.configure(bg="#1a4780", fg="yellow")
console_text.grid(row=8, column=0, columnspan=2)

#Предупреждашка для коллег
console_text.insert(tk.END, 'Дату можно ввести руками или открыть календарь\n')
console_text.insert(tk.END, 'Доверяй, но проверяй. \nПосмотри, что бы готовые файлы не имели ошибок\n')
window.mainloop()

# ████████▒▒ 80% Боевой готовности
# Не забудь что то придумать с лояльностью. Например добавить чекбоксы "удалить транзакции!!
# лояльности по абонементам и сертификатам проданным в визитах".
# Опциональная возможность списать с карт лояльности сумму транзакций или выпилить карты лояльности у клиентов массово
# блокируют ли отзывы удаление записей (master_comments)

# ожидаемые функции которые можно вынести отдельным окном или попробовать сделать свою интеграцию:
# Удаление расчетных ведомостей, Удаленией правил РЗП, Удаление схем РЗП (Специафические запросы)
# Удаление товаров (конкретная категория или все категории), (Обычный API)
# Удаление КБ
# Удаление услуг