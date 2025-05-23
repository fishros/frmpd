import sys
from frmpd.server import app,socketio
from frmpd.comm.comm_serial import FprotocolSerial
from frmpd.comm.comm_udp import FprotocolUDPServer,FProtocolType

from frmpd.server import socketio
from flask_socketio import emit


comm = None

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('write_io')
def handle_write_io(data):
    global comm
    comm.proto.write_io._data_size = int(len(data.get('data'))/2)
    comm.proto.write_io._index_size = int(len(data.get('index'))/2)
    comm.proto.write_io.data = bytes.fromhex(data.get('data'))
    comm.proto.write_io.index = bytes.fromhex(data.get('index'))
    comm.proto.write_write_io(comm.handler,FProtocolType.TRANSPORT_DATA, 0x0001)
   

@socketio.on('config_rs485_rate')
def handle_config_rs485_rate(data):
    global comm
    print(f"Received config_rs485_rate: {data}")
    comm.proto.config_rs485_rate = data.get('rate')
    print(f"Configuring RS485 rate: {comm.proto.config_rs485_rate}")
    comm.proto.write_config_rs485_rate(comm.handler,FProtocolType.TRANSPORT_DATA, 0x0001)
   
@socketio.on('write_can')
def handle_write_can(data):
    global comm
    print(f"Received write_can: {data}")
    # Parse CAN ID and convert to int
    can_id = int(data.get('canid'), 16)
    # Convert hex string data to bytes
    raw_data = bytes.fromhex(data.get('data'))
    if len(raw_data)>8:
        raw_data = raw_data[:8]
    # Set the CAN message properties
    comm.proto.write_can._data_size = len(raw_data)
    comm.proto.write_can.data = raw_data
    comm.proto.write_can.id = can_id
    comm.proto.write_can.dlc = comm.proto.write_can._data_size 
    comm.proto.write_can.type = 1 if data.get('type') == 'std' else 2
    # Send the CAN message
    comm.proto.write_write_can(comm.handler, FProtocolType.TRANSPORT_DATA, 0x0001)

@socketio.on('config_can_rate')
def handle_config_can_rate(data):
    global comm
    print(f"Received config_can_rate: {data}")
    comm.proto.config_can_rate = data.get('rate')
    print(f"Configuring CAN rate: {comm.proto.config_can_rate}")
    comm.proto.write_config_can_rate(comm.handler, FProtocolType.TRANSPORT_DATA, 0x0001)


@socketio.on('write_485')
def handle_ping(data):
    global comm
    print(f"Received write_485: {data}")
    emit('write_485', {'msg': f"{data}"})
    mode = data.get('mode')
    send_data = data.get('data')  
    raw_send_data = None
    if mode == "text":  
        raw_send_data = bytes(send_data, 'utf-8')
    elif mode == "hex":
        raw_send_data = bytes.fromhex(send_data)
    if raw_send_data:
        comm.proto.write_485.data = raw_send_data
        comm.proto.write_485._data_size = len(raw_send_data)
        comm.proto.write_write_485(comm.handler,FProtocolType.TRANSPORT_DATA, 0x0001)

def callback_read_io(type, data, code):
    socketio.emit('read_io', data.to_json())  # Emit to all connected clients

def callback_read_485(type, data, code):
    socketio.emit('read_485', data.to_json())  # Emit to all connected clients
    
def callback_read_can(type, data, code):
    socketio.emit('read_can', data.to_json())  # Emit to all connected clients
    

def main():
    global comm
    print(sys.argv)
    if len(sys.argv) < 2:
        print("Usage: frmpd [serial <port> <baudrate>] | [udp4 <port>]")
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "serial" and len(sys.argv) >= 3:
        port = sys.argv[2]
        if len(sys.argv) >= 4:
            baudrate = int(sys.argv[3])
        else:
            baudrate = 921600
        comm = FprotocolSerial(port=port,baudrate=baudrate)
    elif mode == "udp4" and len(sys.argv) >= 3:
        port = int(sys.argv[2])
        comm = FprotocolUDPServer(port=port)
    else:
        print("Invalid usage. Example: frmpd serial /dev/ttyUSB0 921600  or frmpd udp4 5000")
        sys.exit(1)

    comm.proto.read_io.callback = callback_read_io
    comm.proto.read_485.callback = callback_read_485
    comm.proto.read_can.callback = callback_read_can
    
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)


if __name__=="__main__":
    main()


