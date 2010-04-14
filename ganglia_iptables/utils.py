import sys
import re
import subprocess
import time
import logging

IPTABLES = '/sbin/iptables'
RE_LABEL = re.compile('.* monitor:(?P<label>\S+) .*')

class Rater (object):
    '''Calculates rate over a given number of samples.'''

    def __init__ (self, numsamples, name=None):
        '''name is optional and is only meant for debugging purposes.'''

        self.name = name
        self.numsamples = numsamples
        self.samples = []
        self.total = 0
        self.logger = logging.getLogger('Rater')

    def add (self, v):
        if len(self.samples) == self.numsamples:
            self.samples.pop(0)

        self.samples.append((v, time.time()))

    def rate (self):
        try:
            r = (self.samples[-1][0]-self.samples[0][0])/(self.samples[-1][1] - self.samples[0][1])
        except (IndexError, ZeroDivisionError):
            r = 0
        self.logger.debug('%s: %s | %s' % (self.name,
            ' '.join([str(x[0]) for x in self.samples]), r))

        return r

class IPTables (object):
    '''A class for interacting with the iptables command.'''

    def __init__ (self, iptables):
        self.iptables = iptables
        if self.iptables is None:
            self.iptables = IPTABLES

    def call (self, *args):
        p = subprocess.Popen(self.iptables.split() + list(args), 
                stdout=subprocess.PIPE)
        out = p.stdout.read()
        p.wait()

        return out

    def parse_accounting_chain(self, chain):
        for line in self.call('-vxnL', chain).split('\n'):
            if 'monitor:' in line:
                pkts, bytes, pro, opts, if_in, if_out, source, dest, xtra = \
                        line.split(None, 8)

                mo = RE_LABEL.match(xtra)
                if not mo:
                    continue

                yield({
                    'label'     : mo.group('label'),
                    'packets'   : pkts,
                    'bytes'     : bytes,
                    'protocol'  : pro,
                    'if_in'     : if_in,
                    'if_out'    : if_out,
                    'source'    : source,
                    'dest'      : dest,
                    'xtra'      : xtra,
                    'raw'       : line
                    })

