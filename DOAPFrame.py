# coding: UTF-8
import CRC16CCITT
import struct

SLIP_FRAME_START_CB = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
SLIP_FRAME_END = 0xC0
PREA_FRAME_START = 0xFF
global FE_frame_number
FE_frame_number = 0


def convert_int_to_char(value):
    value_str = str(value)
    return value_str


def Build_DOAP_Request_Frame(request_code, board_idx, sub_idx, obj_idx, attr_idx, data_length, data_list):
    request_command_list = [0x82, 0x9A, 0x07, 0x01, 0x02, 0x03, request_code]
    # Append byteCounts based on request code
    if request_code == 0x01 or request_code == 0x05:
        request_command_list.append(0x08)
    elif request_code == 0x02:
        request_command_list.append(0x29)
    # Append board index
    request_command_list.append(board_idx)
    # Append address index
    request_command_list.append(0x00)
    # Append subsystem index
    request_command_list.append(0x00)
    request_command_list.append(sub_idx)
    # Append object index
    request_command_list.append(0x00)
    request_command_list.append(obj_idx)
    # Append data length
    if attr_idx == -1:
        request_command_list.append(0xFF)
        request_command_list.append(0xFF)
    else:
        request_command_list.append(0x00)
        request_command_list.append(attr_idx)
    # Append data
    if request_code == 0x02:
        request_command_list.append(len(data_list))
        request_command_list.extend(data_list)
        data_left_length = data_length - len(data_list) - 9
        data_list_to_add = [00] * data_left_length
        request_command_list.extend(data_list_to_add)
    else:
        pass
    # Calculate XOR checksum
    xor_checksum = 0x00
    for value in request_command_list:
        xor_checksum = xor_checksum ^ value
    request_command_list.append(xor_checksum)
    # print(request_command_list)
    # print(request_command_str)
    return request_command_list


def Build_FE_Client_Request_Frame(request_code, sub_idx, obj_idx, attri_idx, obj_size, data_list):
    request_command_list = [0x02]
    global FE_frame_number
    request_command_list.append(FE_frame_number)
    if request_code == 0x01:
        request_command_list.append(0x64)
    elif request_code == 0x02:
        request_command_list.append(0x65)
    request_command_list.append(obj_size)
    request_command_list.append(sub_idx)
    request_command_list.append(0x00)
    request_command_list.append(obj_idx)
    request_command_list.append(0x00)
    if attri_idx == -1:
        request_command_list.append(0xFF)
        request_command_list.append(0xFF)
    else:
        request_command_list.append(attri_idx)
        request_command_list.append(0x00)
    if request_code == 0x02:
        request_command_list.extend(data_list)
    else:
        pass
    crc16 = CRC16CCITT.CRC16_CCITT(request_command_list)
    crc16_low = crc16 & 0x00FF
    crc16_high = crc16 >> 8
    request_command_list.append(crc16_low)
    request_command_list.append(crc16_high)
    if FE_frame_number > 255:
        FE_frame_number += 1
    else:
        FE_frame_number += 1
    return request_command_list


def Split_DOAP_Frame(DOAP_frame_list):
    find_flag = False
    DOAP_Preamble_frame = []
    DOAP_data_frame = []
    for i in range(0, len(DOAP_frame_list)):
        if (DOAP_frame_list[i] == PREA_FRAME_START) and (DOAP_frame_list[i + 1] != PREA_FRAME_START):
            end_idx = i + 1
            find_flag = True
            break
    if find_flag:
        DOAP_Preamble_frame = DOAP_frame_list[:end_idx]
        DOAP_data_frame = DOAP_frame_list[end_idx:]
    return DOAP_Preamble_frame, DOAP_data_frame


def Check_DOAP_Ack_Frame(frame_list):
    if frame_list == 0x00 or frame_list[0] == 0x00:
        return True
    else:
        return False


def Check_DOAP_Nak_Frame(frame_list):
    if chr(frame_list[0] == 'n') and chr(frame_list[1] == 'a') and chr(frame_list[2]) == 'k':
        return True
    else:
        return False


def Check_response_frame_status(frame_list):
    if frame_list[0] & 0x80 == 0x80:
        return True
    else:
        return False


def Check_response_frame_error(frame_list):
    return frame_list[0] & 0x03


def Check_response_frame_CRC16(frame_list):
    crc16_calc_list = frame_list[:-2]
    crc16_calc_val = CRC16CCITT.CRC16_CCITT_FALSE(crc16_calc_list)
    crc16_rec_list = frame_list[-2:]
    crc16_rec_val = (crc16_rec_list[1] << 8) | crc16_rec_list[0]
    if (crc16_calc_val == crc16_rec_val):
        return True
    else:
        return False

# Build_DOAP_Request_Frame(0,0,0,[])
