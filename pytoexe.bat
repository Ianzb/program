chcp 65001
pyinstaller -D -w "D:\编程\program\beta\main.pyw" -i "D:\编程\program\beta\source\img\program.ico" -n zbProgram --distpath "D:\编程\打包\dist" --workpath "D:\编程\打包\build" --clean --contents-directory source --add-data D:\编程\program\beta\source\img:img -y
