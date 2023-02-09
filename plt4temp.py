# -*- coding: utf-8 -*-
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from pylab import *
from matplotlib.widgets import Button
from kneed import KneeLocator
from scipy.interpolate import interp1d
import pylab as pl

from numpy.fft import rfft, rfftfreq

def make_spectrum(ys, framerate):
    # 波形采样数
    n = len(ys)
    # 样本采样频率倒数，也即样本间时间差
    d = 1/framerate
    # 返回各个频率元素的倍数振幅和相位差 复数形式，可以理解为振幅和角度的向量
    hs = rfft(ys)
    # 返回包含对应hs各元素的频率数组,采样率的一半 11025/2
    fs = rfftfreq(n, d)
    return hs,fs


b_cur_level = [0] * 1000
b_backup = [0] * 1000
sample_time = np.arange(1000)
is_play = True
update_data_flag = True
counter = 0
zoom_scale = 5
zoom_value = [0.05, 0.1, 0.125, 0.25, 0.5, 1, 1.25, 2.5, 5, 10, 12.5, 25, 50, 100]
is_zoomed = True
is_updated = False
move_step = 0


def update_data(data):
    global update_data_flag
    global counter
    global sample_time
    global b_backup

    if(is_play == False):
        return

    update_data_flag = True

    # sample_time1 = np.arange(len(data))
    # #将原始序列分成多段,用一次函数拟合为函数f1和用三次函数拟合为函数f2
    # f1=interp1d(sample_time1,data,kind='linear')
    # # f2=interp1d(sample_time,data,kind='cubic')
   
    
    # #在原区间内均匀选取30个点,因为要插值到长度30.
    # x_pred=np.linspace(0,len(data),num=len(data))
    
    
    # #用函数f1求出插值的30个点对应的值
    # y1=f1(x_pred)

    # print(len(data))

    for i in range(len(data)):
        b_cur_level.pop(0)
        b_cur_level.append(data[i] * 5000 / 256)
    b_backup = b_cur_level.copy()
    counter += 1


def func(event):
    print("button clicked!")


def onpress(event):
    global is_play
    if(is_play is True):
        is_play = False
    else:
        is_play = True


def update_picture():
    global is_play
    global update_data_flag
    global counter
    global zoom_scale
    global is_zoomed
    global is_updated
    global b_backup
    global move_step
    global b_cur_level
    global sample_time

    rc('mathtext', default='regular')
    mpl.rcParams['font.sans-serif'] = ['SimHei']  # 添加这条可以让图形显示中文
    # 解决保存图像是负号‘-’显示为方块的问题 作者：GXTon https://www.bilibili.com/read/cv12112253 出处：bilibili
    mpl.rcParams['axes.unicode_minus'] = False

    plt.ion()  # 开启interactive mode 成功的关键函数
    figID = "app 参数"
    fig = plt.figure(figID)
    # cid_press = fig.canvas.mpl_connect('button_press_event', onpress)
    counter = 0

    ax1 = fig.add_subplot(111)
    

    ample_time1 = np.arange(len(b_cur_level))
    lns1 = ax1.plot(ample_time1, b_cur_level, '-b', label='level')


    ax1.yaxis.set_ticks([-5000, -4000, -3000, -2000, -1000, 0, 1000, 2000, 3000, 4000, 5000])
    ax1.xaxis.set_ticks([0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
    ax1.grid(linestyle="-.", axis="both")
    ax1.set_ylabel(r"")
    ax1.set_ylim(-10000, 10000)

    ax1.axes.xaxis.set_ticklabels([])



    # added these lines
    # lns = lns1
    # labs = [l.get_label() for l in lns]
    # ax1.legend(lns, labs, loc=2)

    buttonaxe = plt.axes([0.62, 0.03, 0.04, 0.04])
    button_pause = Button(buttonaxe, 'start\n/stop',color='khaki', hovercolor='yellow')
    button_pause.on_clicked(Button_handlers().pause)

    buttonaxe = plt.axes([0.70, 0.03, 0.04, 0.04])
    button_move1 = Button(buttonaxe, '左移',color='khaki', hovercolor='yellow')
    button_move1.on_clicked(Button_handlers().move_left)

    buttonaxe = plt.axes([0.76, 0.03, 0.04, 0.04])
    button_move2 = Button(buttonaxe, '右移',color='khaki', hovercolor='yellow')
    button_move2.on_clicked(Button_handlers().move_right)


    buttonaxe = plt.axes([0.84, 0.03, 0.04, 0.04])
    button1 = Button(buttonaxe, '放大',color='khaki', hovercolor='yellow')
    button1.on_clicked(Button_handlers().zoom_in)

    buttonaxe2 = plt.axes([0.90, 0.03, 0.04, 0.04])
    button2 = Button(buttonaxe2, '缩小',color='khaki', hovercolor='yellow')
    button2.on_clicked(Button_handlers().zoom_out)

    plt.show()
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")  


    while(True):
        if not plt.fignum_exists(figID):
            break

        # counter = counter + 1

        if(is_updated):
            b_cur_level = b_backup.copy()
            # if(len(b_cur_level) > 1000):
            #     step = int(5 * len(b_cur_level) / 1000)
            # else:
            step = int(5 * zoom_value[zoom_scale])

            if(step < 1):
                step = 1

            if(move_step > 0):
                for i in range(int(step * move_step)):
                    b_cur_level.pop(-1)
                    b_cur_level.insert(0, b_cur_level[0])
            elif(move_step < 0):
                for i in range(int(step * (0-move_step))):
                    b_cur_level.pop(0)
                    b_cur_level.append(b_cur_level[-1])

        if(is_play is True or is_updated is True):
            is_updated = False
            # plt.clf()
            sample_time1 = np.arange(len(b_cur_level))
            # print(len(sample_time1), len(b_cur_level))
            ax1.lines[0].set_data(sample_time1, b_cur_level)  # set plot data
            # ax1.relim()                  # recompute the data limits
            ax1.autoscale_view()         # automatic axis scaling

            m_time = zoom_value[zoom_scale] * 2000

            if(m_time >= 1000):
                m_disp = '{:.2f}'.format(m_time / 1000) + 'ms'
            else:
                m_disp = '{:.0f}'.format(m_time) + 'us'
            
            ax1.set_xlabel('{:.2f}'.format(b_cur_level[-1] / 1000) + "V," + " M:" + m_disp)



        # update the plot and take care of window events (like resizing etc.)
        fig.canvas.flush_events()
        time.sleep(0.1)               # wait for next loop iteration

        if(is_zoomed == True):           
            if(is_play == True):
                b_cur_level.clear()
                if(zoom_value[zoom_scale] >= 1):
                    b_cur_level = [0] * int(zoom_value[zoom_scale] * 1000)
                else:
                    b_cur_level = [0] * int(1 * 1000)
                # if(is_play == False):
                #     b_cur_level = b_backup[:min(len(b_backup), len(b_cur_level))]
                b_backup.clear()
                b_backup = [0] * int(zoom_value[zoom_scale] * 1000)
                b_backup = b_cur_level.copy()
                        
            ax1.set_xlim(0, 1000 * zoom_value[zoom_scale])
            ax1.xaxis.set_ticks([0, 100 * zoom_value[zoom_scale], 200 * zoom_value[zoom_scale], 300 * zoom_value[zoom_scale], 400 * zoom_value[zoom_scale], 500 * zoom_value[zoom_scale], 600 * zoom_value[zoom_scale], 700 * zoom_value[zoom_scale], 800 * zoom_value[zoom_scale], 900 * zoom_value[zoom_scale], 1000 * zoom_value[zoom_scale]])
            
            is_updated = True
        is_zoomed = False
        update_data_flag = False

class Button_handlers():
    def zoom_in(self, event):
        global zoom_scale
        global is_play
        global is_zoomed
        global b_cur_level        
        global b_backup

        # is_play = False
        
        if(zoom_scale > 0):
            zoom_scale = zoom_scale - 1
            is_zoomed = True
            # if(zoom_value[zoom_scale] > 1):
            #     b_cur_level.clear()
            #     b_cur_level = [0] * int(zoom_value[zoom_scale] * 1000)
            #     if(is_play == False):
            #         b_cur_level = b_backup[:len(b_cur_level)]
            #     b_backup.clear()
            #     b_backup = [0] * int(zoom_value[zoom_scale] * 1000)
            #     b_backup = b_cur_level.copy()


        # is_play = True
        print(zoom_scale)
    def zoom_out(self, event):
        global zoom_scale
        global is_play
        global b_cur_level
        global is_zoomed
        global b_backup

        # is_play = False

        if(zoom_scale < len(zoom_value) - 1):
            zoom_scale = zoom_scale + 1
            is_zoomed = True
            # if(zoom_value[zoom_scale] > 1):
            #     b_cur_level.clear()
            #     b_cur_level = [0] * int(zoom_value[zoom_scale] * 1000)
            #     if(is_play == False):
            #         b_cur_level = b_backup[:len(b_backup)]
            #     b_backup.clear()
            #     b_backup = [0] * int(zoom_value[zoom_scale] * 1000)
            #     b_backup = b_cur_level.copy()

        # is_play = True
        print(zoom_scale)

    def move_left(self, event):
        global b_cur_level 
        global is_updated
        global b_backup
        global move_step

        if(is_play == True):
            return
        
        move_step = move_step - 1
        is_updated = True

    def move_right(self, event):
        global b_cur_level 
        global is_updated
        global b_backup
        global move_step

        if(is_play == True):
            return
        
        move_step = move_step + 1
        is_updated = True

    def pause(self, event):
        global is_play
        global move_step
        global b_cur_level
        global b_backup        

        move_step = 0
        if(is_play is True):
            is_play = False
        else:
            b_cur_level = [0] * int(zoom_value[zoom_scale] * 1000)
            b_backup = b_cur_level.copy()
            is_play = True

if __name__ == '__main__':
    # i = 0
    # while i < 1000:
    #     b_cur_level.pop(0)
    #     b_cur_level.append(i/10)
    #     i = i + 1

    update_picture()
