7z.exe x -oe:\test\ "e:\test\setup.zip"
del "e:\test\setup.zip"
 e:\test\ThunderbirdSetup.exe -ms
 msiexec /qb /i e:\test\python-setup.msi 
del "e:\test\ThunderbirdSetup.exe"
del "e:\test\python-setup.msi"
