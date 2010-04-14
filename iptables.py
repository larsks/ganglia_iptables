#!/usr/bin/python

import os
import sys
import time
import logging
import optparse

import ganglia_iptables.monitor

MONITOR = None

def metric_init(params):
    '''This is the entry point from Gmond.  Instantiates a new
    IptablesMonitor and starts the monitoring thread.'''

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
    '''Shuts down the monitoring thread.'''

    MONITOR.shutdown()

def parse_args():
    p = optparse.OptionParser()
    p.add_option('-d', '--debug', action='store_true')
    p.add_option('-o', '--option', action='append', default=[])
    p.add_option('-m', '--metrics', action='store_true')

    return p.parse_args()

def main():
    '''This is the entry point when run from the command line.  Set up a
    basic set of parameters, initialize the module, and then display values
    indefinately.'''

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

        if opts.metrics:
            for d in descriptors:
                print 'metric {\n\tname = "%(name)s"\n\tvalue_threshold = 1.0\n}' % d

            raise KeyboardInterrupt

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

