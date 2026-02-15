call ../.venv/Scripts/activate.bat
set PYTHONIOENCODING=utf-8
pip freeze > ../requirements.txt
call ../.venv/Scripts/deactivate.bat
