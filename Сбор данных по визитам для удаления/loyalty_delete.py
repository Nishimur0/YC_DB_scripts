import requests
import time
import datetime
import json

def datetime_parser(DT: str):
    """ datetime in iso8601 format parser """
    a, b = DT.split('+')
    dt = datetime.datetime.strptime(a, "%Y-%m-%dT%H:%M:%S")
    return dt

class YClientsAPI:

    def __init__(self, token, company_id, language='en-US'):
        self.company_id = company_id
        self.headers = {
            "Accept": "application/vnd.yclients.v2+json",
            'Accept-Language': language,
            'Authorization': f"Bearer {token}",
            'Cache-Control': "no-cache"
        }
        # if __show_debugging==True code will show debugging process
        self.__show_debugging = False


    def get_user_token(self, login, password):
        url = "https://api.yclients.com/api/v1/auth"
        querystring = {
            "login": login,
            "password": password
        }
        response = requests.request("POST", url, headers=self.headers, params=querystring)
        user_token = json.loads(response.text)['data']['user_token']
        if (self.__show_debugging):
            print(f"Obtained user token {user_token}")
        return user_token

    def update_user_token(self, user_token):
        self.headers['Authorization'] = \
            self.headers['Authorization'] + f", User {user_token}"
        if (self.__show_debugging):
            print(f"Updated autorisation parameters:"
                  f" {self.headers['Authorization']}")


delete_loyalty = YClientsAPI('rj257pguzmdk9fgaz8cr', 245723)
user_token = delete_loyalty.get_user_token('79997958516', 'WoodPecker1431')
delete_loyalty.update_user_token(user_token)
