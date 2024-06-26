chcp 65001
rmdir /S /Q "D:\Code\打包"
call D:\Code\program\venv\Scripts\activate.bat
pyinstaller -D -w "D:\Code\program\program\main.pyw" -i "D:\Code\program\program\source\img\program.ico" -n zbProgram --distpath "D:\Code\打包" --workpath "D:\Code\打包\build" --clean --contents-directory source --add-data D:\Code\program\program\source\img:img -y
call D:\Code\program\venv\Scripts\deactivate.bat
start setup.iss