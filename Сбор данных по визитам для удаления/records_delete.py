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

records_with_resources_str = ''

class Records:
    #Создание экземпляра класса. Дата создания и пользователь могут быть пустыми.
    #Их буду использовать только если требуется удаление всех записей конкретного пользователя
    #Или созданные в конкретное время
    def __init__(self, date_from, date_to, salon_id, deleted, cdate_from=None, cdate_to = None, user_id = None):
        self.__date_from  = self.validate_date(date_from)
        self.__date_to = self.validate_date(date_to)
        self.__salon_id = int(salon_id)
        self.__deleted = [1, 0] if deleted == '-1' else (['1'] if deleted == '1' else [0])
        self.__cdate_from = self.validate_date(cdate_from) if cdate_from not in '' else None
        self.__cdate_to = self.validate_date(cdate_to)  if cdate_to not in '' else None
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

    def validate_date(self, date):
        try:
            new_date = datetime.strptime(date, '%Y-%m-%d').date()
            return str(new_date)
        except ValueError:
            console_text.insert(tk.END, "Некорректная дата \n")
            raise ValueError('Некорректная дата')
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
                                 f'and cdate <= "{self.__cdate_to} 00:00:00" ' \
                                 f'and deleted in ({", ".join(str(n) for n in self.__deleted)});'

                #Дата записи, дата создания и пользователь
                sql_with_cdate_and_user = f'select id from tt_records where date >= "{self.__date_from} 00:00:00" ' \
                                          f'and date <= "{self.__date_to} 23:59:59" ' \
                                          f'and salon_id = {self.__salon_id} ' \
                                          f'and cdate >= "{self.__cdate_from} 00:00:00" ' \
                                          f'and cdate <= "{self.__cdate_to} 00:00:00" ' \
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
                    console_text.insert(tk.END,"Результат пустой. Проверь запрос снова\n")

                else:
                    ids = [item[0] for item in result]
                    self.__tt_record_ids_global = copy.deepcopy(ids)
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
        finally:
            console_text.insert(tk.END,'tt_records готов\n')
            cursor.close()

    def tt_records_backup(self):
        #Собираю Бэкап по списку ID записей которые собрали для удаления.
        try:
            with connection.cursor() as cursor:
                if len(self.__tt_record_ids_global) >=1:
                    values_str = ', '.join([f'"{val}"' for val in self.__tt_record_ids_global])
                    self.__records_list = copy.deepcopy(values_str)
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
        finally:
            cursor.close()

#Собираю файл client_visits
    def client_visits_delete(self):
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
                elif counter == 5000 or counter == len(result) - 1:
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
            console_text.insert(tk.END, "Нет Записей для удаления\n")
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
                    console_text.insert(tk.END, "Нет услуг в записях\n")
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
                        console_text.insert(tk.END, 'invoce_tips_backup готов \n')

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

                if not result:
                    console_text.insert(tk.END, 'Завершение команды\n')
                else:
                    self.__documents_list = [item[0] for item in result]
                    self.__documents_ids = ', '.join([f'"{val}"' for val in self.__documents_list])
                    ids = copy.deepcopy((self.__documents_list))
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
        global goods_transactions_ids
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
                        console_text.insert(tk.END, 'В записях нет продаж абонементов')

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
            console_text.insert(tk.END, 'Выборка не содержит записей c ресурсами')
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
                                print('DELETE FROM record_resource_instances_link WHERE record_id in ( ', file=transactions_file)
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
                    console_text.insert((tk.END, 'Говорил же, что нет записей с ресурсами'))
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
                            elif counter == 0 and len(result) == 1:
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
            console_text.insert(tk.END, 'Выборка не содержит записей c ресурсами')
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
            console_text.insert(tk.END, "Нет записей с ресурсами для удаления\n")
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
                            elif counter == 5000 or counter == len(result) - 1:
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
    console_text.insert(tk.END, "Метод delete_standart выполнен.\n")
    records.tt_records_backup()
    console_text.insert(tk.END, "Метод tt_records_backup выполнен.\n")
    if deleted != '1':
        records.client_visits_delete()
        console_text.insert(tk.END, "Метод client_visits_delete выполнен.\n")
        records.client_visits_backup()
        console_text.insert(tk.END, "Метод client_visits_backup выполнен.\n")
    records.tt_services_delete()
    console_text.insert(tk.END, "Метод tt_services_delete выполнен. \n")
    records.tt_services_backup()
    console_text.insert(tk.END, "Метод tt_services_backup выполнен. \n")
    records.master_tips()
    console_text.insert(tk.END, 'master_tips выполнен\n')
    records.master_tips_backup()
    console_text.insert(tk.END, 'master_tips_backup выполнен\n')
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
date_from_label = tk.Label(window, text="Выбери дату от которой искать записи:")
date_from_label.pack()
date_from_entry = DateEntry(window, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
date_from_entry.pack()

date_to_label = tk.Label(window, text="Выбери дату до которой искать записи:")
date_to_label.pack()
date_to_entry = DateEntry(window, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
date_to_entry.pack()

salon_id_label = tk.Label(window, text="введи ID филиала:")
salon_id_label.pack()
salon_id_entry = tk.Entry(window)
salon_id_entry.pack()

cdate_from_label = tk.Label(window, text="Введи дату создания от которой искать записи. Например 1970-01-01. Иначе оставь пустым: ")
cdate_from_label.pack()
cdate_from_entry = tk.Entry(window)
cdate_from_entry.pack()


cdate_to_label = tk.Label(window, text="Введи дату создания до которой искать записи. Например 1970-01-01. Иначе оставь пустым: ")
cdate_to_label.pack()
cdate_to_entry = tk.Entry(window)
cdate_to_entry.pack()

user_id_label = tk.Label(window, text="введи ID пользователя который создал записи. Иначе оставь пустым:")
user_id_label.pack()
user_id_entry = tk.Entry(window)
user_id_entry.pack()

options = ['-1', '0', '1']
selected_option = tk.StringVar(value=options[0])
del_label = tk.Label(window, text="-1 - удаленные и не удаленные, 0 не удаленные записи, 1 удаленные записи:")
del_label.pack()
select = tk.OptionMenu(window,  selected_option, *options)
select.pack()

# Стартер
start_button = tk.Button(window, text="Запустить", command=start_application)
start_button.pack()

# Консоль
console_text = scrolledtext.ScrolledText(window)
console_text.configure(bg="#1a4780", fg="yellow")
console_text.pack()

#Предупреждашка для коллег
console_text.insert(tk.END, 'Дату можно ввести руками или открыть календарь\n')
console_text.insert(tk.END, 'Доверяй, но проверяй. \nПосмотри, что бы готовые файлы не имели ошибок\n')
window.mainloop()

# ██████▒▒▒▒ 60% Боевой готовности
# Не забудь что то придумать с лояльностью. Например добавить чекбоксы "удалить транзакции!! IMPORTANT! first_priority!
# лояльности по абонементам и сертификатам проданным в визитах". Не забудь обработать сами визиты IMPORTANT! first_priority!
# и удалить транзакции в них. IMPORTANT! first_priority!
# record_resource_instances_link IMPORTANT! second_priority!
# Опциональная возможность списать с карт лояльности сумму транзакций или выпилить карты лояльности у клиентов массово
# Оставшиеся таблицы для обработки скриптом(не часто используются): google_booking_records, invoice(invoice_record_links),
# presetted_record_links, record_resource_instances_link, reception_qr_record_bind, tt_records_changes,
# records_label_links
# Проверить таблицы _old, проверить
# блокируют ли отзывы удаление записей (master_comments)

# ожидаемые функции которые можно вынести отдельным окном или попробовать сделать свою интеграцию:
# Удаление расчетных ведомостей, Удаленией правил РЗП, Удаление схем РЗП (Специафические запросы)
# Удаление товаров (конкретная категория или все категории), (Обычный API)
# Удаление КБ
# Удаление услуг