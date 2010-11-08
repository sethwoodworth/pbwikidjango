import urllib
import socket

timeout = 150
socket.setdefaulttimeout(timeout)


file = open("wiki-list.txt", "r")
for line in file:
    line = line[7:]
    subdomain = line.split('.')[0]
    new_dir = 'http://wiki-tools.webecology.net/code/wiki/' + subdomain
    print "prefetching " + new_dir
    a = urllib.urlopen(new_dir)
    a.close()
    print "    done"
