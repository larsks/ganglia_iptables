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

        self.logger = logging.getLogger('IptablesMonitor')

        self.running = False
        self.shuttingDown = False
        self.lock = threading.Lock()
        self.runcon = threading.Event()

        self.iptables = utils.IPTables(params.get('IptablesCommand',
            DEFAULTS['IptablesCommand']))

        self.descriptors = []
        self.metrics = {}

        # This is used internally while collecting metrics.
        self._rates = {}

        # This is what is actually exposed to Ganglia.
        self.rates = {}

        super(IptablesMonitor, self).__init__()

        self.discover_metrics()
        self.initialize()

    def initialize(self):
        '''Discover available metrics and initialize _rates with
        corresponding Rater objects.'''

        self.logger.info('Initializing rate table.')
        for d in self.descriptors:
            self.logger.debug('Initializing %(name)s.' % d)
            self._rates[d['name']] = utils.Rater(self.windowsize, d['name'])

    def shutdown (self):
        '''Shutdown the monitoring thread.'''

        self.logger.info('Shutting down.')
        self.shuttingDown = True
        self.runcon.clear()
        if not self.running:
            return
        self.join()

    def run (self):
        self.logger.info('Monitor thread starting.')
        self.running = True

        # Notify any threads waiting for us to start.
        self.runcon.set()

        while not self.shuttingDown:
            self.update_metrics()

            if not self.shuttingDown:
                time.sleep(self.refresh)

        self.running = False

    def update_metrics(self):
        '''Iterate over specified chains looking for metrics, then update
        rate table with the results.'''

        self.logger.info('Updating metrics.')
        for chain in self.chains:
            for metric in self.iptables.parse_accounting_chain(chain):
                if metric['label'] in self.metrics:
                    for t in [ 'packets', 'bytes' ]:
                        name = '%s_%s' % (metric['label'], t)

                        self.logger.debug('Updating %s = %s' %
                                (name, metric[t]))
                        self._rates[name].add(int(metric[t]))

        self.lock.acquire()
        self.logger.debug('Updating rates for Ganglia.')
        for k,v in self._rates.items():
            self.rates[k] = v.rate()
        self.lock.release()
                    
    def discover_metrics (self):
        '''Discover available metrics and build the descriptor table for
        Gmond.'''

        self.logger.info('Discovering available metrics.')
        for chain in self.chains:
            for metric in self.iptables.parse_accounting_chain(chain):
                self.logger.debug('Found metric %(label)s.' % metric)
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
        '''This is the callback defined in all metric descriptors.  Return
        a value to gmond.'''

        self.logger.debug('Servicing request for %s.' % name)

        if not self.running and not self.shuttingDown:
            self.start()

        self.lock.acquire()
        v = int(self.rates.get(name, 0))
        self.lock.release()

        return v

