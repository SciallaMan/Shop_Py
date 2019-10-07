import json
import copy

from bs4 import BeautifulSoup
import requests
import re
import smtplib
from email.mime.multipart import MIMEMultipart


class Data:
    def __init__(self, config, credentials):
        self.gmail_user = credentials.get("gmail_user")
        self.gmail_password = credentials.get("gmail_password")
        self.send_to = credentials.get("send_to")
        self.sent_from = credentials.get("gmail_user")

        self.msg = config.get("mailSubject")
        self.product = config.get("product")

        self.shops = copy.deepcopy(config.get("shops"))

    def updateMsg(self, msg):
        self.msg += msg


def search(webSites):
    for webSite in webSites:
        print(f"Searching on {webSite}")
        url = getUrl(webSite, data.product)
        r = requests.get(url)
        if url != "Invalid website":
            data.updateMsg('\n' + webSite.upper() + ' :\n')
            shop = data.shops.get(webSite)
            soup = BeautifulSoup(r.text, "html.parser")
            prices = soup.select(shop.get('selectorPrice'))
            titles = soup.select(shop.get('selectorTitle'))
            count = shop.get("count") if shop.get("count") < len(prices) else len(prices)
            for i in range(count):
                # print('\n' + titles[i].text.strip() + ': ')
                # print(prices[i].text.strip())
                if titles[i].text.strip() and prices[i].text.strip() :
                    data.updateMsg('\n\n' + titles[i].text.strip() + ':\n' + prices[i].text.strip() + ' euro')
                    print(f"Found on {webSite}")
                else :
                    data.updateMsg(f"\nNot found on {webSite} \n")
                    print(f"Not found on {webSite}")

        else: print("Invalid website")
    sendMail()


def getUrl(webSite, product):
    switcherUrl = {
        "Mediaworld": data.shops.get(webSite).get('url') + product.replace(" ", "%20"),
        "Amazon": data.shops.get(webSite).get('url') + product.replace(" ", "+")
    }
    return switcherUrl.get(webSite, "Invalid website")


def sendMail():
    try:
        # print(data.msg)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(data.gmail_user, data.gmail_password)
        server.sendmail(data.sent_from, data.send_to, data.msg)
        server.close()

        print("Email sent!\n")
    except:
        print("Something went wrong...")


with open('config.json') as config_json:
    config = json.load(config_json)

try:
    with open('credentials.json') as credentials_json:
        credentials = json.load(credentials_json)
    data = Data(config, credentials)
    search(config["activeShops"])
except:
    print("File credentials not found")
