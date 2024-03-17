import machine
import utime


uart = machine.UART(0, baudrate=9600)

buttons = [machine.Pin(i, machine.Pin.IN, machine.Pin.PULL_DOWN) for i in range(2, 6)]  # GP2 bis GP5

def send_button_data():
    data = bytearray(4)
    for i in range(4):
        data[i] = buttons[i].value()
    uart.write(data)

while True:
    for i in range(4):
        if buttons[i].value() == 0:
            send_button_data()
            utime.sleep_ms(int(1000/60))
