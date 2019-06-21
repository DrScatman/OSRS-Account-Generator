#!/usr/bin/env python2
import argparse
import requests
import sys
import time
import os
import xml.dom.createElemen


RUNESCAPE_REGISTER_URL = 'https://secure.runescape.com/m=account-creation/g=oldscape/create_account'
RUNESCAPE_RECAPTCHA_KEY = '1abc234de56fab7c89012d34e56fa7b8'
CAPTCHA_URL = 'http://2captcha.com/'
CAPTCHA_REQ_URL = CAPTCHA_URL + 'in.php'
CAPTCHA_RES_URL = CAPTCHA_URL + 'res.php'

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


def register_account(email, password, name, age = 26):
    print('''Registering account with:
    Email: %s
    Password: %s
    Name: %s''' % (email, password, name))
    dom = Document()

    response = requests.post(RUNESCAPE_REGISTER_URL, data={
        'email1': email,
        'onlyOneEmail': 1,
        'password1': password,
        'onlyOnePassword': 1,
        'displayname': name,
        'age': age,
        'agree_email': 1,
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

    if '|' in response.text:
        _, captcha_id = response.text.split('|')
    else:
        raise Exception('Captcha request failed')

    wait_for_captcha = WaitForCaptcha()

    print('Waiting for captcha (ID: %s) to be solved' % captcha_id)
    while waiting:
        wait_for_captcha.sleep(5 if touched else 15)

        touched = True

        solution_response = requests.get(CAPTCHA_RES_URL, params = {
            'key': CAPTCHA_API_KEY,
            'id': captcha_id,
            'action': 'get'
        })

        if solution_response.text not in ('CAPCHA_NOT_READY', 'CAPTCHA_NOT_READY'):
            print('\nCaptcha solved after %ds! (solution: %s)' % (wait_for_captcha.waited_for, solution_response.text))
            waiting = False
            _, captcha_solution = solution_response.text.split('|')
            return captcha_solution


try:
    CAPTCHA_API_KEY = os.environ['CAPTCHA_API_KEY']
except KeyError:
    print('You forgot to set your 2captcha API key as the CAPTCHA_API_KEY environment variable')
    sys.exit()

if not len(sys.argv) > 1:
    print('You forgot to pass in any arguments! Run with -h/--help for more info')
    sys.exit()

parser = argparse.ArgumentParser(description='Create Runescape account(s)\n'
    'Pass new account details or path to a file with list of them',
    formatter_class=argparse.RawTextHelpFormatter)

single_acc_arg_group = parser.add_argument_group('Create a single account')

single_acc_arg_group.add_argument('-e', '--email', nargs=1,
    help='Email address to use for the new account')
single_acc_arg_group.add_argument('-p', '--password', nargs=1,
    help='Password')
single_acc_arg_group.add_argument('-n', '--name', nargs=1,
    help='Display name (ingame)')

acc_list_arg_group = parser.add_argument_group('Create accounts from a list')

acc_list_arg_group.add_argument('-l', '--list', nargs=1,
    help='''Path to file with list of new account details
        Syntax within files should match:
        email:password:name''')

args = parser.parse_args()

if args.list:
    accounts_file = open(args.list[0])
    accounts = accounts_file.readlines()
    accounts_file.close()

    for account in accounts:
        email, password, name = account.rstrip().split(':')
        register_account(email, password, name)

elif args.email and args.password and args.name:
    register_account(args.email[0], args.password[0], args.name[0])

else:
    print('Not enough arguments! Run with -h/--help for more info')
