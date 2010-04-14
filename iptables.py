#!/usr/bin/python

import os
import sys
import time
import logging
import optparse

import ganglia_iptables.monitor

MONITOR = None

def metric_init(params):
    global MONITOR

    logging.basicConfig(
            filename=params.get('LogFile'),
            format='%(asctime)s %(name)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=getattr(logging, params.get('LogLevel', 'INFO').upper()))

    MONITOR = ganglia_iptables.monitor.IptablesMonitor(params)
    MONITOR.start()
    MONITOR.runcon.wait()

    return MONITOR.descriptors

def metric_cleanup():
    MONITOR.shutdown()

def parse_args():
    p = optparse.OptionParser()
    p.add_option('-d', '--debug', action='store_true')
    p.add_option('-o', '--option', action='append', default=[])

    return p.parse_args()

def main():
    opts, args = parse_args()

    options = {
            'IptablesCommand': '/usr/bin/sudo /sbin/iptables',
            }

    if opts.debug:
        options['LogLevel'] = 'DEBUG'

    for k,v in [x.split('=') for x in opts.option]:
        options[k] = v

    try:
        descriptors = metric_init(options)
        while True:
            for d in descriptors:
                v = d['call_back'](d['name'])
                print 'value for %s is %u' % (d['name'],  v)

            print '-' * 70

            time.sleep(5)
    except KeyboardInterrupt:
        metric_cleanup()

if __name__ == '__main__':
    main()

