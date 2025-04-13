chcp 65001
rmdir /S /Q "..\build"
call ..\.venv\Scripts\activate.bat
pyinstaller -D -w "..\program\main.pyw" -i "..\program\source\img\program.ico" -n zbProgram --distpath "..\build" --workpath "..\build\build" --clean --contents-directory source --add-data ..\program\source\img:img -y
call ..\.venv\Scripts\deactivate.bat
start setup.iss
pause