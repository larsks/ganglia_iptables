import re
import subprocess

IPTABLES = '/sbin/iptables'
RE_LABEL = re.compile('.* monitor:(?P<label>\S+) .*')

def iptables (*args):
    global IPTABLES

    p = subprocess.Popen([IPTABLES] + list(args), 
            stdout=subprocess.PIPE)
    out = p.stdout.read()
    p.wait()

    return out

def parse_accounting_chain(chain):
    for line in iptables('-vxnL', chain).split('\n'):
        if 'monitor:' in line:
            pkts, bytes, pro, opts, if_in, if_out, source, dest, xtra = \
                    line.split(None, 8)

            mo = RE_LABEL.match(xtra)
            if not mo:
                continue

            yield({
                'label':    mo.group('label'),
                'pkts':     pkts,
                'bytes':    bytes,
                'raw':      line
                })

