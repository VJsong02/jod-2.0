from datetime import date, datetime

payments = { 
    # 2020 - 2021
    date(2020,  8, 31): (7568,  3292 - 150),  # uppläggningsavgift
    date(2020,  9, 25): (7568,  3292),
    date(2020, 10, 23): (7568,  3292),
    date(2020, 11, 25): (7568,  3292),
    date(2020, 12, 23): (7592,  3302),
    date(2021,  1, 18): (11424, 4968 - 150),  # uppläggningsavgift
    date(2021,  2, 25): (7616,  3312),
    date(2021,  3, 25): (7616,  3312),
    date(2021,  4, 23): (7616,  3312),
    date(2021,  5, 25): (3808,  1656),
    
    # 2021 - 2022
    date(2021,  8, 30): (7616,  3312 - 150),  # uppläggningsavgift
    date(2021,  9, 24): (7616,  3312),
    date(2021, 10, 25): (7616,  3312),
    date(2021, 11, 25): (7616,  3312),
    date(2021, 12, 23): (7672,  3336),
    date(2022,  1, 17): (11592, 5040 - 150),  # uppläggningsavgift
    date(2022,  2, 25): (7728,  3360),
    date(2022,  3, 25): (7728,  3360),
    date(2022,  4, 25): (7728,  3360),
    date(2022,  5, 25): (3864,  1680),
    
    # 2022 - 2023
    date(2022,  8, 29): (7728,  3360 - 150),  # uppläggningsavgift
    date(2022,  9, 23): (7728,  3360),
    date(2022, 10, 25): (7728,  3360),
    date(2022, 11, 25): (7728,  3360),
    date(2022, 12, 23): (8064,  3506),
    date(2023,  1, 16): (12600, 5478 - 150),  # uppläggningsavgift
    date(2023,  2, 24): (8400,  3652),
    date(2023,  3, 24): (8400,  3652),
    date(2023,  4, 25): (8400,  3652),
    date(2023,  5, 25): (4200,  1826),
    
    # 2023 - 2024
    date(2023,  8, 28): (10500, 4565 - 150),  # uppläggningsavgift
    date(2023,  9, 25): (7728,  3360),
    date(2023, 10, 25): (7728,  3360),
    date(2023, 11, 24): (7728,  3360),
    date(2023, 12, 22): (6300,  2739),
    date(2024,  1, 15): (12600, 5478 - 150),  # uppläggningsavgift
    date(2024,  2, 23): (8400,  3652),
    date(2024,  3, 25): (8400,  3652),
    date(2024,  4, 25): (8400,  3652),
    date(2024,  5, 24): (4200,  1826),
}

interests = {
    2020: 1.0016,
    2021: 1.0005,
    2022: 1.0000,
    2023: 1.0059
}

def calc_debt(now=None):
    if(now == None):
        now = date.today()
    borrowed = 0
    debt = 0
    granted = 0
    prevday = None
    for (day, (loan, grant)) in list(payments.items())+[(now, (0, 0))]:
        if(day <= now):
            if(prevday):
                if(prevday.year == day.year):
                    debt *= (interests[day.year] ** ((day-prevday).days / 365))
                else:
                    newyear = date(day.year-1, 12, 31)
                    debt *= (interests[day.year] ** ((day-newyear).days / 365)) * (interests[prevday.year] ** ((newyear-prevday).days / 365))
            debt += loan
            borrowed += loan
            granted += grant
            prevday = day
    return (borrowed, debt, granted)

