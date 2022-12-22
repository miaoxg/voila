#!/usr/local/bin/python3.9
import logging
import os
import threading
import time

logging.basicConfig(level=logging.INFO,
                    filename='main.log',
                    format="%(asctime)s %(filename)s %(funcName)s：line %(lineno)d threadid %(thread)d %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )

seconds = 1 * 60 * 60 * 24 * 365


def Voila_BIO_AD_Collection():
    os.system("/usr/bin/python3.10 /app/Voila_BIO_AD_Collection.py")


def Voila_BIO_AD_Product():
    os.system("/usr/bin/python3.10 /app/Voila_BIO_AD_Product.py")


def Voila_BIO_Login():
    os.system("/usr/bin/python3.10 /app/Voila_BIO_Login.py")


def Voila_BIO_ProductSearch():
    os.system("/usr/bin/python3.10 /app/Voila_BIO_ProductSearch.py")


def Voila_BIO_SearchRetailer():
    os.system("/usr/bin/python3.10 /app/Voila_BIO_SearchRetailer.py")


def Voila_BloggerData():
    os.system("/usr/bin/python3.10 /app/Voila_BloggerData.py")


def usebouncer_check():
    os.system("/usr/bin/python3.10 /app/usebouncer_check.py")


def Voila_Search_ProductBrands():
    os.system("/usr/bin/python3.10 /app/Voila_Search_ProductBrands.py")


def Voila_Search_ProductRetailers():
    os.system("/usr/bin/python3.10 /app/Voila_Search_ProductRetailers.py")


def Voila_BIO_ProductRecommend():
    os.system("/usr/bin/python3.10 /app/Voila_BIO_ProductRecommend.py")


if __name__ == "__main__":
    while True:
        try:
            p1 = threading.Thread(target=Voila_BIO_AD_Collection)
            p2 = threading.Thread(target=Voila_BIO_AD_Product)
            p3 = threading.Thread(target=Voila_BIO_Login)
            p4 = threading.Thread(target=Voila_BIO_ProductSearch)
            p5 = threading.Thread(target=Voila_BIO_SearchRetailer)
            #        p6 = threading.Thread(target=Voila_BloggerData)
            p7 = threading.Thread(target=usebouncer_check)
            p8 = threading.Thread(target=Voila_Search_ProductBrands)
            p9 = threading.Thread(target=Voila_Search_ProductRetailers)
            p10 = threading.Thread(target=Voila_BIO_ProductRecommend)

            p1.start()
            p2.start()
            p3.start()
            p4.start()
            p5.start()
            #        p6.start()
            p7.start()
            p8.start()
            p9.start()
            p10.start()

            time.sleep(1 * 60 * 60 * 24 * 365)
        except Exception as e:
            logging.info(e)
