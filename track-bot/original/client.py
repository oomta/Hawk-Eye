import socket

s = socket.socket()

s.connect((115.115.139.234, 9001))
print s.recv(1024)
s.close


####################   alternative code  ##########################

#import urllib

#print urllib.urlopen('http://localhost:9000').read()

#print urllib.urlopen('http://localhost:8080/register?%s'%urllib.urlencode({'session': ''})).read()
#print urllib.urlopen('http://track-bot.appspot.com/register').read()
