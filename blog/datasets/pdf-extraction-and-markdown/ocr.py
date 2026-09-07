"""Optional local Poppler/Tesseract adapter; no server or network is involved."""
from pathlib import Path
import shutil
import subprocess
import tempfile


def tesseract(language='eng'):
    renderer=shutil.which('pdftoppm');engine=shutil.which('tesseract')
    if not renderer or not engine:raise RuntimeError('OCR requires local pdftoppm and tesseract executables; native-only extraction remains available.')
    def page_text(path,page):
        with tempfile.TemporaryDirectory(prefix='tegridy-ocr-') as temporary:
            prefix=Path(temporary)/'page'
            subprocess.run([renderer,'-f',str(page),'-l',str(page),'-singlefile','-scale-to','2000','-png',str(Path(path).resolve()),str(prefix)],check=True,capture_output=True,timeout=60)
            result=subprocess.run([engine,str(prefix)+'.png','stdout','-l',language,'--psm','6'],check=True,capture_output=True,timeout=60)
            return result.stdout.decode('utf-8',errors='strict')
    page_text.engine='Tesseract with Poppler; scale-to 2000, PSM 6, language '+language
    return page_text
