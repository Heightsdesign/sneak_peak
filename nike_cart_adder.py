"""This file contains the the Cart Adder class and the methods required to add a product to your cart 
in the NIKE store US site"""

import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import re
import ast

class CartAdder:

    def __init__(self, url, params):

        self.url = url
        self.params = params

    def get_cookie(self):

        #gets cookie for the request builder

        session = requests.Session()
        response = session.get('http://nike.com')
        cookie = session.cookies.get_dict()#['_abck']
        return cookie

    def get_url(self):

        #asks the user to enter the URL
        #note that in order to get the right product you need to be on the exact color
        self.url = input("Enter URL")

        return self.url


    def get_skuids(self):

        headers = headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    }
        self.url = "https://www.nike.com/fr/t/chaussure-air-force-1-07-pour-QNxTcf/CW2288-111"
        page = requests.get(self.url,headers = headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        #The web page is populated with data contained in a script tag which we will look for
        #It is json data
        soupfind = soup.find('script',text = re.compile('INITIAL_REDUX_STATE')) 
        soupstring = str(soupfind) 
        textreplace = soupstring.replace('<script>window.INITIAL_REDUX_STATE=','')[0:-10] 
        data = json.loads(textreplace)

        #print(data)
        #The Sku we are searching for

        product_id = self.url[-10:]

        #In the json file, the following will give us the possible SKUs list
        skus = data['Threads']['products'][product_id]['skus']
        #And the following their availability
        available_skus = data['Threads']['products'][product_id]['availableSkus']

        #Let's use pandas to cross both tables
        df_skus = pd.DataFrame(skus)
        df_available_skus = pd.DataFrame(available_skus)

        #Here is finally the table with the available skus and their sizes
        df_skus.merge(df_available_skus[['skuId','available']], on ='skuId')

        #prints the data to a json file (data_skus.json)
        df_skus.to_json(r'data_skus.json')

        with open("data_skus.json") as json_file:
            data = json.load(json_file)
            

        return data
    
    def get_request_url(self):

        #parses the data to be used in the add to cart request
        self.request_url = self.url[20:]

        return self.request_url

    def skuid_parser(self):
        
        #parses the skuids
        self.data = self.get_skuids()

        for key, value in self.data.items():
            value = ast.literal_eval(str(value))
        
        return self.data
            
    def get_skuid_from_size(self):

        #takes the size as value and gets the corresponding skuID
        size = "8"
        index = ""
        self.parsed_data = self.skuid_parser()

        for key, value in self.parsed_data['nikeSize'].items():
            if value == size:
                index = key
        
        return self.parsed_data['skuId'].get(index)
            
                
    def request_builder(self):
    
        headers = {
    'authority': 'api.nike.com',
    'pragma': 'no-cache',
    'x-b3-traceid': 'b66a5aec-1e66-4b61-8fcb-ce8671b9dfec',
    'x-nike-visitorid': 'cee7537a-ad4b-4cc1-8de7-a5bf481677a9',
    'cache-control': 'no-cache',
    'x-b3-spanname': 'undefined',
    'dnt': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
    'content-type': 'application/json; charset=UTF-8',
    'accept': 'application/json',
    'appid': 'com.nike.commerce.nikedotcom.web',
    'x-nike-visitid': '4',
    'origin': 'https://www.nike.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.nike.com/',
    'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    #'cookie': str(self.get_cookie())
    }

        params = (
            ('modifiers', 'VALIDATELIMITS,VALIDATEAVAILABILITY'),
        )

        data = '[{"op":"add","path":"/items","value":{"itemData":{"url":%s},"skuId":%s,"quantity":1}]' % (str(self.get_request_url()), str(self.get_skuid_from_size()))

        response = requests.patch('https://api.nike.com/buy/carts/v2/US/NIKE/NIKECOM', headers=headers, params=params, data=data)

        return response

testCA = CartAdder('url', 'params')

testCA.request_builder()
#testCA.get_skuids()
#print(testCA.get_request_url())
#print(testCA.get_skuid_from_size())