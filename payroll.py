# -*- coding: utf-8 -*-
'''
Created on 2014年9月30日

@author: Soul
'''
import re
import calendar as cal
from datetime import datetime
from datetime import timedelta
from datetime import date
# import httplib
# import urllib
# import json

DATE_FORMAT = "%Y-%m-%d"

def get_input(prompt, pattern=None, default=None):
    result = None
    while True:
        input_str = raw_input(prompt).strip()
        if not input_str:
            if default != None:
                result = default
            else:
                continue
        elif pattern and not re.match(pattern, input_str):
            print '格式错误！'
            continue
        else:
            result = input_str
        if result != None:
            break
    return result


def get_day_avg_pay(year, month, month_pay):
    month_day_count = cal.monthrange(year, month)[1]
    work_day_count = get_work_day_count(year, month, 1, month_day_count)
    return month_pay / float(work_day_count)


def get_work_day_count(year, month, start_day, end_day):
    work_day_count = 0
    for day in range(start_day, end_day + 1):
        # 5,6 代表周六、周日
        if cal.weekday(year, month, day) == 6: continue
        work_day_count += 1
    return work_day_count


def pay_month(start_date, end_date, month_pay):
    if start_date > end_date:
        raise Exception('The end date must bigger than start date')
    curr_date = start_date
    # http://www.easybots.cn/api/holiday.php?m=201201
#     with httplib.HTTPConnection("www.easybots.cn") as conn:
    while curr_date <= end_date:
#         month_key = curr_date.year + curr_date.month
#         params = urllib.urlencode({'@m': month_key})
#         conn.request("GET", "api/holiday.php", params)
#         holiday_info = json.loads(conn.getresponse())
        leave_count = int(get_input('{0}年{1}月，请假天数(0)：'.format(curr_date.year, curr_date.month), r'^\d+$', 0))
        print '>> {0}年{1}月，请假天数: {2}'.format(curr_date.year, curr_date.month, leave_count)
        month_day_count = cal.monthrange(curr_date.year, curr_date.month)[1]
        if curr_date.year == end_date.year and curr_date.month == end_date.month:
            end_day_of_month = end_date.day
        else:
            end_day_of_month = month_day_count
        day_pay = get_day_avg_pay(curr_date.year, curr_date.month, month_pay)
        full_work_day_count = get_work_day_count(curr_date.year, curr_date.month, 1, end_day_of_month)
        work_day_count = get_work_day_count(curr_date.year, curr_date.month, curr_date.day, end_day_of_month)
        real_work_day_count = work_day_count - leave_count
        if curr_date.day == 1 and end_day_of_month == month_day_count and leave_count == 0:
            final_month_pay = month_pay
        else:
            final_month_pay = real_work_day_count * day_pay
        yield {'final_month_pay': final_month_pay,
               'month_name': curr_date.strftime("%Y-%m"),
               'start_date': curr_date.strftime(DATE_FORMAT),
               'end_date': date(curr_date.year, curr_date.month, end_day_of_month).strftime(DATE_FORMAT),
               'day_pay': day_pay,
               'full_work_day_count': full_work_day_count,
               'real_work_day_count': real_work_day_count,
               'leave_count': leave_count}
        curr_date = datetime(curr_date.year, curr_date.month, month_day_count) + timedelta(days=1)
        


if __name__ == '__main__':
    today = datetime.now()
    print '当前日期： {0}'.format(today.strftime(DATE_FORMAT))
    month_pay = int(get_input("每月工资(2800)：", r'^\d+$', 2800))
    print '>> 每月工资: {0}'.format(month_pay)
    default_start_date = date(today.year, today.month, 1).strftime(DATE_FORMAT)
    start_date = get_input('开始日期({0})：'.format(default_start_date), r'^\d{4}-\d{1,2}-\d{1,2}$', default_start_date)
    start_date = datetime.strptime(start_date, DATE_FORMAT)
    print '>> 开始日期: {0}'.format(start_date.strftime(DATE_FORMAT))
    default_end_date = date(start_date.year, start_date.month, cal.monthrange(start_date.year, start_date.month)[1]).strftime(DATE_FORMAT)
    end_date = get_input('结束日期({0})： '.format(default_end_date), r'^\d{4}-\d{1,2}-\d{1,2}$', default_end_date)
    end_date = datetime.strptime(end_date, DATE_FORMAT)
    print '>> 结束日期: {0}'.format(end_date.strftime(DATE_FORMAT))
    
    result = []
    total_pay = 0
    for pay_month in pay_month(start_date, end_date, month_pay):
        result.append('-----------------------------')
        result.append('月    份： {0}'.format(pay_month['month_name']))
        result.append('开始日期： {0}'.format(pay_month['start_date']))
        result.append('结束日期： {0}'.format(pay_month['end_date']))
        result.append('工 作 日： {0} 天'.format(pay_month['full_work_day_count']))
        result.append('休    假： {0} 天'.format(pay_month['leave_count']))
        result.append('实际工作： {0} 天 (含节日带薪假)'.format(pay_month['real_work_day_count']))
        result.append('每日工资： {0} 元'.format(round(pay_month['day_pay'], 2)))
        result.append('应付工资： {0} 元'.format(round(pay_month['final_month_pay'], 2)))
        total_pay += pay_month['final_month_pay']
    result.append('-----------------------------')
    result.append('总计： {0} 元'.format(round(total_pay, 2)))
    
    print '\r\n'.join(result)
