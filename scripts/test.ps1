# test.ps1: Run all Python tests using pytest (PowerShell)
$venvPython = "./.venv/Scripts/python.exe"
& $venvPython -m pytest --maxfail=3 --disable-warnings -v
