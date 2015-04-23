#!/usr/bin/python

# Michael
# Mark Sheng, i@markwhat.com
# 2015-4-23, Beijing

# maybe you should [pip install ipcalc] first of all
from ipcalc import Network
from optparse import OptionParser
import os
import threading
import commands
import time

alive_num = 0
last_alive_index = 0
lock = threading.RLock()

class PingOne(threading.Thread):
    def __init__(self,interval,timeout,count,ip,index,DEVNULL):
        threading.Thread.__init__(self)
        self.interval = interval
        self.timeout  = timeout
        self.count    = count
        self.ip       = ip
        self.index    = index
        self.DEVNULL  = DEVNULL
    def run(self):
        global alive_num
        global last_alive_index
        ping_cmd = "".join(['ping -i ', self.interval, ' -w ', self.timeout, ' -c ', self.count, " ",str(self.ip)])
        (s,o) = commands.getstatusoutput(ping_cmd)
        #print str(self.ip)
        if s == 0:
            lock.acquire()
            alive_num += 1
            last_alive_index = self.index
            lock.release()
            print "alive:"+str(self.ip)

def main():
    parser = OptionParser()
    parser.add_option("-m", "--multithread", dest="multithread", help="number of threads for concurrency, default is 10")
    parser.add_option("-t", "--target", dest="target", help="Target ip in network to scan -t 192.168.192.0.10/24")
    parser.add_option("-s", "--sleeping", dest="sleeping", help="Seconds to sleep after one cycle, default is 1")
    parser.add_option("-f", "--filename", dest="filename", help="the file to record recent counting result")
    parser.add_option("-j", "--maxjump", dest="maxjump", help="if more than MAXJUMP continuous IPv4 addresses not respond, stop")
    parser.add_option("-w", "--timeout", dest="timeout", help="Ping timeout, default: 2")
    parser.add_option("-c", "--count", dest="count", help="Stop after sending <count> requests to host, default: 1")
    parser.add_option("-i", "--interval", dest="interval", help="Wait <interval> seconds between sending packet, default: 0.2")
    (options, args) = parser.parse_args()

    if not options.target or not '/' in options.target:
        print "please specify a target: -t 192.168.0.10/24"
        print "use -h to view helping text"
        return

    interval = (options.interval if options.interval else '0.1')
    timeout = (options.timeout if options.timeout else '1')
    count = (options.count if options.count else '1')
    multithread = (int(options.multithread) if options.multithread else 10)
    sleeping = (int(options.sleeping) if options.sleeping else 1)
    target = options.target
    filename = (options.filename if options.filename else './subnet_count')
    maxjump = (int(options.maxjump) if options.maxjump else 256*256*256*256)
    
    net = Network(target)
    DEVNULL = open(os.devnull, 'w')
    
    commands.getstatusoutput("echo "+str(0)+" > "+filename)
    
    global alive_num
    global last_alive_index

    while(1):
        alive_num = 0
        last_alive_index = 0
        subnet_max = 16*1024
        index     = 0
        thread_pool = []

        need_to_ping = Network(str(net.host_first()) + '/' + target.split('/')[1])

        for ip in need_to_ping:
            index += 1
            if(index > subnet_max or index-last_alive_index > maxjump):
                break;
            t = PingOne(interval,timeout,count,ip,index,DEVNULL)
            thread_pool.append(t)
            if( index > 0 and index % multithread == 0):
                for tt in thread_pool:
                    tt.start()
                for tt in thread_pool:
                    tt.join()
                thread_pool[:] = []
        # last turn
        if thread_pool:
            for tt in thread_pool:
                tt.start()
            for tt in thread_pool:
                tt.join()
        thread_pool[:] = []
        commands.getstatusoutput("echo "+str(alive_num)+" > "+filename)
        print "find "+str(alive_num)+" alive ipv4 addresses"
        time.sleep(sleeping)

if __name__ == '__main__':
    main()
