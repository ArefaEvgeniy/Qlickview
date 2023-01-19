from datetime import timedelta


class Store():
    week = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    max_checks = 20

    def __init__(self, name, address, working_mode):
        self.name = name
        self.address = address
        self.mode = self.set_mode(working_mode)
        self.current_sales = {}
        self.future_sales = {}
        self.future_staff = {}

    def fill_mode(self, start_day, end_day, start_hours, end_hours):
        res = {}
        cur_days = []
        start = False
        for day in self.week:
            if start_day == day:
                start = True
            if start:
                cur_days.append(day)
            if end_day == day:
                break
        for day in cur_days:
            res.update({day: [x for x in range(start_hours, end_hours+1)]})
        return res

    def set_mode(self, working_mode):
        result = {}
        if working_mode.lower() == 'круглосуточный':
            result = self.fill_mode(self.week[0], self.week[-1], 0, 24)
        else:
            items = working_mode.lower().split(';')
            for item in items:
                days = item.split()[0]
                hours = item.split()[-1]
                start_day = days.split('-')[0]
                end_day = days.split('-')[-1]
                start_hour = hours.split('-')[0]
                end_hour = hours.split('-')[-1]
                result.update(self.fill_mode(start_day, end_day,
                                             int(start_hour), int(end_hour)))
        return result

    def calculate_future_sales(self, days):
        first_calc_day = list(self.current_sales.keys())[0]
        for item in self.current_sales.keys():
            first_calc_day = item if item > first_calc_day else first_calc_day
        first_calc_day += timedelta(days=1)
        for day in range(0, days):
            calc_day = first_calc_day + timedelta(days=day)
            date = calc_day - timedelta(days=7)
            self.future_sales.update({calc_day: self.current_sales.get(date, {})})

    def calculate_future_staff(self):
        for day in self.future_sales:
            self.future_staff.update({day: {}})
            hours = self.mode.get(self.week[day.isoweekday() - 1])
            staff = {}
            add_pers = []
            for hour in hours:
                add_pers = list(map(lambda x: x - 1, add_pers))
                add_pers = list(filter(lambda x: x > 0, add_pers))
                persons = self.future_sales[day].get(hour, 0) // self.max_checks
                persons -= len(add_pers)
                persons = persons if persons >= 0 else 0
                if persons > 0:
                    add_pers.append(4)
                staff.update({hour: persons})
            self.future_staff[day].update(staff)
