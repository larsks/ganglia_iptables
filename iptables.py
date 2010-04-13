#!/usr/bin/python

import os
import sys
import time

import ganglia_iptables.monitor

MONITOR = None

def metric_init(params):
    global MONITOR
    MONITOR = ganglia_iptables.monitor.IptablesMonitor(params)
    MONITOR.start()
    return MONITOR.descriptors

def metric_cleanup():
    MONITOR.shutdown()

def main():
    try:
        descriptors = metric_init({})
        while True:
            for d in descriptors:
                v = d['call_back'](d['name'])
                print 'value for %s is %u' % (d['name'],  v)
            time.sleep(5)
    except KeyboardInterrupt:
        metric_cleanup()

if __name__ == '__main__':
    main()

