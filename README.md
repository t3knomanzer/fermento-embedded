# fermento-software
Embedded app for the sourdough starter tracker "Fermento". Uses micropython running on an ESP32


## Instructions
In WSL make sure you have python3 and python3-pip installed.
Follow the instructions on [this link](https://github.com/micropython/micropython/blob/master/ports/esp32/README.md) to setup and build micropython.
Follow the instructions on [this link](https://github.com/peterhinch/micropython-micro-gui/blob/main/README.md#appendix-2-freezing-bytecode) to freeze modules into the firmware.

Duplicate a board found in ~/micropython/ports/ESP32/boards/ and modify the mpconfigboard.cmake to your liking.
For example, to optimize ram usage remove sdkconfig.ble and include sdkconfig.free_ram.
Use mpconfigboard.h to enable/disable features


```
// mpconfigboard.cmake

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    boards/sdkconfig.free_ram
)
```

```
// mpconfigboard.h
// Both of these can be set by mpconfigboard.cmake if a BOARD_VARIANT is
// specified.

#ifndef MICROPY_HW_BOARD_NAME
#define MICROPY_HW_BOARD_NAME "Generic ESP32 module"
#endif

#ifndef MICROPY_HW_MCU_NAME
#define MICROPY_HW_MCU_NAME "ESP32"
#endif

#define MICROPY_PY_BLUETOOTH (0)

```

Below is an example of a shell script to build the firmware for a specific board and variant, then copy the fimrware to another location. Place this file into your scripts folder (~/scripts).

```
cd ~/micropython/ports/esp32
MANIFEST='/home/rhenares/scripts/esp32_manifest.py'
ENV='~/esp-idf/export.sh'
FMW_SOURCE='~/micropython/ports/esp32/build-ESP32_GENERIC_S3-SPIRAM_OCT/firmware.bin'
FMW_TARGET='/mnt/c/Users/ruben/Projects/T3knomanzer/Hardware/Fermento/fermento-software/firmware/ESP32S3/firmware.bin'

source $ENV

make submodules
make clean
if make -j 8 BOARD=ESP32_GENERIC_S3 BOARD_VARIANT=SPIRAM_OCT FROZEN_MANIFEST=$MANIFEST
then
    echo Firmware compiled
    echo Copying firmware to project folder...
    cp $FMW_SOURCE $FMW_TARGET
    echo Done!
else
    echo Build failure
fi
```

Create a symbolic link inside ~/scripts/modules pointing at the folder containing the modules you want to freeze.
```

```

To include extra packages in the firmware from the [micropython-lib](https://github.com/micropython/micropython-lib/), use the `require` function in the manifest.

```
include("$(MPY_DIR)/ports/esp32/boards/manifest.py")
freeze("/home/rhenares/scripts/modules/esp32_modules")
require("logging")
require("inspect")
```