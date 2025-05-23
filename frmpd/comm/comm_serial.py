import serial
from frmpd.comm.fprotocol.controllerptoto import ControllerProto
from frmpd.comm.fprotocol.fprotocol import *
import time
import threading

class FprotocolSerial:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        self.handler = None
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
        self.serial.write(data)
        print(f"write_callback len=%d -> " % len(data), list(data))
        
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
        print(f"Serial port opened on {self.port} at {self.baudrate} baud")
        try:
            while True:
                if self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    self.handler.read_put(data)
                time.sleep(0.001)
        except KeyboardInterrupt:
            print("Serial port is closing...")
        finally:
            self.serial.close()
            
if __name__ == "__main__":
    serial_comm = FprotocolSerial()
    serial_comm.run()
