#!/usr/bin/env python
"""
Hello World, but with more meat.
"""

import wx
import DOAPSerialHw
import DOAPFrame
import SlipProtocol
import struct
import pandas as pd

request_code_get_value = 0x01
request_code_put_value = 0x02
request_code_request = 0x00
request_code_response = 0x80


def Check_String_Is_Digital(in_str):
    dest_str = ''
    if (in_str[0] == '-'):
        dest_str = in_str[1:]
    else:
        dest_str = in_str[:]
    for i in range(1, len(dest_str)):
        if (dest_str[i] == '.'):
            dest_str = dest_str[:i] + dest_str[i + 1:]
            break
    return dest_str.isdigit()


# ["String", "TUSIGN8","TINT8","TUSIGN16","TINT16","TUSIGN32","TINT32","TFLOAT","HEX"]
def Get_Type_Size(type_idx):
    type_size = 0xFF
    if (type_idx == 1 or type_idx == 2):
        type_size = 1
    elif (type_idx == 3 or type_idx == 4):
        type_size = 2
    elif (type_idx >= 5 and type_idx <= 7):
        type_size = 4
    else:
        pass
    return type_size


def Check_String_Is_Int(in_str):
    dest_str = ''
    if (in_str[0] == '-'):
        dest_str = in_str[1:]
    else:
        dest_str = in_str[:]
    return dest_str.isdigit()


def DUMP_HEX(data_list):
    str_hex = ''
    for data in data_list:
        hex_val = hex(data)
        hex_val = hex_val[2:]
        if (len(hex_val) % 2 != 0):
            hex_val = '0' + hex_val
        str_hex += hex_val
    str_hex += '\n'
    str_hex = str_hex.upper()
    return str_hex


def Get_HEX_From_String(hex_str):
    dest_list = []
    if (len(hex_str) % 2 != 0):
        hex_str = '0' + hex_str
    for i in range(0, len(hex_str), 2):
        if ((hex_str[i] >= '0' and hex_str[i] <= '9') or (hex_str[i] >= 'a' and hex_str[i] <= 'f') or (
                hex_str[i] >= 'A' and hex_str[i] <= 'F')):
            tmp_str = hex_str[i] + hex_str[i + 1]
            item = DOAPSerialHw.Hex_str_to_int(tmp_str)
            dest_list.append(item)
        else:
            dest_list = []
            return dest_list
    return dest_list


def Convert_Character_To_Int(ch):
    num = 0
    if (ch >= '0' and ch <= '9'):
        num = ord(ch) - ord('0')
    elif (ch >= 'a' and ch <= 'f'):
        num = ord(ch) - ord('a') + 10
    elif (ch >= 'A' and ch <= 'F'):
        num = ord(ch) - ord('A') + 10
    else:
        pass
    return num


def Get_HEX_From_String(hex_str):
    dest_list = []
    if (len(hex_str) % 2 != 0):
        hex_str = '0' + hex_str
    for i in range(0, len(hex_str), 2):
        if ((hex_str[i] >= '0' and hex_str[i] <= '9') or (hex_str[i] >= 'a' and hex_str[i] <= 'f') or (
                hex_str[i] >= 'A' and hex_str[i] <= 'F')):
            value = Convert_Character_To_Int(hex_str[i]) * 16 + Convert_Character_To_Int(hex_str[i + 1])
            dest_list.append(value)
        else:
            dest_list = []
            return dest_list
    return dest_list


def Convert_String_To_ASCII_List(in_str):
    dest_list = []
    for ch in in_str:
        dest_list.append(ord(ch))
    return dest_list


def Set_Item_Bold(item):
    font = item.GetFont()
    font = font.Bold()
    item.SetFont(font)
    return


def Enlarge_font_size(item, enlarge_size):
    font = item.GetFont()
    font.PointSize += enlarge_size
    item.SetFont(font)
    return


def Set_font_Facename(item, facename):
    font = item.GetFont()
    font.SetFaceName(facename)
    item.SetFont(font)
    return


def Check_Is_Valid_String(check_list):
    find_flag = False
    check_result = True
    for item in check_list:
        if (item == 0):
            find_flag = True
            break
    if (find_flag == True):
        last_idx = check_list.index(0)
        if (last_idx != 0):
            string_list = check_list[:last_idx]
            zero_list = check_list[last_idx + 1:]
            for item in zero_list:
                if (item != 0):
                    return False
            for item in string_list:
                if (item < 32 or item > 126):
                    return False
        else:
            return False
    else:
        for item in check_list:
            if (item < 32 or item > 126):
                return False
    return check_result


def Convert_String_List_To_String(str_list):
    dest_str = ''
    for item in str_list:
        dest_str += chr(item)
    return dest_str


def Convert_4bytes_To_Float(byte_arr, board_type):
    # CB板大端解析为float类型
    # FE板数据，小端解析为float类型
    if board_type == 0x00:
        f_val = struct.unpack('>f', byte_arr)[0]
    else:
        f_val = struct.unpack('<f', byte_arr)[0]
    return f_val


class DOAP_PC_TOOL_FRAME(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(DOAP_PC_TOOL_FRAME, self).__init__(*args, **kw)

        # create a panel in the frame
        self.scroll = wx.ScrolledWindow(self, -1)  # Create a scroll on top frame
        self.scroll.SetScrollbars(1, 1, 730, 750)  # Set size of the scroll
        self.panel = wx.Panel(self.scroll)  # Create Panel on scroll frame

        self.ser = None
        self.res_decode_list = []
        self.res_obj_size = 0
        self.reponse_flag = False

        # create a sizer
        self.sizer = wx.GridBagSizer(hgap=0, vgap=0)

        self.title_foreground_colour = wx.Colour('white')
        self.title_background_colour = wx.Colour(0, 176, 240)

        # Show a example how to load pic.
        # serial_port_logo_row = 0
        # pic_ABB_logo =wx.Image('ABBLogo.jpg',wx.BITMAP_TYPE_JPEG)
        # bmp_ABB_logo = pic_ABB_logo.ConvertToBitmap()
        # logo_sbmp=wx.StaticBitmap(panel,-1,bitmap=bmp_ABB_logo)
        # #logo_sbmp.SetBackgroundColour('white')
        # sizer.Add(logo_sbmp, pos=(serial_port_logo_row, 0), span=(1,1), border = 0,flag = wx.ALL|wx.EXPAND|wx.ALIGN_LEFT)

        company_logo_row = 0
        company_logo_st = wx.StaticText(self.panel, label="ABB")
        company_logo_st.SetForegroundColour('red')
        Set_font_Facename(company_logo_st, "ABB Logo")
        Enlarge_font_size(company_logo_st, 10)
        self.sizer.Add(company_logo_st, pos=(company_logo_row, 0), border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port static text
        serial_port_title_row = company_logo_row + 1
        serial_port_st = wx.StaticText(self.panel, label="Serial Port Settings")
        serial_port_st.SetForegroundColour(self.title_foreground_colour)
        serial_port_st.SetBackgroundColour(self.title_background_colour)
        Set_font_Facename(serial_port_st, "ABBVoice")
        Set_Item_Bold(serial_port_st)
        Enlarge_font_size(serial_port_st, 2)
        self.sizer.Add(serial_port_st, pos=(serial_port_title_row, 0), span=(1, 6), border=10, flag=wx.ALL | wx.EXPAND)

        # Serial port static text
        serial_port_cfg_row1 = serial_port_title_row + 1
        serial_port_st = wx.StaticText(self.panel, label="Serial Port")
        Set_font_Facename(serial_port_st, "ABBVoice")
        Set_Item_Bold(serial_port_st)
        self.sizer.Add(serial_port_st, pos=(serial_port_cfg_row1, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port selection list
        self.choice_list = DOAPSerialHw.detect_available_serial_port()
        self.serial_port_ch = wx.Choice(self.panel, choices=self.choice_list)
        Set_font_Facename(self.serial_port_ch, "ABBVoice")
        default_sel_idx = 0
        self.serial_port_ch.SetSelection(default_sel_idx)
        self.sizer.Add(self.serial_port_ch, pos=(serial_port_cfg_row1, 1), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port baud rate static text
        serial_port_baudrate_st = wx.StaticText(self.panel, label="Baud Rate")
        Set_font_Facename(serial_port_baudrate_st, "ABBVoice")
        Set_Item_Bold(serial_port_baudrate_st)
        self.sizer.Add(serial_port_baudrate_st, pos=(serial_port_cfg_row1, 2), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port selection list
        choice_list = ['9600', '19200']
        self.serial_port_baudrate_ch = wx.Choice(self.panel, choices=choice_list)
        Set_font_Facename(self.serial_port_baudrate_ch, "ABBVoice")
        default_sel_idx = choice_list.index('19200')
        self.serial_port_baudrate_ch.SetSelection(default_sel_idx)
        self.Bind(wx.EVT_CHOICE, self.request_frame_cfg_board_idx_reset, self.serial_port_baudrate_ch)
        self.sizer.Add(self.serial_port_baudrate_ch, pos=(serial_port_cfg_row1, 3), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity static text
        serial_port_parity_st = wx.StaticText(self.panel, label="Parity")
        Set_font_Facename(serial_port_parity_st, "ABBVoice")
        Set_Item_Bold(serial_port_parity_st)
        self.sizer.Add(serial_port_parity_st, pos=(serial_port_cfg_row1, 4), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity selection list
        choice_list = ['None', 'Odd', 'Even']
        self.serial_port_parity_ch = wx.Choice(self.panel, choices=choice_list)
        Set_font_Facename(self.serial_port_parity_ch, "ABBVoice")
        default_sel_idx = choice_list.index('Odd')
        self.serial_port_parity_ch.SetSelection(default_sel_idx)
        self.sizer.Add(self.serial_port_parity_ch, pos=(serial_port_cfg_row1, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity static text
        serial_port_cfg_row2 = serial_port_cfg_row1 + 1
        serial_port_databits_st = wx.StaticText(self.panel, label="Databits")
        Set_font_Facename(serial_port_databits_st, "ABBVoice")
        Set_Item_Bold(serial_port_databits_st)
        self.sizer.Add(serial_port_databits_st, pos=(serial_port_cfg_row2, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity selection list
        choice_list = ['7', '8']
        self.serial_port_databits_ch = wx.Choice(self.panel, choices=choice_list)
        Set_font_Facename(self.serial_port_databits_ch, "ABBVoice")
        default_sel_idx = choice_list.index('8')
        self.serial_port_databits_ch.SetSelection(default_sel_idx)
        self.sizer.Add(self.serial_port_databits_ch, pos=(serial_port_cfg_row2, 1), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity static text
        serial_port_stopbits_st = wx.StaticText(self.panel, label="Stopbits")
        Set_font_Facename(serial_port_stopbits_st, "ABBVoice")
        Set_Item_Bold(serial_port_stopbits_st)
        self.sizer.Add(serial_port_stopbits_st, pos=(serial_port_cfg_row2, 2), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity selection list
        choice_list = ["1", "2"]
        self.serial_port_stopbits_ch = wx.Choice(self.panel, choices=choice_list)
        Set_font_Facename(self.serial_port_stopbits_ch, "ABBVoice")
        default_sel_idx = choice_list.index('1')
        self.serial_port_stopbits_ch.SetSelection(default_sel_idx)
        self.sizer.Add(self.serial_port_stopbits_ch, pos=(serial_port_cfg_row2, 3), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity selection list
        # self.serial_port_detect_button = wx.Button(self.panel, label="Detect")
        # self.Bind(wx.EVT_BUTTON, self.serial_port_detect_on_click, self.serial_port_detect_button)
        # self.serial_port_detect_button.SetBackgroundColour('grey')
        # Set_font_Facename(self.serial_port_detect_button,"ABBVoice")
        # Set_Item_Bold(self.serial_port_detect_button)
        # self.sizer.Add(self.serial_port_detect_button, pos=(serial_port_cfg_row2, 5), border = 10,flag = wx.ALL|wx.EXPAND|wx.ALIGN_LEFT)

        serial_port_connect_row = serial_port_cfg_row2
        self.serial_port_connect_button = wx.Button(self.panel, label="Connect")
        Set_font_Facename(self.serial_port_connect_button, "ABBVoice")
        self.serial_port_connect_button.SetBackgroundColour('grey')
        self.Bind(wx.EVT_BUTTON, self.serial_port_on_click, self.serial_port_connect_button)
        Set_Item_Bold(self.serial_port_connect_button)
        self.sizer.Add(self.serial_port_connect_button, pos=(serial_port_cfg_row2, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity static text
        # self.serial_port_connect_status_bt = wx.Button(panel, label='')
        # self.serial_port_connect_status_bt.SetBackgroundColour('grey')
        # sizer.Add(self.serial_port_connect_status_bt, pos=(serial_port_connect_row, 5), border = 10,flag = wx.ALL|wx.EXPAND|wx.ALIGN_CENTER)

        # This part is Request Frame
        request_frame_row = serial_port_connect_row + 1
        request_frame_title_st = wx.StaticText(self.panel, label="Request Frame")
        request_frame_title_st.SetForegroundColour(self.title_foreground_colour)
        request_frame_title_st.SetBackgroundColour(self.title_background_colour)
        Set_font_Facename(request_frame_title_st, "ABBVoice")
        Set_Item_Bold(request_frame_title_st)
        Enlarge_font_size(request_frame_title_st, 2)
        self.sizer.Add(request_frame_title_st, pos=(request_frame_row, 0), span=(1, 6), border=10,
                       flag=wx.ALL | wx.EXPAND)

        # Serial port parity static text
        request_frame_cfg_row1 = request_frame_row + 1
        request_frame_cfg_command_st = wx.StaticText(self.panel, label="Command")
        Set_font_Facename(request_frame_cfg_command_st, "ABBVoice")
        Set_Item_Bold(request_frame_cfg_command_st)
        self.sizer.Add(request_frame_cfg_command_st, pos=(request_frame_cfg_row1, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # "Get Object", "Put Object" selection list
        choice_list = ["Get Object", "Put Object"]
        self.request_frame_cfg_command_ch = wx.Choice(self.panel, choices=choice_list)
        self.Bind(wx.EVT_CHOICE, self.request_frame_cfg_command_selected, self.request_frame_cfg_command_ch)
        Set_font_Facename(self.request_frame_cfg_command_ch, "ABBVoice")
        default_sel_idx = choice_list.index('Get Object')
        self.request_frame_cfg_command_ch.SetSelection(default_sel_idx)
        self.sizer.Add(self.request_frame_cfg_command_ch, pos=(request_frame_cfg_row1, 1), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Subsys Idx static text
        request_frame_cfg_subidx_st = wx.StaticText(self.panel, label="Subsys Idx")
        Set_font_Facename(request_frame_cfg_subidx_st, "ABBVoice")
        Set_Item_Bold(request_frame_cfg_subidx_st)
        self.sizer.Add(request_frame_cfg_subidx_st, pos=(request_frame_cfg_row1, 2), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Subsys Idx text ctrl
        self.request_frame_cfg_subidx_it = wx.TextCtrl(self.panel)
        self.request_frame_cfg_subidx_it.Value = '0'
        Set_font_Facename(self.request_frame_cfg_subidx_it, "ABBVoice")
        self.sizer.Add(self.request_frame_cfg_subidx_it, pos=(request_frame_cfg_row1, 3), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Object Idx static text
        request_frame_cfg_objidx_st = wx.StaticText(self.panel, label="Object Idx")
        Set_font_Facename(request_frame_cfg_objidx_st, "ABBVoice")
        Set_Item_Bold(request_frame_cfg_objidx_st)
        self.sizer.Add(request_frame_cfg_objidx_st, pos=(request_frame_cfg_row1, 4), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Object Idx text ctrl
        self.request_frame_cfg_objidx_it = wx.TextCtrl(self.panel)
        self.request_frame_cfg_objidx_it.Value = '0'
        Set_font_Facename(self.request_frame_cfg_objidx_it, "ABBVoice")
        self.sizer.Add(self.request_frame_cfg_objidx_it, pos=(request_frame_cfg_row1, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # attribute idx static text
        self.request_frame_cfg_row2 = request_frame_cfg_row1 + 1
        self.request_frame_cfg_attribute_idx_st = wx.StaticText(self.panel, label="Attribute Idx")
        Set_font_Facename(self.request_frame_cfg_attribute_idx_st, "ABBVoice")
        Set_Item_Bold(self.request_frame_cfg_attribute_idx_st)
        self.sizer.Add(self.request_frame_cfg_attribute_idx_st, pos=(self.request_frame_cfg_row2, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        # attribute index text ctrl
        self.request_frame_cfg_attribute_idx_tc = wx.TextCtrl(self.panel)
        self.request_frame_cfg_attribute_idx_tc.Value = '-1'
        Set_font_Facename(self.request_frame_cfg_attribute_idx_tc, "ABBVoice")
        self.sizer.Add(self.request_frame_cfg_attribute_idx_tc, pos=(self.request_frame_cfg_row2, 1), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # board index static text
        self.request_frame_cfg_row2 = request_frame_cfg_row1 + 1
        self.request_frame_cfg_obj_size_st = wx.StaticText(self.panel, label="Board Idx")
        Set_font_Facename(self.request_frame_cfg_obj_size_st, "ABBVoice")
        Set_Item_Bold(self.request_frame_cfg_obj_size_st)
        self.sizer.Add(self.request_frame_cfg_obj_size_st, pos=(self.request_frame_cfg_row2, 2), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # board index text ctrl
        self.request_frame_cfg_obj_size_it = wx.TextCtrl(self.panel)
        self.request_frame_cfg_obj_size_it.Value = '0'
        Set_font_Facename(self.request_frame_cfg_obj_size_it, "ABBVoice")
        self.sizer.Add(self.request_frame_cfg_obj_size_it, pos=(self.request_frame_cfg_row2, 3), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Object Type static text
        self.request_frame_cfg_obj_type_st = wx.StaticText(self.panel, label="Object Type")
        Set_font_Facename(self.request_frame_cfg_obj_type_st, "ABBVoice")
        Set_Item_Bold(self.request_frame_cfg_obj_type_st)
        self.sizer.Add(self.request_frame_cfg_obj_type_st, pos=(self.request_frame_cfg_row2, 4), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Object Type selection list
        choice_list = ["String", "TUSIGN8", "TINT8", "TUSIGN16", "TINT16", "TUSIGN32", "TINT32", "TFLOAT", "HEX"]
        self.request_frame_cfg_obj_type_ch = wx.Choice(self.panel, choices=choice_list)
        self.Bind(wx.EVT_CHOICE, self.request_frame_cfg_obj_type_selected, self.request_frame_cfg_obj_type_ch)
        default_sel_idx = choice_list.index('HEX')
        self.request_frame_cfg_obj_type_ch.SetSelection(default_sel_idx)
        Set_font_Facename(self.request_frame_cfg_obj_type_ch, "ABBVoice")
        self.sizer.Add(self.request_frame_cfg_obj_type_ch, pos=(self.request_frame_cfg_row2, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Object Data static text
        self.request_frame_cfg_row3 = self.request_frame_cfg_row2 + 1
        self.request_frame_cfg_obj_data_st = wx.StaticText(self.panel, label="Object Data")
        Set_font_Facename(self.request_frame_cfg_obj_data_st, "ABBVoice")
        Set_Item_Bold(self.request_frame_cfg_obj_data_st)
        self.sizer.Add(self.request_frame_cfg_obj_data_st, pos=(self.request_frame_cfg_row3, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Object Data text ctrl
        self.request_frame_object_data_span_row = 2
        self.request_frame_cfg_obj_data_it = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        Set_font_Facename(self.request_frame_cfg_obj_data_it, "ABBVoice")
        self.sizer.Add(self.request_frame_cfg_obj_data_it, pos=(self.request_frame_cfg_row3, 1),
                       span=(self.request_frame_object_data_span_row, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)

        self.request_frame_send_button_row = self.request_frame_cfg_row3 + self.request_frame_object_data_span_row
        self.request_frame_send_button = wx.Button(self.panel, label="Send")
        Set_font_Facename(self.request_frame_send_button, "ABBVoice")
        self.request_frame_send_button.SetBackgroundColour('grey')
        self.Bind(wx.EVT_BUTTON, self.send_on_click, self.request_frame_send_button)
        Set_Item_Bold(self.request_frame_send_button)
        self.sizer.Add(self.request_frame_send_button, pos=(self.request_frame_send_button_row, 0), span=(1, 6),
                       border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)

        self.reponse_frame_row = self.request_frame_send_button_row + 1
        self.response_frame_title_st = wx.StaticText(self.panel, label="Response Frame")
        self.response_frame_title_st.SetForegroundColour(self.title_foreground_colour)
        self.response_frame_title_st.SetBackgroundColour(self.title_background_colour)
        Set_font_Facename(self.response_frame_title_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_title_st)
        Enlarge_font_size(self.response_frame_title_st, 2)
        self.sizer.Add(self.response_frame_title_st, pos=(self.reponse_frame_row, 0), span=(1, 6), border=10,
                       flag=wx.ALL | wx.EXPAND)

        self.response_frame_para_row1 = self.reponse_frame_row + 1
        self.response_frame_cfg_command_st = wx.StaticText(self.panel, label="Command")
        Set_font_Facename(self.response_frame_cfg_command_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_cfg_command_st)
        self.sizer.Add(self.response_frame_cfg_command_st, pos=(self.response_frame_para_row1, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity selection list
        self.response_frame_cfg_command_dt = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        Set_font_Facename(self.response_frame_cfg_command_dt, "ABBVoice")
        self.sizer.Add(self.response_frame_cfg_command_dt, pos=(self.response_frame_para_row1, 1), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)

        # Serial port parity static text
        self.response_frame_cfg_subidx_st = wx.StaticText(self.panel, label="Subsys Idx")
        Set_font_Facename(self.response_frame_cfg_subidx_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_cfg_subidx_st)
        self.sizer.Add(self.response_frame_cfg_subidx_st, pos=(self.response_frame_para_row1, 2), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        #
        self.response_frame_cfg_subidx_dt = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        Set_font_Facename(self.response_frame_cfg_subidx_dt, "ABBVoice")
        self.sizer.Add(self.response_frame_cfg_subidx_dt, pos=(self.response_frame_para_row1, 3), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)

        # Serial port parity static text
        self.response_frame_cfg_objidx_st = wx.StaticText(self.panel, label="Object Idx")
        Set_font_Facename(self.response_frame_cfg_objidx_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_cfg_objidx_st)
        self.sizer.Add(self.response_frame_cfg_objidx_st, pos=(self.response_frame_para_row1, 4), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        #
        self.response_frame_cfg_objidx_dt = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        Set_font_Facename(self.response_frame_cfg_objidx_dt, "ABBVoice")
        self.sizer.Add(self.response_frame_cfg_objidx_dt, pos=(self.response_frame_para_row1, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)

        # board type static text
        self.response_frame_para_row2 = self.response_frame_para_row1 + 1
        self.response_frame_cfg_attribute_idx_st = wx.StaticText(self.panel, label="Attribute Idx")
        Set_font_Facename(self.response_frame_cfg_attribute_idx_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_cfg_attribute_idx_st)
        self.sizer.Add(self.response_frame_cfg_attribute_idx_st, pos=(self.response_frame_para_row2, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        # board type text ctrl
        self.response_frame_cfg_attribute_idx_tc = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        Set_font_Facename(self.response_frame_cfg_attribute_idx_tc, "ABBVoice")
        self.sizer.Add(self.response_frame_cfg_attribute_idx_tc, pos=(self.response_frame_para_row2, 1), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity static text
        self.response_frame_para_row2 = self.response_frame_para_row1 + 1
        self.response_frame_cfg_obj_size_st = wx.StaticText(self.panel, label="Object Size")
        Set_font_Facename(self.response_frame_cfg_obj_size_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_cfg_obj_size_st)
        self.sizer.Add(self.response_frame_cfg_obj_size_st, pos=(self.response_frame_para_row2, 2), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        #
        self.response_frame_cfg_obj_size_dt = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        Set_font_Facename(self.response_frame_cfg_obj_size_dt, "ABBVoice")
        self.sizer.Add(self.response_frame_cfg_obj_size_dt, pos=(self.response_frame_para_row2, 3), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)

        #
        # Serial port parity static text
        self.response_frame_cfg_obj_type_st = wx.StaticText(self.panel, label="Object Type")
        Set_font_Facename(self.response_frame_cfg_obj_type_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_cfg_obj_type_st)
        self.sizer.Add(self.response_frame_cfg_obj_type_st, pos=(self.response_frame_para_row2, 4), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity selection list
        choice_list = ["String", "TUSIGN8", "TINT8", "TUSIGN16", "TINT16", "TUSIGN32", "TINT32", "TFLOAT", "HEX"]
        self.response_frame_cfg_obj_type_ch = wx.Choice(self.panel, choices=choice_list)
        self.Bind(wx.EVT_CHOICE, self.response_frame_cfg_obj_type_selected, self.response_frame_cfg_obj_type_ch)
        default_sel_idx = choice_list.index('HEX')
        self.response_frame_cfg_obj_type_ch.SetSelection(default_sel_idx)
        Set_font_Facename(self.response_frame_cfg_obj_type_ch, "ABBVoice")
        self.sizer.Add(self.response_frame_cfg_obj_type_ch, pos=(self.response_frame_para_row2, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)

        # Serial port parity static text
        self.response_frame_para_row3 = self.response_frame_para_row2 + 1
        self.response_frame_cfg_obj_data_st = wx.StaticText(self.panel, label="Object Data")
        Set_font_Facename(self.response_frame_cfg_obj_data_st, "ABBVoice")
        Set_Item_Bold(self.response_frame_cfg_obj_data_st)
        self.sizer.Add(self.response_frame_cfg_obj_data_st, pos=(self.response_frame_para_row3, 0), border=10,
                       flag=wx.ALL | wx.EXPAND)

        #
        self.response_frame_object_data_span_row = 2
        self.response_frame_cfg_obj_data_dt = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        Set_font_Facename(self.response_frame_cfg_obj_data_dt, "ABBVoice")
        self.sizer.Add(self.response_frame_cfg_obj_data_dt, pos=(self.response_frame_para_row3, 1),
                       span=(self.response_frame_object_data_span_row, 5), border=10, flag=wx.ALL | wx.EXPAND)

        self.message_display_row = self.response_frame_para_row3 + self.response_frame_object_data_span_row
        self.message_display_span_row = 6
        self.message_display_dt = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
        Set_font_Facename(self.message_display_dt, "ABBVoice")
        self.sizer.Add(self.message_display_dt, pos=(self.message_display_row, 0),
                       span=(self.message_display_span_row, 6), border=10, flag=wx.ALL | wx.EXPAND)

        self.Request_parameter_inavailable()

        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(self.sizer)
        # self.sizer.Layout()
        self.panel.Fit()

        # connect_button = wx.ToggleButton(serial_port_config_pnl, label="Connect")
        # Set_Item_Bold(connect_button)

        # serial_port_connect_sizer = wx.FlexGridSizer(rows=1, cols=1, vgap=3, hgap=3)
        # serial_port_connect_pnl.SetSizer(serial_port_connect_sizer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome Use LMT PC Tools!")

    def serial_port_on_click(self, event):
        if (self.serial_port_connect_button.Label == "Connect"):
            serial_port_sel_name = self.serial_port_ch.GetString(self.serial_port_ch.GetSelection())
            serial_port_baudrate_sel = self.serial_port_baudrate_ch.GetString(
                self.serial_port_baudrate_ch.GetSelection())
            serial_port_parity_sel = self.serial_port_parity_ch.GetString(self.serial_port_parity_ch.GetSelection())
            serial_port_databits_sel = self.serial_port_databits_ch.GetString(
                self.serial_port_databits_ch.GetSelection())
            serial_port_stopbits_sel = self.serial_port_stopbits_ch.GetString(
                self.serial_port_stopbits_ch.GetSelection())
            serial_port_cfg = DOAPSerialHw.check_serial_port_config(serial_port_sel_name, serial_port_baudrate_sel,
                                                                    serial_port_parity_sel, serial_port_databits_sel,
                                                                    serial_port_stopbits_sel)
            if (serial_port_cfg != []):
                self.ser = DOAPSerialHw.serial_port_connect(serial_port_cfg)
                if (DOAPSerialHw.check_serial_port_connected(self.ser)):
                    connect_success_str = 'Serial Port '
                    connect_success_str += serial_port_cfg[0]
                    connect_success_str += ' Baud Rate '
                    connect_success_str += str(serial_port_cfg[1])
                    connect_success_str += ' Parity '
                    connect_success_str += str(serial_port_cfg[2])
                    connect_success_str += ' Data Bits '
                    connect_success_str += str(serial_port_cfg[3])
                    connect_success_str += ' Stop Bits '
                    connect_success_str += str(serial_port_cfg[4])
                    connect_success_str += ' Connected Success'
                    self.serial_port_connect_button.SetBackgroundColour('green')
                    self.request_frame_send_button.SetBackgroundColour('green')
                    self.message_display_dt.Value = connect_success_str
                    self.serial_port_connect_button.Label = "Disconnect"
                else:
                    self.message_display_dt.Value = "Serial Port Connected Failed"
            else:
                self.message_display_dt.Value = "Serial Port Configuration Not Set"
        else:
            DOAPSerialHw.serial_port_disconnect(self.ser)
            self.serial_port_connect_button.SetBackgroundColour('grey')
            self.request_frame_send_button.SetBackgroundColour('grey')
            self.message_display_dt.Value = "Serial Port Disconnected"
            self.serial_port_connect_button.Label = "Connect"

    def serial_port_detect_on_click(self, event):
        if (self.ser and DOAPSerialHw.check_serial_port_connected(self.ser)):
            pass
        else:
            self.choice_list = DOAPSerialHw.detect_available_serial_port()
            if (self.choice_list != []):
                self.serial_port_detect_button.SetBackgroundColour('green')
            else:
                self.serial_port_detect_button.SetBackgroundColour('grey')
            self.serial_port_ch.SetItems(self.choice_list)
        return

    def Auto_Detect_Object_Type(self, obj_size, obj_data):
        # Default type is hex
        type_idx = 8
        if (obj_size > 4):
            if (Check_Is_Valid_String(obj_data)):
                type_idx = 0
        elif (obj_size == 4):
            # Default 4 byte type is TFLOAT
            type_idx = 7
        elif (obj_size == 2):
            # Default 2 byte type is TUSIGN16
            type_idx = 3
        elif (obj_size == 1):
            # Default 1 byte type is TUSIGN8
            type_idx = 1
        else:
            pass
        return type_idx

    # "String", "TUSIGN8","TINT8","TUSIGN16","TINT16","TUSIGN32","TINT32","TFLOAT","HEX"
    def Check_if_type_select_valid(self, type_idx, obj_size):
        check_res = False
        if type_idx <= 2 or type_idx == 8:
            check_res = True
        elif type_idx == 3 or type_idx == 4:
            if obj_size % 2 == 0:
                check_res = True
            else:
                check_res = False
        elif 5 <= type_idx <= 7:
            if obj_size % 4 == 0:
                check_res = True
            else:
                check_res = False
        else:
            pass
        return check_res

    def Conver_Data_Object_By_Type(self, type_idx, obj_data, board_type):
        dest_str = ''
        if (type_idx == 0):
            end_idx = obj_data.index(0)
            for i in range(0, end_idx):
                dest_str += chr(obj_data[i])
        elif type_idx == 1:
            for i in range(0, len(obj_data), 1):
                obj = obj_data[i:i + 1]
                byte_arr = bytearray(obj)
                f_val = struct.unpack('B', byte_arr)[0]
                dest_str += str(f_val) + ' '
        elif type_idx == 2:
            for i in range(0, len(obj_data), 1):
                obj = obj_data[i:i + 1]
                byte_arr = bytearray(obj)
                value = struct.unpack('b', byte_arr)[0]
                dest_str += str(value) + ' '
        elif type_idx == 3:
            for i in range(0, len(obj_data), 2):
                obj = obj_data[i:i + 2]
                byte_arr = bytearray(obj)
                if board_type == 0x01:
                    value = struct.unpack('<H', byte_arr)[0]
                else:
                    value = struct.unpack('>H', byte_arr)[0]
                dest_str += str(value) + ' '
        elif type_idx == 4:
            for i in range(0, len(obj_data), 2):
                obj = obj_data[i:i + 2]
                byte_arr = bytearray(obj)
                if board_type == 0x01:
                    value = struct.unpack('<h', byte_arr)[0]
                else:
                    value = struct.unpack('>h', byte_arr)[0]
                dest_str += str(value) + ' '
        elif type_idx == 5:
            for i in range(0, len(obj_data), 4):
                obj = obj_data[i:i + 4]
                byte_arr = bytearray(obj)
                # CB板数据采用大端模式解析
                # FE板数据采用小端模式解析
                if board_type == 0x00:
                    f_val = struct.unpack('>I', byte_arr)[0]
                else:
                    f_val = struct.unpack('<I', byte_arr)[0]
                dest_str += str(f_val) + ' '
        elif type_idx == 6:
            for i in range(0, len(obj_data), 4):
                obj = obj_data[i:i + 4]
                byte_arr = bytearray(obj)
                if board_type == 0x00:
                    value = struct.unpack('>i', byte_arr)[0]
                else:
                    value = struct.unpack('<i', byte_arr)[0]
                dest_str += str(value) + ' '
        elif type_idx == 7:
            for i in range(0, len(obj_data), 4):
                obj = obj_data[i:i + 4]
                byte_arr = bytearray(obj)
                f_val = Convert_4bytes_To_Float(byte_arr, board_type)
                dest_str += str(f_val) + ' '
        elif type_idx == 8:
            dest_str += "0x" + DUMP_HEX(obj_data)
        return dest_str

    def search_data_type(self, data_type_str):
        type_idx = 8
        if data_type_str in ['TABENUM8', 'SIMPLE_U8', 'ACTION']:
            type_idx = 1
        elif data_type_str in ['SIMPLE_FLOAT', 'FLOAT']:
            type_idx = 7
        elif data_type_str in ['SIMPLE_U32']:
            type_idx = 5
        elif data_type_str in ['SIMPLE_I16']:
            type_idx = 4
        elif data_type_str in ['SIMPLE_U16', ]:
            type_idx = 3
        return type_idx

    def Parse_DOAP_Response_Frame(self, frame_list):
        if frame_list[0] & 0x40 == 0x00:
            self.response_frame_cfg_command_dt.Value = 'Get Object'
        else:
            self.response_frame_cfg_command_dt.Value = 'Put Object'
        self.response_frame_cfg_subidx_dt.Value = str(frame_list[1])
        self.response_frame_cfg_objidx_dt.Value = str(frame_list[2])
        self.res_obj_size = frame_list[3]
        self.response_frame_cfg_obj_size_dt.Value = str(frame_list[3])
        data_list = frame_list[4:-2]
        auto_detect_idx = self.Auto_Detect_Object_Type(frame_list[3], data_list)
        self.response_frame_cfg_obj_type_ch.SetSelection(auto_detect_idx)
        convert_str = self.Conver_Data_Object_By_Type(auto_detect_idx, data_list)
        self.response_frame_cfg_obj_data_dt.Value = convert_str

    def Clear_DOAP_Response_Display(self):
        self.response_frame_cfg_command_dt.Value = ''
        self.response_frame_cfg_subidx_dt.Value = ''
        self.response_frame_cfg_objidx_dt.Value = ''
        self.response_frame_cfg_obj_size_dt.Value = ''
        # self.response_frame_cfg_obj_type_ch.SetSelection(8)
        self.response_frame_cfg_obj_data_dt.Value = ''

    # ["String", "TUSIGN8","TINT8","TUSIGN16","TINT16","TUSIGN32","TINT32","TFLOAT","HEX"]
    def Set_Request_Frame_Data_List(self, board_type):
        data_list = []
        obj_type_idx = self.request_frame_cfg_obj_type_ch.GetSelection()
        obj_data_str = self.request_frame_cfg_obj_data_it.Value
        if obj_data_str == '':
            return data_list

        if obj_type_idx == 0:
            data_list = Convert_String_To_ASCII_List(obj_data_str)

        elif obj_type_idx == 1:
            obj_list = obj_data_str.split(" ")
            for i in range(0, len(obj_list)):
                if obj_list[i].isdigit():
                    val = int(obj_list[i])
                    if 0 <= val < 255:
                        byte_arr = struct.pack('B', val)
                        data_list.append(ord(byte_arr))
                    else:
                        self.message_display_dt.Value = 'Object Data Out of Range'
                else:
                    self.message_display_dt.Value = 'Object Data Is Not A Number'
        elif obj_type_idx == 2:
            obj_list = obj_data_str.split(" ")
            for i in range(0, len(obj_list)):
                if Check_String_Is_Int(obj_list[i]):
                    val = int(obj_list[i])
                    if -128 <= val < 127:
                        byte_arr = struct.pack('b', val)
                        data_list.append(ord(byte_arr))
                    else:
                        self.message_display_dt.Value = 'Object Data Out of Range'
                else:
                    self.message_display_dt.Value = 'Object Data Is Not A Number'
        elif obj_type_idx == 3:
            obj_list = obj_data_str.split(" ")
            for obj in range(0, len(obj_list)):
                if obj_list[obj].isdigit():
                    val = int(obj_list[obj])
                    if 0 <= val < 65535:
                        if board_type == 0x01:
                            byte_arr = struct.pack('<H', val)
                        else:
                            byte_arr = struct.pack('>H', val)
                        for byte in byte_arr:
                            data_list.append(byte)
                    else:
                        self.message_display_dt.Value = 'Object Data Out of Range'
                else:
                    self.message_display_dt.Value = 'Object Data Is Not A Number'
        elif obj_type_idx == 4:
            obj_list = obj_data_str.split(" ")
            for obj in range(0, len(obj_list)):
                if Check_String_Is_Int(obj_list[obj]):
                    val = int(obj_list[obj])
                    if -32768 <= val < 32767:
                        if board_type == 0x01:
                            byte_arr = struct.pack('<h', val)
                        else:
                            byte_arr = struct.pack('>h', val)
                        for byte in byte_arr:
                            data_list.append(byte)
                    else:
                        self.message_display_dt.Value = 'Object Data Out of Range'
                else:
                    self.message_display_dt.Value = 'Object Data Is Not A Number'
        elif obj_type_idx == 5:
            obj_list = obj_data_str.split(" ")
            for i in range(0, len(obj_list)):
                if obj_list[i].isdigit():
                    val = int(obj_list[i])
                    if 0 <= val < 4294967295:
                        if board_type == 0x01:
                            byte_arr = struct.pack('<I', val)
                        else:
                            byte_arr = struct.pack('>I', val)
                        for byte in byte_arr:
                            data_list.append(byte)
                    else:
                        self.message_display_dt.Value = 'Object Data Out of Range'
                else:
                    self.message_display_dt.Value = 'Object Data Is Not A Number'
        elif obj_type_idx == 6:
            obj_list = obj_data_str.split(" ")
            for i in range(0, len(obj_list)):
                if Check_String_Is_Int(obj_list[i]):
                    val = int(obj_list[i])
                    if -2147483648 <= val < 2147483647:
                        if board_type == 0x01:
                            byte_arr = struct.pack('<i', val)
                        else:
                            byte_arr = struct.pack('>i', val)
                        for byte in byte_arr:
                            data_list.append(ord(byte))
                    else:
                        self.message_display_dt.Value = 'Object Data Out of Range'
                else:
                    self.message_display_dt.Value = 'Object Data Is Not A Number'
        elif obj_type_idx == 7:
            obj_list = obj_data_str.split(" ")
            for obj in range(0, len(obj_list)):
                if Check_String_Is_Digital(obj_list[obj]):
                    val = float(obj_list[obj])
                    if board_type == 0x01:
                        byte_arr = struct.pack('<f', val)
                    else:
                        byte_arr = struct.pack('>f', val)
                    for byte in byte_arr:
                        data_list.append(byte)
                else:
                    self.message_display_dt.Value = 'Object Data Is Not A Float Value'
        elif obj_type_idx == 8:
            data_list = Get_HEX_From_String(obj_data_str)
            if not data_list:
                self.message_display_dt.Value = 'Not A Valid HEX'
            else:
                pass
        else:
            pass
        return data_list

    # ["String", "TUSIGN8","TINT8","TUSIGN16","TINT16","TUSIGN32","TINT32","TFLOAT","HEX"]
    def Set_Request_Obj_Size_By_Type(self):
        # obj_type_idx = self.request_frame_cfg_obj_type_ch.GetSelection()
        # if (obj_type_idx == 1 or obj_type_idx == 2):
        #     self.request_frame_cfg_obj_size_it.Value = '1'
        # elif (obj_type_idx == 3 or obj_type_idx == 4):
        #     self.request_frame_cfg_obj_size_it.Value = '2'
        # elif (obj_type_idx >= 5 and obj_type_idx <= 7):
        #     self.request_frame_cfg_obj_size_it.Value = '4'
        # else:
        #     self.request_frame_cfg_obj_size_it.Value = '0'
        return

    def DOAP_Get_Put_Object(self):
        self.ser.timeout = 0.5
        self.reponse_flag = False
        req_cmd_str = self.request_frame_cfg_command_ch.GetString(self.request_frame_cfg_command_ch.GetSelection())

        req_board_idx_str = self.request_frame_cfg_obj_size_it.Value
        if req_board_idx_str == '1':
            object_lists = pd.read_csv('./FEdataOBJ_0_9_9_Pra.csv')
        elif req_board_idx_str == '0':
            object_lists = pd.read_csv('./CBdataOBJPra.csv')
        else:
            pass

        if req_cmd_str == 'Get Object':
            req_sub_idx_str = self.request_frame_cfg_subidx_it.Value
            req_obj_idx_str = self.request_frame_cfg_objidx_it.Value
            req_attribute_str = self.request_frame_cfg_attribute_idx_tc.Value
            match_objidx_row = object_lists[
                (object_lists["SUBIDX"] == int(req_sub_idx_str)) & (object_lists["OBJIDX"] == int(req_obj_idx_str))]
            match_type_str = match_objidx_row["TYPE"]
            # "String", "TUSIGN8","TINT8","TUSIGN16","TINT16","TUSIGN32","TINT32","TFLOAT","HEX"
            type_idx = self.search_data_type(match_type_str.values)

            if req_sub_idx_str.isdigit() and req_obj_idx_str.isdigit():
                req_data_list = []
                baud_set = self.serial_port_baudrate_ch.GetSelection()
                if baud_set == 1:
                    req_frame_list = DOAPFrame.Build_DOAP_Request_Frame(request_code_get_value, int(req_board_idx_str),
                                                                        int(req_sub_idx_str), int(req_obj_idx_str),
                                                                        int(req_attribute_str),
                                                                        0x06, req_data_list)
                    req_encode_list = SlipProtocol.Encode_SlipProtocol(req_frame_list)
                else:
                    req_frame_list = DOAPFrame.Build_FE_Client_Request_Frame(request_code_get_value,
                                                                             int(req_sub_idx_str), int(req_obj_idx_str),
                                                                             int(req_attribute_str), 8,
                                                                             req_data_list)
                    req_encode_list = req_frame_list
                self.message_display_dt.Value = 'DOAP Request Frame: '
                self.message_display_dt.Value += DUMP_HEX(req_frame_list)
                self.message_display_dt.Value += 'DOAP Encode Request Frame: '
                self.message_display_dt.Value += DUMP_HEX(req_encode_list)
                DOAPSerialHw.serial_port_write(self.ser, req_encode_list)
                req_encode_list.clear()
                res_frame_list = DOAPSerialHw.serial_port_read(self.ser, 300)
                if len(res_frame_list) != 0:
                    self.message_display_dt.Value += 'DOAP Receive Frame: '
                    self.message_display_dt.Value += DUMP_HEX(res_frame_list)
                    if baud_set == 1:
                        res_ack_frame_list, res_data_frame_list = DOAPFrame.Split_DOAP_Frame(res_frame_list)
                        res_decode_ack_code, res_decode_list = SlipProtocol.Decode_SlipProtocol(res_data_frame_list)
                    else:
                        res_decode_ack_code, res_decode_list = SlipProtocol.Decode_FE_CommProtocol(res_frame_list)
                    if res_decode_list:
                        if DOAPFrame.Check_DOAP_Ack_Frame(res_decode_ack_code):
                            self.reponse_flag = True
                            if baud_set == 1:
                                res_board_type = res_decode_list[0]
                                res_sub_idx = res_decode_list[3]
                                res_obj_idx = res_decode_list[5]
                                res_attr_idx = res_decode_list[7]
                                res_data_size = res_decode_list[8]
                                res_data = res_decode_list[9:res_data_size + 9]
                            else:
                                res_board_type = 0x01
                                res_sub_idx = res_decode_list[0]
                                res_obj_idx = res_decode_list[2]
                                res_attr_idx = res_decode_list[4]
                                res_data = res_decode_list[6:]
                                res_data_size = len(res_data)
                            # type_idx = self.response_frame_cfg_obj_type_ch.GetSelection()
                            str_data = "".join([str(data) for data in res_data])
                            if self.Check_if_type_select_valid(type_idx, res_data_size):
                                data_list = res_data
                                convert_str = self.Conver_Data_Object_By_Type(type_idx, data_list, res_board_type)
                                self.response_frame_cfg_obj_data_dt.Value = convert_str
                            else:
                                self.response_frame_cfg_obj_data_dt.Value = 'Object Can\'t Convert To This Type'
                                return
                            self.response_frame_cfg_command_dt.SetValue("Get Object")
                            self.response_frame_cfg_subidx_dt.SetValue(str(res_sub_idx))
                            self.response_frame_cfg_objidx_dt.SetValue(str(res_obj_idx))
                            if res_attr_idx == 0xFF:
                                res_attr_idx = -1
                            else:
                                pass
                            self.response_frame_cfg_attribute_idx_tc.SetValue(str(res_attr_idx))
                            self.response_frame_cfg_obj_size_dt.SetValue(str(res_data_size))
                            self.response_frame_cfg_obj_type_ch.SetSelection(type_idx)
                            self.message_display_dt.Value += 'Ack Received\n'
                            self.message_display_dt.Value += 'DOAP Response Frame:'
                            self.message_display_dt.Value += DUMP_HEX(res_frame_list)
                            self.message_display_dt.Value += 'DOAP Decode Response Frame:'
                            self.message_display_dt.Value += DUMP_HEX(res_decode_list)
                        elif DOAPFrame.Check_DOAP_Nak_Frame(res_decode_ack_code):
                            self.message_display_dt.Value += 'Nak Received\n'
                        else:
                            self.message_display_dt.Value += 'No Ack/Nak Received\n'
                else:
                    self.message_display_dt.Value += 'No Response Frame Received\n'
            else:
                self.message_display_dt.Value = 'Request parameter is not configured'
        else:
            req_sub_idx_str = self.request_frame_cfg_subidx_it.Value
            req_obj_idx_str = self.request_frame_cfg_objidx_it.Value
            req_board_idx_str = self.request_frame_cfg_obj_size_it.Value
            req_obj_type_idx = self.request_frame_cfg_obj_type_ch.GetSelection()
            self.response_frame_cfg_obj_type_ch.SetSelection(req_obj_type_idx)
            req_obj_data_str = self.request_frame_cfg_obj_data_it.Value
            req_attribute_str = self.request_frame_cfg_attribute_idx_tc.Value
            if req_sub_idx_str.isdigit() and req_obj_idx_str.isdigit() and req_board_idx_str.isdigit():
                req_data_list = self.Set_Request_Frame_Data_List(int(req_board_idx_str))

                baud_set = self.serial_port_baudrate_ch.GetSelection()
                if baud_set == 1:
                    data_length = 41
                    req_frame_list = DOAPFrame.Build_DOAP_Request_Frame(request_code_put_value, int(req_board_idx_str),
                                                                        int(req_sub_idx_str), int(req_obj_idx_str),
                                                                        int(req_attribute_str),
                                                                        data_length, req_data_list)
                    req_encode_list = SlipProtocol.Encode_SlipProtocol(req_frame_list)
                else:
                    data_length = len(req_data_list) + 8
                    req_frame_list = DOAPFrame.Build_FE_Client_Request_Frame(request_code_put_value,
                                                                             int(req_sub_idx_str), int(req_obj_idx_str),
                                                                             int(req_attribute_str), data_length,
                                                                             req_data_list)
                    req_encode_list = req_frame_list
                self.message_display_dt.Value = 'DOAP Request Frame: '
                self.message_display_dt.Value += DUMP_HEX(req_frame_list)
                self.message_display_dt.Value += 'DOAP Encode Request Frame: '
                self.message_display_dt.Value += DUMP_HEX(req_encode_list)
                DOAPSerialHw.serial_port_write(self.ser, req_encode_list)
                res_frame_list = DOAPSerialHw.serial_port_read(self.ser, 80)
                if len(res_frame_list) != 0:
                    self.message_display_dt.Value += 'DOAP Receive Frame: '
                    self.message_display_dt.Value += DUMP_HEX(res_frame_list)
                    if baud_set == 1:
                        res_ack_frame_list, res_data_frame_list = DOAPFrame.Split_DOAP_Frame(res_frame_list)
                        res_decode_ack_code, res_decode_list = SlipProtocol.Decode_SlipProtocol(res_data_frame_list)
                    else:
                        res_decode_ack_code, res_decode_list = SlipProtocol.Decode_FE_CommProtocol(res_frame_list)
                    if res_decode_list:
                        if DOAPFrame.Check_DOAP_Ack_Frame(res_decode_ack_code):
                            self.reponse_flag = True
                            if baud_set == 1:
                                res_board_type = res_decode_list[0]
                                res_sub_idx = res_decode_list[3]
                                res_obj_idx = res_decode_list[5]
                                res_attr_idx = res_decode_list[7]
                                res_data_size = res_decode_list[8]
                                res_data = res_decode_list[9:res_data_size + 9]
                            else:
                                res_board_type = 0x01
                                res_sub_idx = res_decode_list[0]
                                res_obj_idx = res_decode_list[2]
                                res_attr_idx = res_decode_list[4]
                                res_data = res_decode_list[6:]
                                res_data_size = len(res_data)
                            type_idx = self.response_frame_cfg_obj_type_ch.GetSelection()
                            str_data = "".join([str(data) for data in res_data])
                            if self.Check_if_type_select_valid(type_idx, res_data_size):
                                data_list = res_data
                                convert_str = self.Conver_Data_Object_By_Type(type_idx, data_list, res_board_type)
                                self.response_frame_cfg_obj_data_dt.Value = convert_str
                            else:
                                self.response_frame_cfg_obj_data_dt.Value = 'Object Can\'t Convert To This Type'
                                return
                            self.response_frame_cfg_command_dt.SetValue("Put Object")
                            self.response_frame_cfg_subidx_dt.SetValue(str(res_sub_idx))
                            self.response_frame_cfg_objidx_dt.SetValue(str(res_obj_idx))
                            if res_attr_idx == 0xFF:
                                res_attr_idx = -1
                            else:
                                pass
                            self.response_frame_cfg_attribute_idx_tc.SetValue(str(res_attr_idx))
                            self.response_frame_cfg_obj_size_dt.SetValue(str(res_data_size))
                            self.message_display_dt.Value += 'Ack Received\n'
                            self.message_display_dt.Value += 'DOAP Response Frame:'
                            self.message_display_dt.Value += DUMP_HEX(res_frame_list)
                            self.message_display_dt.Value += 'DOAP Decode Response Frame:'
                            self.message_display_dt.Value += DUMP_HEX(res_decode_list)
                        elif DOAPFrame.Check_DOAP_Nak_Frame(res_decode_ack_code):
                            self.message_display_dt.Value += 'Nak Received\n'
                        else:
                            self.message_display_dt.Value += 'No Ack/Nak Received\n'
                else:
                    self.message_display_dt.Value += 'No Response Framre Received\n'
            else:
                self.message_display_dt.Value = 'Request Parameter Is Not Configured'
        if not self.reponse_flag:
            self.Clear_DOAP_Response_Display()
        return

    def send_on_click(self, event):
        if self.ser and DOAPSerialHw.check_serial_port_connected(self.ser):
            self.DOAP_Get_Put_Object()
        else:
            self.message_display_dt.Value = 'Serial Port Isn\'t Connected'
        return

    def request_frame_cfg_command_selected(self, event):
        request_command = self.request_frame_cfg_command_ch.GetString(self.request_frame_cfg_command_ch.GetSelection())
        if request_command == 'Get Object':
            self.Request_parameter_inavailable()
        else:
            self.Request_parameter_available()
        return

    def request_frame_cfg_board_idx_reset(self, event):
        request_baudrate_selected = self.serial_port_baudrate_ch.GetString(self.serial_port_baudrate_ch.GetSelection())
        if request_baudrate_selected == "9600":
            self.request_frame_cfg_obj_size_it.SetValue('1')
            self.serial_port_parity_ch.SetSelection(0)
        else:
            self.serial_port_parity_ch.SetSelection(1)

    def request_frame_cfg_obj_type_selected(self, event):
        self.Set_Request_Obj_Size_By_Type()
        return

    def response_frame_cfg_obj_type_selected(self, event):
        type_idx = self.response_frame_cfg_obj_type_ch.GetSelection()
        obj_size = self.res_obj_size
        if self.Check_if_type_select_valid(type_idx, obj_size):
            data_list = self.res_decode_list[4:-2]
            # convert_str = self.Conver_Data_Object_By_Type(type_idx, data_list)
            # self.response_frame_cfg_obj_data_dt.Value = convert_str
        else:
            self.response_frame_cfg_obj_data_dt.Value = 'Object Can\'t Convert To This Type'
        return

    def moveup_response_parameter(self):
        self.request_frame_send_button_row = self.request_frame_cfg_row3
        self.sizer.SetItemPosition(self.request_frame_send_button, pos=(self.request_frame_send_button_row, 0))
        self.sizer.SetItemSpan(self.request_frame_send_button, span=(1, 6))

        self.reponse_frame_row = self.request_frame_send_button_row + 1
        self.sizer.SetItemPosition(self.response_frame_title_st, pos=(self.reponse_frame_row, 0))
        self.sizer.SetItemSpan(self.response_frame_title_st, span=(1, 6))

        self.response_frame_para_row1 = self.reponse_frame_row + 1
        self.sizer.SetItemPosition(self.response_frame_cfg_command_st, pos=(self.response_frame_para_row1, 0))
        self.sizer.SetItemPosition(self.response_frame_cfg_command_dt, pos=(self.response_frame_para_row1, 1))
        self.sizer.SetItemPosition(self.response_frame_cfg_subidx_st, pos=(self.response_frame_para_row1, 2))
        self.sizer.SetItemPosition(self.response_frame_cfg_subidx_dt, pos=(self.response_frame_para_row1, 3))
        self.sizer.SetItemPosition(self.response_frame_cfg_objidx_st, pos=(self.response_frame_para_row1, 4))
        self.sizer.SetItemPosition(self.response_frame_cfg_objidx_dt, pos=(self.response_frame_para_row1, 5))

        self.response_frame_para_row2 = self.response_frame_para_row1 + 1
        self.sizer.SetItemPosition(self.response_frame_cfg_attribute_idx_st, pos=(self.response_frame_para_row2, 0))
        self.sizer.SetItemPosition(self.response_frame_cfg_attribute_idx_tc, pos=(self.response_frame_para_row2, 1))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_size_st, pos=(self.response_frame_para_row2, 2))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_size_dt, pos=(self.response_frame_para_row2, 3))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_type_st, pos=(self.response_frame_para_row2, 4))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_type_ch, pos=(self.response_frame_para_row2, 5))

        self.response_frame_para_row3 = self.response_frame_para_row2 + 1
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_data_st, pos=(self.response_frame_para_row3, 0))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_data_dt, pos=(self.response_frame_para_row3, 1))
        self.sizer.SetItemSpan(self.response_frame_cfg_obj_data_dt, span=(self.response_frame_object_data_span_row, 5))

        self.message_display_row = self.response_frame_para_row3 + self.response_frame_object_data_span_row
        self.sizer.SetItemPosition(self.message_display_dt, pos=(self.message_display_row, 1))
        self.sizer.SetItemSpan(self.message_display_dt, span=(self.message_display_span_row, 6))
        return

    def movedown_response_parameter(self):
        self.request_frame_send_button_row = self.request_frame_cfg_row3 + self.request_frame_object_data_span_row

        self.reponse_frame_row = self.request_frame_send_button_row + 1

        self.response_frame_para_row1 = self.reponse_frame_row + 1

        self.response_frame_para_row2 = self.response_frame_para_row1 + 1

        self.response_frame_para_row3 = self.response_frame_para_row2 + 1

        self.message_display_row = self.response_frame_para_row3 + self.response_frame_object_data_span_row
        self.sizer.SetItemPosition(self.message_display_dt, pos=(self.message_display_row, 1))
        self.sizer.SetItemSpan(self.message_display_dt, span=(self.message_display_span_row, 6))

        self.sizer.SetItemPosition(self.response_frame_cfg_obj_data_st, pos=(self.response_frame_para_row3, 0))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_data_dt, pos=(self.response_frame_para_row3, 1))
        self.sizer.SetItemSpan(self.response_frame_cfg_obj_data_dt, span=(self.response_frame_object_data_span_row, 5))

        self.sizer.SetItemPosition(self.response_frame_cfg_attribute_idx_st, pos=(self.response_frame_para_row2, 0))
        self.sizer.SetItemPosition(self.response_frame_cfg_attribute_idx_tc, pos=(self.response_frame_para_row2, 1))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_size_st, pos=(self.response_frame_para_row2, 2))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_size_dt, pos=(self.response_frame_para_row2, 3))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_type_st, pos=(self.response_frame_para_row2, 4))
        self.sizer.SetItemPosition(self.response_frame_cfg_obj_type_ch, pos=(self.response_frame_para_row2, 5))

        self.sizer.SetItemPosition(self.response_frame_cfg_command_st, pos=(self.response_frame_para_row1, 0))
        self.sizer.SetItemPosition(self.response_frame_cfg_command_dt, pos=(self.response_frame_para_row1, 1))
        self.sizer.SetItemPosition(self.response_frame_cfg_subidx_st, pos=(self.response_frame_para_row1, 2))
        self.sizer.SetItemPosition(self.response_frame_cfg_subidx_dt, pos=(self.response_frame_para_row1, 3))
        self.sizer.SetItemPosition(self.response_frame_cfg_objidx_st, pos=(self.response_frame_para_row1, 4))
        self.sizer.SetItemPosition(self.response_frame_cfg_objidx_dt, pos=(self.response_frame_para_row1, 5))

        self.sizer.SetItemPosition(self.response_frame_title_st, pos=(self.reponse_frame_row, 0))
        self.sizer.SetItemSpan(self.response_frame_title_st, span=(1, 6))

        self.sizer.SetItemPosition(self.request_frame_send_button, pos=(self.request_frame_send_button_row, 0))
        self.sizer.SetItemSpan(self.request_frame_send_button, span=(1, 6))
        return

    def Request_parameter_inavailable(self):
        # self.sizer.Hide(self.request_frame_cfg_attribute_idx_st)
        # self.sizer.Hide(self.request_frame_cfg_attribute_idx_tc)
        # self.sizer.Hide(self.request_frame_cfg_obj_size_st)
        # self.sizer.Hide(self.request_frame_cfg_obj_size_it)
        self.sizer.Hide(self.request_frame_cfg_obj_type_st)
        self.sizer.Hide(self.request_frame_cfg_obj_type_ch)
        self.sizer.Hide(self.request_frame_cfg_obj_data_st)
        self.sizer.Hide(self.request_frame_cfg_obj_data_it)
        # self.sizer.Detach(self.request_frame_cfg_attribute_idx_st)
        # self.sizer.Detach(self.request_frame_cfg_attribute_idx_tc)
        # self.sizer.Detach(self.request_frame_cfg_obj_size_st)
        # self.sizer.Detach(self.request_frame_cfg_obj_size_it)
        self.sizer.Detach(self.request_frame_cfg_obj_type_st)
        self.sizer.Detach(self.request_frame_cfg_obj_type_ch)
        self.sizer.Detach(self.request_frame_cfg_obj_data_st)
        self.sizer.Detach(self.request_frame_cfg_obj_data_it)
        self.moveup_response_parameter()
        self.panel.Layout()
        return

    def Request_parameter_available(self):
        self.movedown_response_parameter()
        # self.sizer.Add(self.request_frame_cfg_attribute_idx_st, pos=(self.request_frame_cfg_row2, 0), border=10,
        #                flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        # self.sizer.Add(self.request_frame_cfg_attribute_idx_tc, pos=(self.request_frame_cfg_row2, 1), border=10,
        #                flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        # self.sizer.Add(self.request_frame_cfg_obj_size_st, pos=(self.request_frame_cfg_row2, 2), border=10,
        #                flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        # self.sizer.Add(self.request_frame_cfg_obj_size_it, pos=(self.request_frame_cfg_row2, 3), border=10,
        #                flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        self.sizer.Add(self.request_frame_cfg_obj_type_st, pos=(self.request_frame_cfg_row2, 4), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        self.sizer.Add(self.request_frame_cfg_obj_type_ch, pos=(self.request_frame_cfg_row2, 5), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        self.sizer.Add(self.request_frame_cfg_obj_data_st, pos=(self.request_frame_cfg_row3, 0), border=10,
                       flag=wx.ALL | wx.EXPAND | wx.ALIGN_LEFT)
        self.sizer.Add(self.request_frame_cfg_obj_data_it, pos=(self.request_frame_cfg_row3, 1),
                       span=(self.request_frame_object_data_span_row, 5), border=10, flag=wx.ALL | wx.EXPAND)
        # self.sizer.Show(self.request_frame_cfg_attribute_idx_st)
        # self.sizer.Show(self.request_frame_cfg_attribute_idx_tc)
        self.sizer.Show(self.request_frame_cfg_obj_size_it)
        self.sizer.Show(self.request_frame_cfg_obj_size_st)
        self.sizer.Show(self.request_frame_cfg_obj_size_it)
        self.sizer.Show(self.request_frame_cfg_obj_type_st)
        self.sizer.Show(self.request_frame_cfg_obj_type_ch)
        self.sizer.Show(self.request_frame_cfg_obj_data_st)
        self.sizer.Show(self.request_frame_cfg_obj_data_it)
        self.panel.Layout()
        self.panel.Fit()  # 2021.03.13, added to fix the abnormal display for frame data when "put object" mode enabled
        return

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Instruction\tCtrl-H",
                                    "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Now a help menu for the about item
        waveformMenu = wx.Menu()
        waveformItem = waveformMenu.Append(-1, "&Waveform\tCtrl-W")
        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")
        menuBar.Append(waveformMenu, "&Waveform")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnWaveform, waveformItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("1. Detect button to detect current serial port.\n\
2. Connect button to connect serial port, button change green means connected\n\
3. Send button to send LMT request frame\n\
4. Get object will auto detect most possible type", caption='LMT PC Tools Instruction\n')

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox('Version: 1.0.0\n\
Author: ABB Firmware\n\
Date: 2021/03/13\n\
Email: panpan.zhang@cn.abb.com', "About LMT PC Tools", wx.OK | wx.ICON_INFORMATION)

    def OnWaveform(self, event):
        dialog = wx.MessageDialog(self, 'Not support now！', 'warning', style=wx.OK | wx.CENTER | wx.ICON_ERROR)
        dialog.ShowModal()


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = DOAP_PC_TOOL_FRAME(None, title='LMT PC Tool v0.0.3')
    frm.SetSize(730, 900)
    frm.Show()
    app.MainLoop()
