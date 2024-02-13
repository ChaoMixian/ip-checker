import subprocess
import socket
import socks 

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

proxy_host = "127.0.0.1"
proxy_port = 7890

# 填写IP和端口
ip_address = ""
tcp_port = 443



# 邮件服务器的地址和端口
mail_server = ""
mail_port = 587
email_passwd = ""
# 发件人和收件人信息
sender_email = ""
recipient_email = ""
# 邮件内容
subject = "IP可用性检测"
body = ""

def check_icmp(ip_address):
    """
    使用ping命令检测给定IP地址的ICMP可用性
    """
    try:
        subprocess.check_call(['ping', '-c', '1', ip_address])
        return True
    except subprocess.CalledProcessError:
        return False


def check_tcp_proxy(ip_address, port, proxy_host=None, proxy_port=None):
    """
    使用socket库检测给定IP地址和端口的TCP可用性
    """
    try:
        if proxy_host and proxy_port:
            socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)  # 设置代理
            socket.socket = socks.socksocket  # 应用代理设置
        else:
            socks.set_default_proxy()  # 设置代理
            socket.socket = socks.socksocket  # 应用代理设置
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)  # 设置超时时间为2秒
        s.connect((ip_address, port))
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def email():
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # 添加邮件内容
    msg.attach(MIMEText(body, 'plain'))

    # 初始化SMTP客户端
    with smtplib.SMTP(mail_server, mail_port) as server:
        server.starttls()  # 启用安全传输层
        # 登录到邮箱
        server.login(sender_email, email_passwd)
        # 发送邮件
        server.send_message(msg)
        print("邮件发送成功！")

if __name__ == "__main__":
    
    body += "IP: "+ip_address+"\nPORT: "+str(tcp_port)+"\n"
    body += ("=======ICMP========\n")
    if check_icmp(ip_address):
        body+= "ICMP可用性: 可达\n"
    else:
        body+= "ICMP可用性: 不可达\n"

    body+= ("=======PROXY=======\n")
    if check_tcp_proxy(ip_address, tcp_port, proxy_host, proxy_port):
        body+= (f"TCP可用性: 可用\n")
    else:
        body+= (f"TCP可用性: 不可用\n")

    body+= ("======NOPROXY======\n")
    if check_tcp_proxy(ip_address, tcp_port):
        body+= (f"TCP可用性: 可用\n")
    else:
        body+= (f"TCP可用性: 不可用\n")
    
    print(body)
    email()
