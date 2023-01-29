# -*- coding: utf-8 -*-
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from pylab import *
from matplotlib.widgets import Button
from kneed import KneeLocator

running_dict = {
    '0': 'init',
    '1': '首出水',
    '2': '常温',
    '3': '强抽',
    '4': '预热',
    '5': '加热',
    '6': '反向',
    '7': '保护',
}

b_cur_pwm0 = [0] * 500
b_cur_temp1 = [0] * 500
b_cur_temp0 = [0] * 500
b_target_temp0 = [0] * 500
b_target_temp1 = [0] * 500
b_cur_pwm1 = [0] * 500
b_cur_temp2 = [0] * 500
b_target_temp2 = [0] * 500
b_cur_pwm2 = [0] * 500

b_motor_tarangle = [0] * 500


sample_time = np.arange(500)
is_play = True
update_data_flag = True
counter = 0


# def update_data(vm, pwm, cur1, cur2, speed1, speed2, cur_hall1, cur_hall2, axis_x, axis_y, axis_z, temp, error_code1):
def update_data(cur_temp0, target_temp0, cur_pwm0, cur_temp1, target_temp1, cur_pwm1, cur_temp2, target_temp2, cur_pwm2, motor_tarangle):
    global update_data_flag
    global counter
    global error_code

    b_cur_temp0.pop(0)
    b_cur_temp0.append(cur_temp0/100)
    b_target_temp0.pop(0)
    b_target_temp0.append(target_temp0)
    b_cur_pwm0.pop(0)
    b_cur_pwm0.append(cur_pwm0)

    b_cur_temp1.pop(0)
    b_cur_temp1.append(cur_temp1/100)
    b_target_temp1.pop(0)
    b_target_temp1.append(target_temp1)
    b_cur_pwm1.pop(0)
    b_cur_pwm1.append(cur_pwm1)

    b_cur_temp2.pop(0)
    b_cur_temp2.append(cur_temp2/100)
    b_target_temp2.pop(0)
    b_target_temp2.append(target_temp2)
    b_cur_pwm2.pop(0)
    b_cur_pwm2.append(cur_pwm2)

    b_motor_tarangle.pop(0)
    b_motor_tarangle.append(motor_tarangle)

    update_data_flag = True
    counter += 1


"""完成拟合曲线参数计算"""


def liner_fitting(data_y):

    data_x = [1, 2, 3, 4, 5, 6]
    size = len(data_x)
    i = 0
    sum_xy = 0
    sum_y = 0
    sum_x = 0
    sum_sqare_x = 0
    average_x = 0
    average_y = 0
    while i < size:
        sum_xy += data_x[i]*data_y[i]
        sum_y += data_y[i]
        sum_x += data_x[i]
        sum_sqare_x += data_x[i]*data_x[i]
        i += 1
    average_x = sum_x/size
    average_y = sum_y/size
    return_k = (size*sum_xy-sum_x*sum_y)*20/(size*sum_sqare_x-sum_x*sum_x)
    return_b = average_y-average_x*return_k
    print(return_k)
    return return_k


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
    global error_code

    rc('mathtext', default='regular')
    mpl.rcParams['font.sans-serif'] = ['SimHei']  # 添加这条可以让图形显示中文
    # 解决保存图像是负号‘-’显示为方块的问题 作者：GXTon https://www.bilibili.com/read/cv12112253 出处：bilibili
    mpl.rcParams['axes.unicode_minus'] = False
    plt.ion()  # 开启interactive mode 成功的关键函数
    figID = "app 参数"
    fig = plt.figure(figID)
    cid_press = fig.canvas.mpl_connect('button_press_event', onpress)
    counter = 0

    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)
    # ax4 = fig.add_subplot(224)
    # ax31 = ax3.twinx()
    # ax21 = ax2.twinx()

    lns1 = ax1.plot(sample_time, b_cur_pwm0, '-y', label='当前PWM')
    lns2 = ax1.plot(sample_time, b_target_temp0, '-b', label='设置水温')
    lns3 = ax1.plot(sample_time, b_cur_temp0, '-r', label='当前水温')

    lns4 = ax2.plot(sample_time, b_cur_temp1, '-r', label='当前风温')
    lns5 = ax2.plot(sample_time, b_target_temp1, '-b', label='设置风温')
    lns6 = ax2.plot(sample_time, b_cur_pwm1, '-y', label='当前PWM')

    lns7 = ax3.plot(sample_time, b_cur_temp2, '-r', label='当前座温')
    lns8 = ax3.plot(sample_time, b_target_temp2, '-b', label='设置座温')
    lns9 = ax3.plot(sample_time, b_cur_pwm2, '-y', label='当前PWM')

    ax1.yaxis.set_ticks([0, 20, 40, 60, 80, 100])
    ax1.grid(linestyle=":", axis="both")
    ax1.set_ylabel(r"水温/PWM")
    ax1.set_ylim(0, 110)

    ax2.yaxis.set_ticks([0, 20, 40, 60, 80, 100])
    ax2.grid(linestyle=":", axis="both")
    ax2.set_ylabel(r"风温/PWM")
    ax2.set_ylim(0, 110)

    ax3.yaxis.set_ticks([0, 20, 40, 60, 80, 100])
    ax3.grid(linestyle=":", axis="both")
    ax3.set_ylabel(r"座温/PWM")
    ax3.set_ylim(0, 110)

    # added these lines
    lns = lns1+lns2+lns3
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=2)

    lns = lns4+lns5+lns6
    labs = [l.get_label() for l in lns]
    ax2.legend(lns, labs, loc=2)

    lns = lns7+lns8+lns9
    labs = [l.get_label() for l in lns]
    ax3.legend(lns, labs, loc=2)

    plt.show()
    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")

    # 以●绘制最大值点的位置
    y1_max = np.argmax(b_cur_temp0)
    ax11_plot, = ax1.plot(y1_max, b_cur_temp0[y1_max], 'ko')
    show_max = '['+str(b_cur_temp0[y1_max])+']'
    annotate1 = ax1.annotate(show_max, xy=(
        y1_max, b_cur_temp0[y1_max]), xytext=(y1_max, b_cur_temp0[y1_max]))

    y1_max = np.argmax(b_cur_temp1)
    ax21_plot, = ax2.plot(y1_max, b_cur_temp1[y1_max], 'ko')
    show_max = '['+str(b_cur_temp1[y1_max])+']'
    annotate2 = ax2.annotate(show_max, xy=(
        y1_max, b_cur_temp1[y1_max]), xytext=(y1_max, b_cur_temp1[y1_max]))

    y1_max = np.argmax(b_cur_temp2)
    ax31_plot, = ax3.plot(y1_max, b_cur_temp2[y1_max], 'ko')
    show_max = '['+str(b_cur_temp2[y1_max])+']'
    annotate3 = ax1.annotate(show_max, xy=(
        y1_max, b_cur_temp2[y1_max]), xytext=(y1_max, b_cur_temp2[y1_max]))

    y1_max = np.argmax(b_cur_temp0)
    ax12_plot, = ax1.plot(y1_max, b_cur_temp0[y1_max], 'k^')

    y1_max = np.argmax(b_cur_temp1)
    ax22_plot, = ax2.plot(y1_max, b_cur_temp1[y1_max], 'k^')


    while(True):
        if not plt.fignum_exists(figID):
            break

        # counter = counter + 1

        if(is_play is True):
            # plt.clf()
            ax1.lines[0].set_data(sample_time, b_cur_pwm0)  # set plot data
            ax1.lines[1].set_data(sample_time, b_target_temp0)  # set plot data
            ax1.lines[2].set_data(sample_time, b_cur_temp0)  # set plot data
            ax1.relim()                  # recompute the data limits
            ax1.autoscale_view()         # automatic axis scaling

            ax1.set_xlabel("target temp:" + '{:d}'.format(b_target_temp0[-1]) + ' diff:' + '{:.2f}'.format(b_cur_temp0[-1] - b_target_temp0[-1]))

            ax2.lines[2].set_data(sample_time, b_cur_pwm1)  # set plot data
            ax2.lines[0].set_data(sample_time, b_cur_temp1)  # set plot data
            ax2.lines[1].set_data(sample_time, b_target_temp1)  # set plot data
            
            ax2.relim()                  # recompute the data limits
            ax2.autoscale_view()         # automatic axis scaling

            ax2.set_xlabel("target temp:" + '{:d}'.format(b_target_temp1[-1]) + ' diff:' + '{:.2f}'.format(b_cur_temp1[-1] - b_target_temp1[-1]))

            # ax21.lines[0].set_data(sample_time, b_cur_temp1)  # set plot data
            # ax21.relim()                  # recompute the data limits
            # ax21.autoscale_view()         # automatic axis scaling

            ax3.lines[0].set_data(sample_time, b_cur_temp2)  # set plot data
            ax3.lines[1].set_data(sample_time, b_target_temp2)  # set plot data
            ax3.lines[2].set_data(sample_time, b_cur_pwm2)  # set plot data
            ax3.relim()                  # recompute the data limits
            ax3.autoscale_view()         # automatic axis scaling

            ax3.set_xlabel("target temp:" + '{:d}'.format(b_target_temp2[-1]) + ' diff:' + '{:.2f}'.format(b_cur_temp2[-1] - b_target_temp2[-1]) + ' time:' + '{:d}'.format(counter))

            # 以●绘制最大值点的位置
            y1_max = np.argmax(b_cur_temp0)
            ax11_plot.set_data(y1_max, b_cur_temp0[y1_max])
            show_max = '['+str(b_cur_temp0[y1_max])+']'
            annotate1.remove()
            annotate1 = ax1.annotate(show_max, xy=(
                y1_max, b_cur_temp0[y1_max]), xytext=(y1_max, b_cur_temp0[y1_max]))

            
            # 状态发生变化
            tarangle_prev = b_motor_tarangle[-2]
            tarangle = b_motor_tarangle[-1]
            for i in range(len(b_motor_tarangle) - 1):
                tarangle = b_motor_tarangle[i]
                if(tarangle != tarangle_prev and tarangle > 200):
                    ax12_plot.set_data(i,b_cur_temp0[i])
                    ax22_plot.set_data(i,b_cur_temp1[i])
                tarangle_prev = tarangle

            y1_max = np.argmax(b_cur_temp1)
            ax21_plot.set_data(y1_max, b_cur_temp1[y1_max])
            show_max = '['+str(b_cur_temp1[y1_max])+']'
            annotate2.remove()
            annotate2 = ax2.annotate(show_max, xy=(
                y1_max, b_cur_temp1[y1_max]), xytext=(y1_max, b_cur_temp1[y1_max]))

            y1_max = np.argmax(b_cur_temp2)
            ax31_plot.set_data(y1_max, b_cur_temp2[y1_max])
            show_max = '['+str(b_cur_temp2[y1_max])+']'
            annotate3.remove()
            annotate3 = ax3.annotate(show_max, xy=(
                y1_max, b_cur_temp2[y1_max]), xytext=(y1_max, b_cur_temp2[y1_max]))

        # update the plot and take care of window events (like resizing etc.)
        fig.canvas.flush_events()
        time.sleep(0.01)               # wait for next loop iteration

        update_data_flag = False


if __name__ == '__main__':
    i = 0
    while i < 500:
        b_cur_temp0.pop(0)
        b_cur_temp0.append(i/10)
        b_target_temp0.pop(0)
        b_target_temp0.append(i/20)
        b_cur_pwm0.pop(0)
        b_cur_pwm0.append(i/30)

        b_cur_temp1.pop(0)
        b_cur_temp1.append(i/10)

        b_cur_temp2.pop(0)
        b_cur_temp2.append(50 - i/30)

        i = i + 1

    update_picture()
