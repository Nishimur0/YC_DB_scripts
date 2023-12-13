import codecs
import pymysql.cursors
import tkinter as tk
from tkinter import scrolledtext
from babel import numbers

config = {
    'user': '',
    'password': '',
    'host': '',
    'database': ''
}
def update_sql_statement():
    custom_fields_resource_id = int(custom_fields_resource_id_entry.get())
    words_to_code = []

    try:
        connection = pymysql.connect(**config)
    except Exception as e:
        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Не удалось установить соединение с базой данных: {e}")
        result_text.config(state='disabled')
        return

    try:
        with connection.cursor() as cursor:
            query = f"select id, available_values " \
                    f"from custom_fields_resources_available_values " \
                    f"where custom_fields_resource_id = {custom_fields_resource_id} " \
                    f"LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchall()
            current_words = str(result[0][1].replace("\\", "\\\\"))
            cfrav_id = int(result[0][0])
    finally:
        connection.close()

    input_text = input_words_text.get(1.0, tk.END).strip()
    words_to_code = input_text.split('\n')

    encoded_words = [codecs.encode(f'"{word.strip()}"', 'unicode_escape').decode().replace("\\", "\\\\") for word in words_to_code]
    encoded_string = ", ".join(encoded_words)
    result_string = current_words.lstrip("[").rstrip("]") + "," + encoded_string

    sql_statement = f"UPDATE custom_fields_resources_available_values SET available_values = " \
                    f"\'[{result_string}]\' WHERE id = {cfrav_id}"
    sql_backup = f"UPDATE custom_fields_resources_available_values SET available_values = " \
                    f"\'{current_words}\' WHERE id = {cfrav_id}"

    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Запрос:\n")
    result_text.insert(tk.END, sql_statement)

    result_text2.config(state='normal')
    result_text2.delete(1.0, tk.END)
    result_text2.insert(tk.END, "Бэкап:\n")
    result_text2.insert(tk.END, sql_backup)

root = tk.Tk()
root.title("Генератор запроса добавить значение доп.поля")

custom_fields_resource_id_label = tk.Label(root, text="custom_fields_resource_id:")
custom_fields_resource_id_label.pack()
custom_fields_resource_id_entry = tk.Entry(root)
custom_fields_resource_id_entry.pack()

input_words_label = tk.Label(root, text="Введи значения для кодировки (Одно значение - одна строка):")
input_words_label.pack()
input_words_text = tk.Text(root, height=5, width=40)
input_words_text.pack()

result_text = scrolledtext.ScrolledText(root, width=40, height=10)
result_text.pack()
result_text.config(state='disabled')
result_text2 = scrolledtext.ScrolledText(root, width=40, height=10)
result_text2.pack()
result_text2.config(state='disabled')

generate_button = tk.Button(root, text="Покажи запрос!", command=update_sql_statement)
generate_button.pack()

root.mainloop()
