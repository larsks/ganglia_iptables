import utils
import threading
import time

DEFAULTS = {
        'AccountingChains'  : 'acctin,acctout',
        'RefreshRate'       : '10',
        }

class IptablesMonitor (threading.Thread):

    def __init__ (self, params):
        self.params = params
        self.chains = self.params.get('AccountingChains',
                DEFAULTS['AccountingChains']).split(',')
        self.refresh = int(self.params.get('RefreshRate',
            DEFAULTS['RefreshRate']))
        self.descriptors = []
        self.metrics = {}
        self.discover_metrics()

        self.running = False
        self.shuttingDown = False
        self.lock = threading.Lock()

        self._last = {}
        self._rates = {}
        self.rates = {}

        super(IptablesMonitor, self).__init__()

    def shutdown (self):
        self.shuttingDown = True
        if not self.running:
            return
        self.join()

    def run (self):
        self.running = True

        while not self.shuttingDown:
            self.update_metrics()

            if not self.shuttingDown:
                time.sleep(self.refresh)

        self.running = False

    def update_metrics(self):
        self._rates = {}
        for chain in self.chains:
            for metric in utils.parse_accounting_chain(chain):
                if metric['label'] in self.metrics:
                    for t in [ 'pkts', 'bytes' ]:
                        name = '%s_%s' % (metric['label'], t)

                        if name in self._last:
                            self._rates[name] = int(metric[t]) - self._last[name]
                        else:
                            self._rates[name] = 0

                        self._last[name] = int(metric[t])

        self.lock.acquire()
        for k,v in self._rates.items():
            self.rates[k] = v
        self.lock.release()
                    
    def discover_metrics (self):
        for chain in self.chains:
            for metric in utils.parse_accounting_chain(chain):
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
        if not self.running:
            self.start()

        self.lock.acquire()
        v = int(self.rates.get(name, 0))
        self.lock.release()

        return v

