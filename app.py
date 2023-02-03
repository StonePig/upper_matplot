# -*- coding: utf-8 -*- 

import wx
# 导入modbus_win.py中内容
import serial_app_win
import win32api,win32con
from tkinter.filedialog import askdirectory
import time
from serial.tools import list_ports
import serial
import numpy as np
import _thread
import threading
import os
import sys
import configparser
import struct

import re

from plt4temp import *

from multiprocessing import Process
import tkinter as tk
from tkinter import filedialog

endian_str = "big"

heat_dict = {
    '预热': 'PRE_HEAT',
    '水温': 'WATER_HEAT',
    '风温': 'WIND_HEAT',
    '座温': 'SEAT_HEAT',
}

# 创建mainWin类并传入modbus_win.MyFrame1
class mainWin(serial_app_win.serialApp):
	port_opened = False

	def init(self):

		ret1 = re.findall('\d+', "Content length:1000;Package Length:1234;")

		str_ = "Content length:1000;Package Length:1234;"
		number = re.findall("\d+",str_)    # 输出结果为列表
		print(number)


		self.init_done = True

		self.config = configparser.ConfigParser()
		print(os.getcwd())
		self.cfg_file = os.path.join(os.getcwd(), 'config.ini')
		self.config.read(self.cfg_file)

		os.system("mkdir log")
		
		self.baudrate = self.config.get('DEFAULT', 'baud')
		if self.baudrate in self.m_comboBox_Baud.GetItems():
			self.m_comboBox_Baud.SetSelection(self.m_comboBox_Baud.FindString(self.baudrate, False))
		else:
			self.baudrate = "9600"
			print("配置文件错误：不支持的波特率")
			win32api.MessageBox(0, "配置文件错误：不支持的波特率", "提醒",win32con.MB_ICONWARNING)
			self.init_done = False

		self.heat = 'PRE_HEAT'
		self.kp = self.config.get(self.heat, 'kp')
		self.ki = self.config.get(self.heat, 'ki')
		self.kd = self.config.get(self.heat, 'kd')
		self.pwm_min = self.config.get(self.heat, 'pwm_min')
		self.pwm_max = self.config.get(self.heat, 'pwm_max')
		
		self.m_textCtrl_kp.SetValue(self.kp)
		self.m_textCtrl_ki.SetValue(self.ki)
		self.m_textCtrl_kd.SetValue(self.kd)
		self.m_textCtrl_pwm_min.SetValue(self.pwm_min)
		self.m_textCtrl_pwm_max.SetValue(self.pwm_max)

		# self.m_comboBox_temp.SetSelection(0)


		port_list = list(list_ports.comports())
		num = len(port_list)
		if num <= 0:
			print("找不到任何串口设备")
			# win32api.MessageBox(0, "找不到任何串口设备", "提醒",win32con.MB_ICONWARNING)
			self.init_done = False
		else:
			port_items = []
			for i in range(num):
				# 将 ListPortInfo 对象转化为 list
				port = list(port_list[i])
				port_items.append(port[0]) 
				print(port_list)
				print(port_list[i])
				print(port)
				print(port_items)

			self.m_comboBox_Port.Set(port_items)
			self.port = self.config.get('DEFAULT', 'port')
			if self.port in self.m_comboBox_Port.GetItems():
				self.m_comboBox_Port.SetSelection(self.m_comboBox_Port.FindString(self.port, False))
			else:
				self.m_comboBox_Port.SetSelection(0)

			self.port = self.m_comboBox_Port.GetValue()


	def send_to_slave_timer(self, event ):
		pass
			
	def PortSelectNewVaule( self, event ):
		print(self.m_comboBox_Port.GetValue())
		self.port = self.m_comboBox_Port.GetValue()
		self.config.set('DEFAULT', 'port', self.port)
	
	def BaudSelectNewVaule( self, event ):
		print(self.m_comboBox_Baud.GetValue())
		self.baudrate = self.m_comboBox_Baud.GetValue()
		self.config.set('DEFAULT', 'baud', self.baudrate)

	def recv(self, com):
		data = b''
		print("recv thread start")

		# file_name = "log/record_" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".csv"
		# with open(file_name, 'w', encoding='utf-8') as fo:
			# fo.write('time,water temp,set temp,pwm,wind temp,set temp,pwm,seat temp,set temp,pwm,motor tarangle' + '\n')
		content = []
		line = 0
		length = 1000
		while (self.port_opened):
			time.sleep(0.001)
			try:
				n = com.inWaiting()
				if n:
					data = data + com.read(n)
					# print(len(data))
					if(len(data) > length):
						update_data(data[:length])
						# print(data[:length])
						data = data[length:]
					
					# data = b''

			except Exception as exc:
				# fo.write(''.join(content))
				return
			# fo.write(''.join(content))

		return

	
	def PortOpen( self, event ):
		if(self.init_done == False):
			return

		if(self.port_opened == False):	
			self.m_button_port_open.SetLabel("关闭")
			try:
				self.com = serial.Serial(port=self.port,baudrate=self.baudrate, bytesize=8, parity='N', stopbits=1)
			except Exception as exc:
				win32api.MessageBox(0, "串口打开失败", "提醒",win32con.MB_ICONWARNING)
				return
			if self.com.isOpen() :
				self.port_opened = True
				print("open success")
				# _thread.start_new_thread(update_picture, ())
				_thread.start_new_thread(self.recv, (self.com,))
				update_picture()
			else :
				print("open failed")
				win32api.MessageBox(0, "串口打开失败", "提醒",win32con.MB_ICONWARNING)
				return
		
			self.m_comboBox_Port.Disable()
			self.m_comboBox_Baud.Disable()
			
			with open(self.cfg_file, 'w', encoding='utf-8') as configfile:
				self.config.write(configfile)
	
			# p_one = Process(target=self.recv)
			# p_one.start()

		else:
			self.port_opened = False
			self.m_button_port_open.SetLabel("打开")
			# serial.Serial.close(self)
			self.com.close()
			self.m_comboBox_Port.Enable()
			self.m_comboBox_Baud.Enable()

	def readfile(self):
		'''打开选择文件夹对话框'''
		root = tk.Tk()
		root.withdraw()
		Filepath = filedialog.askopenfilename() #获得选择好的文件
		print('Filepath:',Filepath)
		parm = [0] * 50
		# update_picture()

		with open(Filepath, 'r', encoding='utf-8') as f:
			line = f.readline()
			while self.openfile:
				line = f.readline()
				if(line):
					try:
						for i in range(9):
							if(line.split(",")[i+1].lstrip('-').isdigit()):
								parm[i] = int(line.split(",")[i+1])

					except Exception as exc:
						for i in range(9):
							parm[i] = 0
					
					update_data(parm[0], parm[1], parm[2], parm[3], parm[4], parm[5], parm[6], parm[7], parm[8])
					# update_data(vm, pwm, cur1, cur2, speed1, speed2, hall1_plus, hall2_plus, axis_x, axis_y, axis_z, temp, error_code)
									
					
					# print(cur2, temp)
				else:
					break
				time.sleep(0.01)
		root.mainloop()

	def m_button_openOnButtonClick( self, event ):
		self.openfile = False
		time.sleep(0.5)
		self.openfile = True
		_thread.start_new_thread(self.readfile, ())
		update_picture()

	def m_comboBox_tempOnCombobox( self, event ):	
		self.heat = heat_dict[self.m_comboBox_temp.GetValue()]

		self.kp = self.config.get(self.heat, 'kp')
		self.ki = self.config.get(self.heat, 'ki')
		self.kd = self.config.get(self.heat, 'kd')
		self.pwm_min = self.config.get(self.heat, 'pwm_min')
		self.pwm_max = self.config.get(self.heat, 'pwm_max')
		
		self.m_textCtrl_kp.SetValue(self.kp)
		self.m_textCtrl_ki.SetValue(self.ki)
		self.m_textCtrl_kd.SetValue(self.kd)
		self.m_textCtrl_pwm_min.SetValue(self.pwm_min)
		self.m_textCtrl_pwm_max.SetValue(self.pwm_max)



	def OnsettingButtonClick( self, event ):
		if (self.port_opened):

			self.heat = heat_dict[self.m_comboBox_temp.GetValue()]

			self.config.set(self.heat, "kp", self.m_textCtrl_kp.GetValue())
			self.config.set(self.heat, "ki", self.m_textCtrl_ki.GetValue())
			self.config.set(self.heat, "kd", self.m_textCtrl_kd.GetValue())
			self.config.set(self.heat, "pwm_min", self.m_textCtrl_pwm_min.GetValue())
			self.config.set(self.heat, "pwm_max", self.m_textCtrl_pwm_max.GetValue())

			with open(self.cfg_file, 'w', encoding='utf-8') as configfile:
				self.config.write(configfile)

			sendbuf = b''
			# sel = self.m_comboBox_temp.GetSelection()

			sendbuf += int(0xA5).to_bytes(1,endian_str)
			sendbuf += int(56).to_bytes(1,endian_str)

			for i in heat_dict:
				self.heat = heat_dict[i]
				self.kp = self.config.get(self.heat, 'kp')
				self.ki = self.config.get(self.heat, 'ki')
				self.kd = self.config.get(self.heat, 'kd')
				self.pwm_min = self.config.get(self.heat, 'pwm_min')
				self.pwm_max = self.config.get(self.heat, 'pwm_max')

				sendbuf += struct.pack('>f', float(self.kp))
				sendbuf += struct.pack('>f', float(self.ki))
				sendbuf += struct.pack('>f', float(self.kd))
				sendbuf += int(self.pwm_min).to_bytes(1, endian_str)
				sendbuf += int(self.pwm_max).to_bytes(1, endian_str)

			sendbuf += int(0x5A).to_bytes(1,endian_str)
			print(sendbuf)

			self.com.write(sendbuf)
			# win32api.MessageBox(0, "设置成功", "提醒",win32con.MB_ICONWARNING)

		else:
			win32api.MessageBox(0, "串口未打开", "提醒",win32con.MB_ICONWARNING)


b_ave = [0] * 1000000

if __name__ == '__main__':
	# 下面是使用wxPython的固定用法
	# 读取文件，文件绝对地址"D:\Project\arpatest01\foo.arpa"
	# dat = np.fromfile("E:\\bat.bin", dtype=np.uint8)
	# print(dat.shape)# 打印二进制文件形状
	# file_size = dat.size
	# num = file_size
	# record_num = file_size//4
	# step = int(num / 10) // 4 * 4
	# ave = dat[0]*256+dat[1]
	# for i in range(record_num):
	# 	ave = (ave*19 + dat[i*4] * 256 + dat[i*4+1])//20
	# 	b_ave[i*4] = ave // 256
	# 	b_ave[i*4+1] = ave % 256

	# for i in range(11):
	# 	bat_value = b_ave[i*step] * 256 + b_ave[i*step+1]
	# 	print(bat_value)

	app = wx.App()
	main_win = mainWin(None)
	main_win.Show()
	main_win.init()
	app.MainLoop()