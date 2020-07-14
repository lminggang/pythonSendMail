import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import logging
from config import smtp_conf


class EmailSender(object):
    def __init__(self):
        self.host = smtp_conf.HOST
        self.port = smtp_conf.PORT
        self.password = smtp_conf.PASSWORD

        self.email = smtp_conf.EMAIL
        self.connect()

    def connect(self):
        self.server = smtplib.SMTP_SSL(self.host, self.port, timeout=smtp_conf.TIMEOUT)
        self.server.login(self.email, self.password)
    
    def get_receivers(self, tos):
        to_str = ""
        to_array = []
        if type(tos) in [list, tuple]:
            to_str = ",".join(tos) 
            to_array = tos
        else:
            to_str = tos
            to_array = [tos]
        
        return to_str, to_array

    def send(self, tos, subject, content=''):
        to_str, to_array = self.get_receivers(tos)

        msg = MIMEText(content,'html','utf-8')
        msg['From'] = self.email 
        msg['To'] = to_str
        msg['Subject'] = subject
        start_time = time.time()
        self.server.sendmail(self.email, to_array, msg.as_string())
        run_time = time.time() - start_time
        logging.info(f'send mail success. - [run: {run_time}, tos: {tos}, content: {content}]')

    def send_attachment(self, tos, subject, file_path, content='', index=1):
        try:
            to_str, to_array = self.get_receivers(tos)
            file_name = file_path.split('/')[-1]
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] =  to_str
            msg['Subject'] = subject
            # add mail content
            msg.attach(MIMEText(content, 'html', 'utf-8'))
            
            # add mail attachment
            att = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = f'attachment; filename="{file_name}"'
            msg.attach(att)

            start_time = time.time()
            res = self.server.sendmail(self.email, to_array, msg.as_string())
            run_time = time.time() - start_time
            logging.info(f'send_attachment mail success. - [run: {run_time}, tos: {tos}, file_path: {file_path}]')
            return True
        except Exception as e:
            if index > 5:
                return False
            logging.warning(f'send_attachment mail error. [index: {index}, date: {file_path.split("/")[-1].split(".")[0]}] {e}')
            self.connect()
            return self.send_attachment(tos, subject, file_path, content='', index=index+1)
            



if __name__ == "__main__":
    mail = EmailSender()
    html = """
        <style type="text/css">
            table.gridtable {
                font-family: verdana,arial,sans-serif;
                font-size:11px;
                border:1px solid #666666;
                border-collapse: collapse;
            }
            table.gridtable th {
              border: 1px solid #666666;
              padding:8px;
            }
            table.gridtable td {
              border: 1px solid #666666;
              padding:8px;
            }
            </style>

            <table class="gridtable">
              <tr>
                <th>Month</th>
                <th>Savings</th>
              </tr>
              <tr>
                <td>January</td>
                <td>$100</td>
              </tr>
              <tr>
                <td>February</td>
                <td>$80</td>
              </tr>
            </table>
    """
    # send content
    # mail.send(['18710002395@163.com'], '测试邮件主题', html)

    # send content and attachment
    file_path = '/home/parallels/works_mic/dbs-mic/save_audio/20191219_081013_20191219_082513_20191226144457.wav'
    res = mail.send_attachment(['18710002395@163.com'], '测试邮件主题', file_path, html)
    print(res)
