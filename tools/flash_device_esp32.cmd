SET FMW=%CD%\firmware\ESP32_FERMENTO\firmware.bin
esptool --baud 460800 write-flash 0x1000 %FMW%
