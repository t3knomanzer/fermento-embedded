SET FMW=%CD%\firmware\ESP32S3\firmware.bin
esptool --baud 460800 write-flash 0 %FMW%
