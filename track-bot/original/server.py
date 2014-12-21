import socket
import logging

logging.basicConfig(level=logging.DEBUG, filename="log", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")
log = logging.getLogger(__name__)

s = socket.socket()
host = socket.gethostbyname('localhost')
port = 9000
s.bind((host, port))

s.listen(5)
log.info('Listening for connection on port ' + str(port) + ' at ' + str(host) + ' ...')
while True:
   conn, addr = s.accept()
   log.info('Got connection from %s'%str(addr))
   conn.send('Thank you for connecting')
   log.info('Sent data to %s'%str(addr))
   conn.close()