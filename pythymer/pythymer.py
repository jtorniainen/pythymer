#!/usr/bin/env python3

# This thing controlls one thyme process and does smart things

import time
import sys
import datetime
import socket
import subprocess
import os
import configparser
import argparse
import sys


def is_weekend():
    now = datetime.datetime.now()
    return now.isoweekday() in range(6, 8)


def time_in_range(start, end):
    value = datetime.datetime.now().time()
    if start <= end:
        return start <= value <= end
    else:
        return start <= value or value <= end


def check_if_can_log(opts):  # Check if there are restrictions on place!

    if opts['start'] and opts['end'] and not time_in_range(opts['start'], opts['end']):
        return False

    if opts['skip_weekends'] and is_weekend():
        return False

    return True


def setup():
    """ Interactive setup routine for generating the conf-file. """
    opts = {}
    input('Generating configuration file for thymer. Leave selection blank to use the default settings.\n(Press ENTER to continue)')
    opts['THYME'] = input('\nInput path to the thyme executable. If thyme is defined in your path you can simply use "thyme" (default="~/workspace/bin/thyme")\n>')
    opts['DATA'] = input('\nInput path where you want to store thyme-logs (default="~/thyme_logs")\n>')
    opts['START'] = input('\nInput the time you want to start logging each day as HH:MM (default=always log)\n>')
    opts['END'] = input('\nInput the time you want to stop logging each day as HH:MM (default=always log)\n>')
    opts['INTERVAL'] = input('\nInput polling interval in seconds (default=30)\n>')
    opts['SKIP_WEEKENDS'] = input('\nInput whether to skip data loggin on weekends (default=False)\n>').lower() == 'true'


    if not opts['THYME']:
        opts['THYME'] = '~/workspace/bin/thyme'
    if not opts['DATA']:
        opts['DATA'] = '~/thyme_logs/'
    if not opts['START']:
        opts.pop('START', None)
    if not opts['END']:
        opts.pop('END', None)
    if not opts['INTERVAL']:
        opts['INTERVAL'] = 30.0
    else:
        opts['INTERVAL'] = float(opts['INTERVAL'])

    print('Writing configuration to ~/.config/pythymer.conf. If you want to change options in the future you can edit this file.')

    config = configparser.ConfigParser()
    config['SETUP'] = opts
    filename = os.path.expanduser('~') + '/.config/pythymer.conf'
    with open(filename, 'w+') as configfile:  # Check if we need to expand ~
        config.write(configfile)

    sys.exit('Thymer setup complete')


def read_configuration(config_file='~/.config/pythymer.conf'):
    """ Reads the predefined configurations. """

    config_file = config_file.replace('~', os.path.expanduser('~'))

    opts = {'thyme': '~/workspace/bin/thyme',
            'data': '~/thyme_logs/',
            'start': None,
            'end': None,
            'skip_weekends': False,
            'interval': 30.0}

    if os.path.isfile(config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        config = dict(config['SETUP'])

        if 'thyme' in config:
            opts['thyme'] = config['thyme']

        if 'data' in config:
            opts['data'] = config['data']

        if 'start' in config:
            opts['start'] = datetime.datetime.strptime(config['start'], '%H:%M').time()

        if 'end' in config:
            opts['end'] = datetime.datetime.strptime(config['end'], '%H:%M').time()

        if 'skip_weekends' in config:
            opts['skip_weekends'] = config['skip_weekends'].lower() == 'true'
    else:
        print('Warning: Can not find {}'.format(config_file))
        print('Using default parameter values.')

    opts['thyme'] = opts['thyme'].replace('~', os.path.expanduser('~'))
    opts['data'] = opts['data'].replace('~', os.path.expanduser('~'))

    return opts


def generate_filename():
    """ Generate filename for this day """
    return '{}.json'.format(str(datetime.date.today()))


def check_if_thyme_running():
    """ Checks if there is an existing thyme instance. """

    # TODO: Lock only works for linux for now
    if sys.platform == 'linux':
        global lock_socket
        lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            lock_socket.bind('\0' + 'pythymer.lock')
        except socket.error:
            sys.exit('An instance of pythymer is already running.')


def start_thymer():
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', help='Run the interactive setup', action='store_true')
    args = parser.parse_args()

    if args.setup:
        setup()

    check_if_thyme_running()
    opts = read_configuration()

    while True:
        filename = opts['data'] + generate_filename()
        if check_if_can_log(opts):
            subprocess.call([opts['thyme'], 'track', '-o', filename], shell=False)
        time.sleep(opts['interval'])


if __name__ == '__main__':
    start_thymer()
