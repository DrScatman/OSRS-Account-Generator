#!/usr/bin/env python2
import argparse
import requests
import sys
import time
import os

RUNESCAPE_REGISTER_URL = 'https://secure.runescape.com/m=account-creation/g=oldscape/create_account'
RUNESCAPE_RECAPTCHA_KEY = '6Lcsv3oUAAAAAGFhlKrkRb029OHio098bbeyi_Hv'
CAPTCHA_URL = 'http://2captcha.com/'
CAPTCHA_REQ_URL = CAPTCHA_URL + 'in.php'
CAPTCHA_RES_URL = CAPTCHA_URL + 'res.php'
CAPTCHA_API_KEY = '4935affd16c15fb4100e8813cdccfab6'

class WaitForCaptcha():
    def __init__(self):
        self.waited_for = 0

    def sleep(self, seconds):
        self.waited_for += seconds

        for i in range(0, seconds):
            if i is seconds-1 and self.waited_for % 10 is 0:
                if self.waited_for > 30:
                    print(". (%ds)" % self.waited_for)
                else:
                    print('.')
            else:
                print('.',
            sys.stdout.flush())
            time.sleep(1)


def register_account(email, password, key):
    print('''Registering account with:
    Email: %s
    Password: %s ''' % (email, password))

    response = requests.post(RUNESCAPE_REGISTER_URL, data={
        'email1': email,
        'onlyOneEmail': 1,
        'password1': password,
        'onlyOnePassword': 1,
        'day': 12,
        'month': 12,
        'year' : 2000,
        'agree_email': 1,
        'agree_email_third_party' : 1,
        'g-recaptcha-response' : key,
        'submit': 'Play Now'
    })

    if response.status_code == requests.codes.ok:
        if 'Account Created' in response.text:
            print('Robots win again, account successfully registered\n\n')

            with open('rsaccounts.created.txt', 'a+') as f:
                f.write('%s:%s:%s\n' % (email, password, name))
                f.close()

        else:
            print(response.text)
            raise Exception('Jagex says no')
    else:
        print(response.text)
        raise Exception('Jagex says no')


def solve_captcha():
    print('Solving Captcha')
    waiting = True
    touched = False
    captcha_id = None

    response = requests.get(CAPTCHA_REQ_URL, params = {
        'key': CAPTCHA_API_KEY,
        'method': 'userrecaptcha',
        'googlekey': RUNESCAPE_RECAPTCHA_KEY,
        'pageurl': RUNESCAPE_REGISTER_URL
    })
    
    if response.status_code != requests.codes.ok:
        raise Exception('2Captcha says no')
        print(response.text)

    if '|' in response.text:
        _, captcha_id = response.text.split('|')
    else:
        raise Exception('Captcha request failed')
        print(response.text)

    wait_for_captcha = WaitForCaptcha()

    print('Waiting for captcha (ID: %s) to be solved' % captcha_id)
    while waiting:
        wait_for_captcha.sleep(15 if touched else 20)

        touched = True

        solution_response = requests.get(CAPTCHA_RES_URL, params = {
            'key': CAPTCHA_API_KEY,
            'action': 'get',
            'id': captcha_id
        })

        if solution_response.text not in ('CAPCHA_NOT_READY', 'CAPTCHA_NOT_READY'):
            print('\nCaptcha solved after %ds! (solution: %s)' % (wait_for_captcha.waited_for, solution_response.text))
            waiting = False
            _, captcha_solution = solution_response.text.split('|')
            return captcha_solution

args = ['bllitzer20000@yahoo.com', 'plmmlp']
register_account(args[0], args[1], solve_captcha())
