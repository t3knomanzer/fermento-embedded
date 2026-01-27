tools/flash_device_esp32s3.cmdSET FMW=%CD%\firmware\ESP32_GENERIC_S3\firmware.bin
esptool --baud 460800 write-flash 0 %FMW%
