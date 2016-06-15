#!/usr/bin/env python
from dns.resolver import query


class MonitorDomain(object):
    def __init__(self, url):
        self.url = url

    def check_domain(self):
        query(self.url)
        return True


def main():
    from dns.resolver import NXDOMAIN
    try:
        domain = 'mypebble.co.uk'
        query(domain)
        print("{url}")
    except NXDOMAIN:
        print "hey ho, I got me an errorrrzzzz"


if __name__ == '__main__':
    main()
