import threading

class AccountingThread(threading.Thread):

    def __init__ (self):
        super(AccountingThread, self).__init__()
        self.running = False
        self.shuttingDown = False
        self.lock = threading.Lock()

        self.c_tally = {}
        self.l_tally = {}
        self.rates = {}

        self.discover_metrics()

    def discover_metrics():
        for chain in self.chains:
            for metric in parse_accounting_chain(chain):
                pass

    def shutdown (self):
        self.shuttingDown = True
        if not self.running:
            return
        self.join()

    def run (self):
        global chains, refreshRate, rates

        self.running = True

        while not self.shuttingDown:
            print 'top of accounting loop'
            self.c_tally = {}

            for chain in chains:
                self.parse_accounting_chain(chain)

                for k,v in self.c_tally.items():
                    if k in self.l_tally:
                        deltaP = self.c_tally[k][0] - self.l_tally[k][0]
                        deltaB = self.c_tally[k][1] - self.l_tally[k][1]
                        self.rates[k] = (deltaP/refreshRate,
                                deltaB/refreshRate)
                    else:
                        self.rates[k] = (0,0)

                    print 'rate', k, self.rates[k]

                    self.l_tally[k] = v

                lock.acquire()
                rates = {}
                for k,v in self.rates.items():
                    rates[k] = v
                lock.release()

            if not self.shuttingDown:
                time.sleep(refreshRate)


