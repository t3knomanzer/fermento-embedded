@ECHO OFF


echo "Erasing device..."
call %~dp0erase_device.cmd
echo "Compiling..."
python tools/compile.py
echo "Uploading..."
python tools/upload.py
echo "Cleaning..."
python tools/clean.py

echo "Complete!"