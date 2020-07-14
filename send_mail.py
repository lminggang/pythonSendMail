import os
import time
import datetime
import subprocess
from config import conf, smtp_conf
from tools.mail import EmailSender

import logging
from logging.handlers import TimedRotatingFileHandler
LOG_FILE = "log/mail.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE, when='D', interval=1)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '[%(asctime)s.%(msecs)03d %(levelname)s] %(message)s  [%(process)d]'
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)


read_file_path = smtp_conf.RECORD_SEND_MAIL

def get_today_list():
    timestamp_day = 86400
    date_list = list()
    now_timestamp = time.time() - 86400
    for i in range(30):
        today = time.strftime('%Y-%m-%d', time.localtime(now_timestamp - i * timestamp_day))
        date_list.append(today)
    date_list.sort()
    return date_list

def get_record_today_list():
    if not os.path.isfile(read_file_path):
        f = open(read_file_path, 'w')
        f.close()

    with open(read_file_path, 'r+') as file:
        rows = file.readlines()
    
    today_list = [row.split(',')[0] for row in rows]
    today_list.sort()
    return today_list[:30]

def get_send_file():
    today_list = get_today_list()
    record_today_list = get_record_today_list()
    if not record_today_list:
        return [today_list[-1]]
    
    record_max_date = record_today_list[-1]
    today_list = today_list[today_list.index(record_max_date)+1:]
    return today_list

def date_handle(date_arr):
    result = dict()
    old_date = date_arr[0]
    for date in date_arr:
        old_time_arr = time.strptime(old_date, '%Y-%m-%d')
        cur_time_arr = time.strptime(date, '%Y-%m-%d')
        old_timestamp = time.mktime(old_time_arr)
        cur_timestamp = time.mktime(cur_time_arr)
        
        result[old_date] = 1

        if cur_timestamp - old_timestamp != 0:
            diff_s = cur_timestamp - old_timestamp
            diff_d = int(diff_s / 86400)
            for i in range(diff_d):
                old_timestamp += 86400
                old_date = time.strftime('%Y-%m-%d', time.localtime(old_timestamp))
                result[old_date] = 0
                if old_date == date:
                    result[old_date] = 1
    
    return result


def create_date_html(send_status=None):
    if not send_status:
        return ''
    
    first_month = datetime.datetime.strptime(list(send_status.keys())[0], '%Y-%m-%d').strftime('%Y 年 %m 月')
    last_month = datetime.datetime.strptime(list(send_status.keys())[-1], '%Y-%m-%d').strftime('%Y 年 %m 月')
    week_list = []
    week_row = 0
    
    for send_date, status in send_status.items():
        send_date = datetime.datetime.strptime(send_date, '%Y-%m-%d')
        week_day = send_date.weekday()
        current_day = send_date.strftime('%d')
        
        if not first_month:
            first_month = send_date.strftime('%Y 年 %m 月')
        
        if week_row != len(week_list) - 1:
            week_list.append([])
            
            for k in range(0, week_day):
                week_list[week_row].append('<td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center; height: 60px; background:#e2e3e5; color: #383d41;">-</td>')
        
        if week_day + 1 != len(week_list[week_row]):
            for_cnt = week_day - len(week_list[week_row])
            for k in range(0, for_cnt):
                week_list[week_row].append('<td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center; height: 60px; background:#e2e3e5; color: #383d41;">-</td>')
        
        if status:
            week_list[week_row].append('<td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center; height: 60px; background:#d4edda; color: #155724;">' + current_day + '</td>')
        else:
            week_list[week_row].append('<td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center; height: 60px; background:#f8d7da; color: #721c24;">' + current_day + '</td>')
        
        if week_day == 6:
            week_row += 1
    
    last_day_cnt = len(week_list[-1])
    
    if last_day_cnt != 7:
        for_cnt = 7 - last_day_cnt
        last_index = len(week_list) - 1
        for i in range(0, for_cnt):
            week_list[last_index].append('<td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center; height: 60px; background:#e2e3e5; color: #383d41;">-</td>')

    if first_month != last_month:
        first_month = "{} - {}".format(first_month, last_month)
    html = '<table cellpadding="0" cellspacing="0" style="border-left:#d9d9d9 1px solid;border-top:#d9d9d9 1px solid; width: 400px;">'
    html += """
        <tr>
            <td colspan="7" style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center; height: 30px;font-size: 16px; font-weight: bold;">""" + first_month + """</td>
        </tr>
    """
    
    html += """
        <tr>
        <td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center;height: 30px;">一</td>
        <td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center;height: 30px;">二</td>
        <td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center;height: 30px;">三</td>
        <td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center;height: 30px;">四</td>
        <td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center;height: 30px;">五</td>
        <td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center;height: 30px;">六</td>
        <td style="border-bottom:#d9d9d9 1px solid; border-right: #d9d9d9 1px solid; text-align: center;height: 30px;">日</td>
    </tr>
    """
    
    for row in week_list:
        html += '<tr>'
        for col in row:
            html += col
        html += '</tr>'
    
    html += '</table>'
    return html



def send_mail(file_path, date_list):
    server_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    exitcode, output = subprocess.getstatusoutput('df -h')
    date_html = create_date_html(date_handle(date_list))

    content = f'''

        <h2>{server_time}</h2>
        <h3>磁盘空间</h3>
        <pre style='font-size:0.7rem;'>{output}</pre>
        <h3>发送记录</h3>
        {date_html}'''

    mail = EmailSender()
    mail_res = mail.send_attachment(smtp_conf.MAIL_TOS, smtp_conf.MAIL_SUBJECT, file_path, content=content)
    return mail_res

def send_mail_content(content=''):
    mail = EmailSender()
    mail_res = mail.send(smtp_conf.MAIL_TOS, smtp_conf.MAIL_SUBJECT, content)
    return mail_res

def set_record(file_path='', zip_path=''):
    if not file_path or not zip_path:
        return

    today = file_path.split('/')[-1]
    with open(read_file_path, 'a+') as file:
        file.write(f'{today},{zip_path},{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))} \n')

def main():
    record_today_list = get_record_today_list()
    send_file_list = get_send_file()
    for send_file in send_file_list:
        record_today_list.append(send_file)
        file_path = os.path.join(conf.ROOT_PATH, conf.RECODE_SEGMENT_SAVE_PATH, send_file)
        zip_path = os.path.join(conf.ROOT_PATH, conf.RECODE_SEGMENT_SAVE_PATH, f'{send_file}.zip')
        zip_status = os.system(f'zip -r {zip_path} {file_path}')
        zip_size = os.path.getsize(zip_path)

        if zip_size / 1024 / 1024 > 50:
            logging.warning(f'zip size greater than 50M. [zip_size: {zip_size / 1024 / 1024}]')
            mail_res = send_mail_content(f'{send_file} file greater than 50M. send fail!')
            os.remove(zip_path)

        if zip_status != 0:
            raise Exception(f'[Error] No such file or directory: {file_path}')

        mail_res = send_mail(zip_path, record_today_list)

        if mail_res:
            set_record(file_path=file_path, zip_path=zip_path)


if __name__ == '__main__':
    logging.info('-'*56)

    lock_file_path = conf.LOCK_FILE_PATH

    if not os.path.isfile(lock_file_path):
        f = open(lock_file_path, 'w+')
        f.close()

        try:
            main()
        except Exception as e:
            print(e)
            logging.warning(f'main error. {e}')
        finally:
            os.remove(lock_file_path)

    logging.info('-'*56)


