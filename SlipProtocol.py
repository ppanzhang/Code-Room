import CRC16CCITT

SLIP_FRAME_START_CB = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
SLIP_FRAME_END = 0xC0
SLIP_ESC = 0xDB
SLIP_CUSTOM = 0x5A
SLIP_ESC_START = 0xDE
SLIP_ESC_END = 0xDC
SLIP_ESC_ESC = 0xDD
SLIP_ESC_CUSTOM = 0xDA

SLIP_SMALLEST_ENCODE = 2

s_esc =SLIP_ESC
s_escEsc = [SLIP_ESC, SLIP_ESC_ESC]
s_frameStart = SLIP_FRAME_START_CB
s_escStart = [SLIP_ESC, SLIP_ESC_START]
s_frameEnd = SLIP_FRAME_END
s_escEnd = [SLIP_ESC, SLIP_ESC_END]
s_custom = SLIP_CUSTOM
s_escCustom = [SLIP_ESC, SLIP_ESC_CUSTOM]


def ReplaceEn_SlipProtocol(source_list, find_item, replace_list):
    dest_list=[]
    for i in range(0,len(source_list)):
        if(source_list[i] == find_item):
            dest_list.extend(replace_list)
        else:
            dest_list.append(source_list[i])
    return dest_list


def ReplaceDe_SlipProtocol(source_list, find_item, replace_list):
    dest_list=[]
    j = len(source_list)
    for i in range(0,len(source_list)):
        if i == j:
            pass
        elif(source_list[i] == find_item[0] and source_list[i+1] == find_item[1]):
            dest_list.append(replace_list)
            j = i+1
        else:
            dest_list.append(source_list[i])
    return dest_list


def Encode_SlipProtocol(to_encode_list):
    dest_list = SLIP_FRAME_START_CB[:]
    dest_list.extend(to_encode_list)
    return dest_list


def Decode_SlipProtocol(to_decode_list):
    ret_val = 0
    data_list = []
    dest_list = to_decode_list[:]
    checksum_received = dest_list.pop(-1)
    # Calculate XOR checksum for received data
    checksum_calc = 0x00
    # check the checksum for received data
    for value in dest_list:
        checksum_calc = checksum_calc ^ value
    if checksum_received == checksum_calc:
        # check the response code
        if dest_list[8] != 0x00:
            ret_val = 0x10
        data_list = dest_list[10:]
    else:
        data_list = []
        ret_val = 0x01
        return ret_val
    return ret_val, data_list

def Decode_FE_CommProtocol(to_decode_list):
    ret_val = 0
    data_list = []
    dest_list = to_decode_list[:]
    crc_high_received = dest_list.pop(-1)
    crc_low_received = dest_list.pop(-1)
    # Calculate XOR checksum for received data
    crc16_calcu = CRC16CCITT.CRC16_CCITT(dest_list)
    crc16_low = crc16_calcu & 0x00FF
    crc16_high = crc16_calcu >> 8

    # check the checksum for received data
    if crc16_low == crc_low_received and crc16_high == crc_high_received:
        ret_val = dest_list[4:6]
        data_list = dest_list[6:]
    else:
        data_list = []
        # 0x0001 indicate that CRC check is wrong
        ret_val = 0x0001
        return ret_val
    return ret_val, data_list

# list1=[0,0,0,0,0xc0,0x84]
# list2=Encode_SlipProtocol(list1)
# print(list2)
# list2 = [223,219, 220, 4, 2, 0, 198, 141,192]
# list3=Decode_SlipProtocol(list2)
# print(list3)