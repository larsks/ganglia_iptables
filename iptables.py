#!/usr/bin/python

import os
import sys
import time
import logging

import ganglia_iptables.monitor

MONITOR = None

def metric_init(params):
    global MONITOR

    logging.basicConfig(
            filename=params.get('Logfile'),
            format='%(asctime)s %(name)s %(levelname)s: %(message)s',
            level=logging.INFO)

    MONITOR = ganglia_iptables.monitor.IptablesMonitor(params)
    MONITOR.start()
    MONITOR.runcon.wait()

    return MONITOR.descriptors

def metric_cleanup():
    MONITOR.shutdown()

def main():
    try:
        descriptors = metric_init({
            'IptablesCommand': '/usr/bin/sudo /sbin/iptables',
            })
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

