chcp 65001
rmdir /S /Q "D:\编程\打包"
pyinstaller -D -w "D:\编程\program\program\main.pyw" -i "D:\编程\program\program\source\img\program.ico" -n zbProgram --distpath "D:\编程\打包" --workpath "D:\编程\打包\build" --clean --contents-directory source --add-data D:\编程\program\program\source\img:img -y
start setup.iss