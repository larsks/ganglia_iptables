===========================
Iptables module for Ganglia
===========================

:Author: Lars Kellogg-Stedman

This is a Python module for Ganglia's gmond that extracts byte and packet
counts from selected iptables rules and publishes them as bytes/sec and
packets/sec to gmond.

Configuration
=============

This module is configured via the ``iptables.pyconf`` file, possibly
located in ``/etc/ganglia/conf.d``.  The module supports the following
parameters:

LogFile
  Send logging to the specified file instead of stderr.

LogLevel (default INFO)
  What to log.

AccountingChains (default acctin,acctout)
  A comma-separated list of iptables chains to search for marked rules.

RefreshRate (default 10)
  How often to poll iptables for new byte/packet counts.

WindowSize (default 6)
  Over how many samples to calculate rate information.

IptablesCommand (default /sbin/iptables)
  Command used to run iptables.  If you're running gmond as user
  ``nobody``, you may want to change this to "/usr/bin/sudo
  /sbin/iptables" and making the appropriate changes to your
  ``/etc/sudoers`` file.

You will need to add the necessary ``metric`` definitions to the
``collection_group`` in the configuration file.  You can generate
appropriate definitions by running ``iptables.py`` with the ``-m`` option::

  python /usr/lib/ganglia/python_modules/iptables.py -m

NB: Running ``iptables.py`` directly will not parse your config file.  You
can use the ``-o parameter=value`` command line option to provide
configuration parameters.

Marking iptables rules
======================

This module extracts packet and byte counts from rules marked with special
comments using the ``comment`` module.  The module looks for rules
containing the phrase "monitor:" followed by a metric name.  For example,
to monitor inbound http traffic::

  iptables -A acctin -p tcp --dport 80 -m comment --comment 'monitor:http_in'

This will result in the metrics ``http_in_bytes`` and ``http_in_packets``.

