rem This is all very specific to one type of setup
call "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars32.bat" || exit /b 1
signtool sign /a /tr http://timestamp.globalsign.com/?signature=sha2 /td SHA256 dist\spacebridge.exe || exit /b 1
