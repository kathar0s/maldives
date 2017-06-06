# -*- coding: utf-8 -*-

#!/usr/bin/python

import os
import sys
import django
import threading
import time
import subprocess
import signal



class CrawlerThread(threading.Thread):
    def __init__(self, id, name, source):
        threading.Thread.__init__(self)
        self.id = id
        self.name = name
        self.source = source
        self._stop = threading.Event()

    def run(self):
        default_spider = "article_spider"
        if source.name.startswith(u'세티즌'):
            default_spider = "cetizen_article_spider"

        max_waiting = 60
        command = "scrapy crawl %s -a id=%d -a do_action=yes" % (default_spider, self.id)

        while not self.stopped():
            start_time = time.time()
            print("%s - %d start crawling\n" % (self.name, self.id))
            subprocess.call(command, shell=True)
            delta = max_waiting - (time.time() - start_time)
            if delta > 0:
                print("%s - %d waiting %d seconds\n" % (self.name, self.id, delta))
                time.sleep(delta)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


if __name__ == '__main__':
    sys.path.append(sys.argv[1])
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maldives.settings.production")
    django.setup()
    from joonggo.models import Article, ArticleItem, Source

    threads = []
    sources = Source.objects.all()
    for source in sources:
        thread1 = CrawlerThread(source.id, "thread", source)
        thread1.start()
        threads.append(thread1)

    killer = GracefulKiller()
    while True:
        time.sleep(10)
        if killer.kill_now:
            print("Trying to kill ...")
            for t in threads:
                t.stop()
            for t in threads:
                t.join()
            break

    print "Exiting Crawler main"



