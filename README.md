# pytesseract based OCR
this is a basic OCR with GUI to extract text
from images, such as screenshots, and store the data in
mysql table. GUI is pyqt5
this baseline version 0.0.0 of OCR was generated with chatGPT

# dependencies
OS linux (archlinux in this case 6.10.3-arch1-2 x86_64 GNU/Linux)
But could be any distro

### pacman -Qo /usr/share/tessdata/
/usr/share/tessdata/ is owned by tesseract 5.4.1-1
/usr/share/tessdata/ is owned by tesseract-data-est 2:4.1.0-4
/usr/share/tessdata/ is owned by tesseract-data-eus 2:4.1.0-4
/usr/share/tessdata/ is owned by tesseract-data-osd 2:4.1.0-4
/usr/share/tessdata/ is owned by tesseract-data-rus 2:4.1.0-4

### pacman -Q | grep -i percona
libperconaserverclient 8.3.0_1-2
percona-server 8.3.0_1-2
percona-server-clients 8.3.0_1-2

### image storage path
sudo mkdir -p /opt/images && chown -R you:you /opt/images

### init schema
initialize from deps/init.sql

### mysql hardcoded credentials
update guioctress.py and octress.py with valid credentials for mysql

### /opt/images
Either put some images in this path, like screenshots,
or something with clear text - or update octress.py to use
different path

### venv (init python virtual env)

from the repo:
mkdir static/
python -m venv ocr_venv
# activate ocr_venv
source ocr_venv/bin/activate
# install deps 
Install the python-pillow on your distro
pacman -S python-pillow
pip install -r requirements.txt