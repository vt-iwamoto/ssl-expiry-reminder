import json
import datetime
import pytz
import os
import socket
import ssl
import requests
import sys

jst = pytz.timezone('Asia/Tokyo')

# 1. 実行ハンドラー：Lambdaはここから開始
def lambda_handler(event, context):
    domains = [x.strip() for x in str(os.getenv('Urls')).split(',')]
    webhook = os.getenv('IncommingWebhooks')
    try:
        # SSL期限チェック
        ssl_expires = {}
        for domain in domains:
            is_ssl_expires, ssl_expires_date = ssl_expires_in(domain)
            if is_ssl_expires:
                ssl_expires[domain] = ssl_expires_date
        print(len(ssl_expires))
        if len(ssl_expires) != 0:
            text = f"以下のSSL証明書が{os.getenv('BufferDays')}日以内に期限切れになります"
            for domain, expired_date in ssl_expires.items():
                text += f"\n{domain} - 有効期限 : {expired_date}"
            send_slack(text)
    except requests.RequestException as e:
        print(e)
        raise e
    except:
        print(sys.exc_info())
        text = "SSLチェック中にエラーが発生しました。"
        send_slack(text)
        raise


# 残日数の取得
def ssl_valid_time_remaining(hostname):
    expires = ssl_expiry_datetime(hostname)
    return expires - datetime.datetime.now(jst), expires

# SSLチェック関数
def ssl_expires_in(hostname):
    buffer_days=int(os.getenv('BufferDays'))
    try:
        remaining, expires = ssl_valid_time_remaining(hostname)
        return valid_date(remaining, expires, buffer_days)
    except:
        return True, "SSLチェックに失敗しました"

# 有効期限をジャッジする関数
def valid_date(remaining, expires, buffer_days):
    if remaining < datetime.timedelta(days=0):
        return True, "有効期限切れ、手遅れです"
    elif remaining < datetime.timedelta(days=buffer_days):
        return True, expires.strftime("%Y/%m/%d")
    else:
        return False, ""

# 有効期限の取り出し
def ssl_expiry_datetime(hostname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    utc_datetime = datetime.datetime.strptime(
        ssl_expiry(hostname), ssl_date_fmt)
    return utc_datetime.astimezone(jst)

# 有効期限の取得
def ssl_expiry(hostname):
    print("{}の接続を開始します。".format(hostname))
    context = ssl.create_default_context()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.settimeout(3.0)
            ssock.connect((hostname, 443))
            ssl_info = ssock.getpeercert()
            ssock.close()
            print(ssl_info)
            return ssl_info['notAfter']  # ssl_info['notAfter'] が証明書の期限

# Slack通知
def send_slack(text):
    webhook = os.getenv('IncommingWebhooks')
    print('slack通知')
    requests.post(webhook, data=json.dumps({
        # 通知内容
        'text': text
    }))
