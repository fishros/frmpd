import socket
from frmpd.comm.fprotocol.controllerptoto import ControllerProto
from frmpd.comm.fprotocol.fprotocol import *
import time
import threading

class FprotocolUDPServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.handler = None
        self.addr = None
        self.last_call_time = time.time()
        self.call_count = 0
        
        self._init_protocol()
        
    def _init_protocol(self):
        self.handler = FProtocol(self.read_callback, self.write_callback)
        self.proto = ControllerProto()
        self.proto.read_can.callback = self.can_read_callback
        self.proto.read_485.callback = self.rs485_read_callback
        self.handler.add_slave_node(0x0001, self.proto)
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        
    def read_callback(self):
        return None
        
    def write_callback(self, data):
        # print(f"write_callback {self.addr} len=%d -> " % len(data), list(data))
        self.sock.sendto(data, self.addr)
        
    def can_read_callback(self, type, from_node, error_code):
        self.call_count += 1
        elapsed_time = time.time() - self.last_call_time
        if elapsed_time > 1:
            frequency = self.call_count
            self.call_count = 0
            print(f"Callback frequency: {frequency:.2f} calls per second")
            self.last_call_time = time.time()
            
    def rs485_read_callback(self, type, from_node, error_code):
        self.call_count += 1
        elapsed_time = time.time() - self.last_call_time
        if elapsed_time > 1:
            frequency = self.call_count
            self.call_count = 0
            print(f"Callback RS485 frequency: {frequency:.2f} calls per second")
            self.last_call_time = time.time()
            
    def run(self):
        print(f"UDP server listening on {self.host}:{self.port}")
        try:
            while True:
                data, self.addr = self.sock.recvfrom(4096)
                self.handler.read_put(data)
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("Server is shutting down...")
        finally:
            self.sock.close()
            
if __name__ == "__main__":
    server = FprotocolUDPServer()
    server.run()
