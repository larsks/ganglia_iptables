import sys

import utils
import threading
import time
import logging

DEFAULTS = {
        'AccountingChains'  : 'acctin,acctout',
        'RefreshRate'       : '10',
        'WindowSize'        : '6',
        'IptablesCommand'   : '/sbin/iptables',
        }

class IptablesMonitor (threading.Thread):

    def __init__ (self, params):
        self.params = params

        self.chains = self.params.get('AccountingChains',
                DEFAULTS['AccountingChains']).split(',')
        self.refresh = int(self.params.get('RefreshRate',
            DEFAULTS['RefreshRate']))
        self.windowsize = int(self.params.get('WindowSize',
            DEFAULTS['WindowSize']))
        self.debug = self.params.get('Debug', None)

        self.running = False
        self.shuttingDown = False
        self.lock = threading.Lock()
        self.runcon = threading.Event()

        self.iptables = utils.IPTables(params.get('IptablesCommand',
            DEFAULTS['IptablesCommand']))

        self._last = {}
        self.descriptors = []
        self.metrics = {}
        self._rates = {}
        self.rates = {}

        super(IptablesMonitor, self).__init__()

        self.discover_metrics()
        self.initialize()

    def initialize(self):
        for d in self.descriptors:
            self._rates[d['name']] = utils.Rater(d['name'], self.windowsize)

    def shutdown (self):
        self.shuttingDown = True
        self.runcon.clear()
        if not self.running:
            return
        self.join()

    def run (self):
        if self.debug:
            print >>sys.stderr, '+ Thread starting.'
        self.running = True
        self.runcon.set()

        while not self.shuttingDown:
            if self.debug:
                print >>sys.stderr, '+ Top of loop.'
            self.update_metrics()

            if not self.shuttingDown:
                time.sleep(self.refresh)

        self.running = False

    def update_metrics(self):
        for chain in self.chains:
            for metric in self.iptables.parse_accounting_chain(chain):
                if metric['label'] in self.metrics:
                    for t in [ 'packets', 'bytes' ]:
                        name = '%s_%s' % (metric['label'], t)

                        if self.debug:
                            print >>sys.stderr, '+ updating %s = %s' % (name,
                                    metric[t])
                        self._rates[name].add(int(metric[t]))

        self.lock.acquire()
        for k,v in self._rates.items():
            self.rates[k] = v.rate()
        self.lock.release()
                    
    def discover_metrics (self):
        for chain in self.chains:
            for metric in self.iptables.parse_accounting_chain(chain):
                self.metrics[metric['label']] = (
                        {
                            'name': '%s_packets' % metric['label'],
                            'call_back': self.metric_get,
                            'time_max': 20,
                            'value_type': 'uint',
                            'units': 'Packets',
                            'slope': 'both',
                            'format': '%u',
                            'description': 'Numbers of packets/second',
                            'groups': 'ip_accounting',
                            },
                        {
                            'name': '%s_bytes' % metric['label'],
                            'call_back': self.metric_get,
                            'time_max': 20,
                            'value_type': 'uint',
                            'units': 'Bytes',
                            'slope': 'both',
                            'format': '%u',
                            'description': 'Numbers of bytes/second',
                            'groups': 'ip_accounting',
                            })
                self.descriptors.extend(self.metrics[metric['label']])

    def metric_get(self, name):
        if not self.running and not self.shuttingDown:
            self.start()

        self.lock.acquire()
        v = int(self.rates.get(name, 0))
        self.lock.release()

        return v

