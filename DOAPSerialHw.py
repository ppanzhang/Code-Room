import serial
import serial.tools.list_ports
import SlipProtocol
import binascii


def detect_available_serial_port():
    port_list = list(serial.tools.list_ports.comports())
    serial_port_name_list=[]
    for serial_port_item in port_list:
        serial_port_item_list=list(serial_port_item)
        serial_port_name=str(serial_port_item_list[0])
        serial_port_name_list.append(serial_port_name)
    return serial_port_name_list


def check_serial_port_config(port_str, baudrate_str, parity_str, databits_str, stopbits_str):
    serial_port_cfg_list = []
    if(port_str!=""):
        serial_port_cfg_list.append(port_str)

    if(baudrate_str == "9600"):
        serial_port_cfg_list.append(9600)
    elif(baudrate_str == "19200"):
        serial_port_cfg_list.append(19200)
    else:
        pass

    if(parity_str == "None"):
        serial_port_cfg_list.append(serial.PARITY_NONE)
    elif(parity_str == "Odd"):
        serial_port_cfg_list.append(serial.PARITY_ODD)
    elif(parity_str == "Even"):
        serial_port_cfg_list.append(serial.PARITY_EVEN)
    else:
        pass

    if(databits_str == "7"):
        serial_port_cfg_list.append(serial.SEVENBITS)
    elif(databits_str == "8"):
        serial_port_cfg_list.append(serial.EIGHTBITS)
    else:
        pass
    
    if(stopbits_str == "1"):
        serial_port_cfg_list.append(serial.STOPBITS_ONE)
    elif(stopbits_str == "2"):
        serial_port_cfg_list.append(serial.STOPBITS_TWO)
    else:
        pass

    if(len(serial_port_cfg_list)<5):
        serial_port_cfg_list=[]
    return serial_port_cfg_list


def serial_port_connect(serial_port_cfg_list):
    ser=serial.Serial(serial_port_cfg_list[0], baudrate=serial_port_cfg_list[1],parity=serial_port_cfg_list[2],stopbits=serial_port_cfg_list[4], bytesize=serial_port_cfg_list[3],timeout=0.5)
    ser.close()
    ser.open()
    return ser


def serial_port_disconnect(ser):
    ser.close()
    return


def check_serial_port_connected(ser):
    if ser.isOpen():
        return True
    else:
        return False


def serial_port_write(ser, frame):
    frame_bytes=bytearray(frame)
    ser.write(frame_bytes)
    return


def serial_port_read(ser, length):
    frame_bytes = ser.read(length)
    frame = list(frame_bytes)
    dest_list=[]
    for item in frame:
    #    item_int=Hex_str_to_int(item)
        dest_list.append(item)
    return dest_list


def Hex_str_to_int(hex_str):
    data=0
    for i in hex_str:
        val = ord(i)
        data = data*256 + val
    return data


# if __name__ == '__main__':
    # cfg = check_serial_port_config("COM20","19200","None","8","1")
    # ser=serial_port_connect(cfg)
    # wr_str=DOAPFrame.Build_DOAP_Request_Frame(0,0,0,[])
    # wr_str=SlipProtocol.Encode_SlipProtocol(wr_str)
    # # #bytearray([1,2,3])
    # # print(bytearray([1,2,3]))
    # #ser.write(bytearray(wr_str))
    # serial_port_write(ser, wr_str)
    # #response_frame_bytes = ser.read(80)
    # res_list=serial_port_read(ser, 80)
    # print(res_list)
    # for item in response_frame_bytes:
    #     item_ch=str(item)
    #     data=item_ch.encode('hex')
    #     #data_dc=int(data)
    #     print(type(data))


# list1=[12,2,3,4]
# str = DUMP_HEX(list1)
# print(str)
# a = 0x665554
# b = hex(a)
# b = b[2:]
# c = binascii.a2b_hex(b)


