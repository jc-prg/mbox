# Config GPIO ports ...

# For LED
#------------------------------
led_pins = {
            "SDI"    : 11, #23 #11
            "RCLK"   : 12, #24 #12
            "SRCLK"  : 13  #26 #13
            }

# For BUTTONS
#------------------------------

button_pins = {
               "up"    : 40,
               "mute"  : 38,
               "down"  : 37,
               "next"  : 7,
               "pause" : 35,
               "back"  : 33,
               "GND"   : "(34) connected to GROUND"
               }

# For RFID sensor (documentations only; not configuration)
#------------------------------

rfid_pins = {
             "SDA"     : 24,
             "SCK"     : 23,
             "MOSI"    : 19,
             "MISO"    : 21,
             "IRQ"     : "not used",
             "GND"     : "(9) connected to GROUND",
             "RST"     : 22,
             "VCC"     : "(17) connected to 3.3V"
             }

# Overview GPIO Raspberry Pi 3 / Pi Zero
# -----------------------------
#    3.3V     1  :   2    5V
#   GPIO2     3  :   4    5v
#   GPIO3     5  :   6    GND
#   GPIO4     7  :   8    GPIO14
#     GND     9  :  10    GPIO15
#  GPIO17    11  :  12    GPIO18
#  GPIO27    13  :  14    GND
#  GPIO22    15  :  16    GPIO23
#    3.3V    17  :  18    GPIO24
#  GPIO10    19  :  20    GND
#   GPIO9    21  :  22    GPIO25
#  GPIO11    23  :  24    GPIO8
#     GND    25  :  26    GPIO7
#     DNC    27  :  28    DNC
#   GPIO5    29  :  30    GND
#   GPIO6    31  :  32    GPIO12
#  GPIO13    33  :  34    GND
#  GPIO19    35  :  36    GPIO16
#  GPIO25    27  :  38    GPIO20

# -----------------------------
# EOF
