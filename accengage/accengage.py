#! Python3

import hashlib
import pandas as pd
import time
import requests
import json

try:
    from StringIO import StringIO as BufferIO
except ImportError:
    from io import BytesIO as BufferIO


class Accengage:
    def __init__(self, email, api_key):
        """

        :param email: email for the associated api_key
        :param api_key: generated in the accengage administration menu
        """
        self.emaiil = email
        self.api_key = api_key
        self.first_payload = json.dumps({'email': self.emaiil})
        self.login_reponse = self.login()
        print(self.login_reponse)
        self.access_token = self.login_reponse['access_token']
        self.token_type = self.login_reponse['token_type']

    def set_time_signature(self, payload=None):
        if payload is not None and isinstance(payload, dict):
            payload = json.dumps(payload)
        self.accengage_time = str(int(time.time()))
        self.payload = self.first_payload if payload is None else payload
        if self.payload == '{}':
            self.payload = ''
        self.accengage_signature = hashlib.sha1((self.payload + self.api_key + self.accengage_time).encode('utf-8')).hexdigest()

    def login(self):
        self.set_time_signature()

        url = "http://api.accengage.com/v1/access_token"

        headers = {
            'content-type': "application/json",
            'accengage-signature': self.accengage_signature,
            'accengage-time': self.accengage_time,
            'cache-control': "no-cache",
        }
        response = requests.request("POST", url, data=self.first_payload, headers=headers)
        return response.json()

    def get_users(self, partner_id, last_open=None):

        url = "http://api.accengage.com/v1/me/apps/{partner_id}/devices".format(partner_id=partner_id)

        if last_open is not None:
            # last_open should be in format "%Y-%m-%d"
            querystring = {"lastOpen": last_open}
        else:
            querystring = {}
        self.set_time_signature(payload={})
        headers = {
            'content-type': "application/json",
            'accengage-signature': self.accengage_signature,
            'accengage-time': self.accengage_time,
            'authorization': "{} {}".format(self.token_type, self.access_token),
            'cache-control': "no-cache",
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

        return response.text, response.headers

    def make_generic_request(self, api_url, method='GET', payload=None, querystring=None):

        if querystring is None:
            querystring = {}

        if payload is None:
            payload = json.dumps({})

        if method == "GET":
            response = requests.request(method, api_url, headers=self.set_headers(), params=querystring)
        if method == "POST" or method == "PUT" or method == "DELETE":
            response = requests.request(method, api_url, data=payload, headers=self.set_headers(), params=querystring)
        return response.text, response.headers

    def set_headers(self):
        self.set_time_signature(payload=self.payload)
        self.headers = {
            'content-type': "application/json",
            'accengage-signature': self.accengage_signature,
            'accengage-time': self.accengage_time,
            'authorization': "{} {}".format(self.token_type, self.access_token),
            'cache-control': "no-cache",
        }
        return self.headers

    def get_output_in_list(self, result, headers):
        """

        :param result: response.text from api call
        :param headers: response.headers from api call useful if request is paginated (Link key in headers)
        :return: pd.DataFrame
        """
        data = BufferIO(result.encode())
        if len(result) == 0:
            return []
        data_list = pd.read_csv(data, sep=";", header=0, encoding='utf-8', error_bad_lines=False).to_dict('records')
        if headers.get('Link'):
            response = requests.request("GET", headers['Link'].replace('<', '').replace('>; rel="next"', ''), headers=self.set_headers(), params={})
            data_list += self.get_output_in_list(response.text, response.headers)
        else:
            pass
        return data_list

    def get_users_df(self, partner_id, last_open=None):
        return pd.DataFrame(self.get_output_in_list(*self.get_users(partner_id=partner_id, last_open=last_open)))
