# -*- coding: utf-8 -*-

#!/usr/bin/python

import os
import sys
import django
import threading
import time
import subprocess
import signal



class CheckerThread(threading.Thread):
    def __init__(self, id, name, source):
        threading.Thread.__init__(self)
        self.id = id
        self.name = name
        self.source = source
        self._stop = threading.Event()

    def run(self):
        default_spider = "naver_standalone_checker"
        if source.name.startswith(u'세티즌'):
            default_spider = "cetizen_standalone_checker"

        command = "scrapy crawl %s -a id=%d" % (default_spider, self.id)
        subprocess.call(command, shell=True)


if __name__ == '__main__':
    sys.path.append(sys.argv[1])
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maldives.settings.production")
    django.setup()
    from joonggo.models import Source

    threads = []
    sources = Source.objects.all()
    for source in sources:
        thread1 = CheckerThread(source.id, "thread", source)
        thread1.start()
        threads.append(thread1)

    for t in threads:
        t.join()

    print "Exiting checker main"


