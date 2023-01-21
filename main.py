import argparse
import csv
import os
from datetime import datetime
from functools import reduce

from store import Store


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HOURS = [f'0{str(x)}' if len(str(x)) < 2 else str(x) for x in range(25)]


def create_stores():
    result = {}
    file_name = os.path.join(BASE_DIR, 'data', 'Stores.csv')
    with open(file_name, encoding='Windows-1251') as r_file:
        file_reader = csv.reader(r_file, delimiter=";")
        for index, item in enumerate(file_reader):
            if index == 0 or result.get(item[0]):
                continue
            store = Store(item[0], item[1], item[2])
            result.update({store.name: store})
    return result


def fill_sales(stores):
    cut_hour = lambda x: int(item[2].split(':')[0])
    file_name = os.path.join(BASE_DIR, 'data', 'Data.csv')
    with open(file_name, encoding='Windows-1251') as r_file:
        file_reader = csv.reader(r_file, delimiter=";")
        for index, item in enumerate(file_reader):
            if index == 0 or stores.get(item[3]) is None:
                continue
            store = stores.get(item[3])
            date = datetime.strptime(item[1], '%d.%m.%Y')
            if store.current_sales.get(date):
                if store.current_sales[date].get(cut_hour(item[2])):
                    store.current_sales[date][cut_hour(item[2])] += 1
                else:
                    store.current_sales[date].update({cut_hour(item[2]): 1})
            else:
                store.current_sales.update({date: {cut_hour(item[2]): 1}})


def future_staff_report(stores):
    file_name = os.path.join(BASE_DIR, 'data', 'FutureStaff.csv')
    name_of_fields = ['Магазин', 'Дата', 'Общее кол-во доп.раб. (4 часа)']
    name_of_fields.extend(HOURS)
    with open(file_name, mode="w", encoding='Windows-1251') as w_file:
        file_writer = csv.writer(w_file, delimiter=";")
        file_writer.writerow(name_of_fields)
        names_stores = list(stores.keys())
        for name in names_stores:
            dates = list(stores[name].future_staff.keys())
            for date in dates:
                data = [name, ]
                data.append(date.strftime("%d.%m.%Y"))
                list_of_hours = list(stores[name].future_staff[date].values())
                general_number = reduce(lambda x, y: x+y, list_of_hours)
                data.append(general_number)
                for hour in HOURS:
                    number = stores[name].future_staff[date].get(int(hour), 0)
                    data.append(number if number > 0 else '')
                file_writer.writerow(data)


def future_sales_report(stores):
    file_name = os.path.join(BASE_DIR, 'data', 'FutureSales.csv')
    name_of_fields = ['Магазин', 'Дата']
    name_of_fields.extend(HOURS)
    with open(file_name, mode="w", encoding='Windows-1251') as w_file:
        file_writer = csv.writer(w_file, delimiter=";")
        file_writer.writerow(name_of_fields)
        names_stores = list(stores.keys())
        for name in names_stores:
            dates = list(stores[name].future_sales.keys())
            for date in dates:
                data = [name, ]
                data.append(date.strftime("%d.%m.%Y"))
                for hour in HOURS:
                    number = stores[name].future_sales[date].get(int(hour), 0)
                    data.append(number if number > 0 else '')
                file_writer.writerow(data)


def main(days):
    stores = create_stores()
    fill_sales(stores)
    for store in stores.values():
        store.calculate_future_sales(days)
        store.calculate_future_staff()
    future_staff_report(stores)
    future_sales_report(stores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", help="number of days to forecast", type=str)
    args = parser.parse_args()

    days = int(args.days) if args.days and args.days.isdigit() else 7
    main(days)
