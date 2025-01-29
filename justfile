set windows-shell := ["powershell.exe"]

install:
    mkdir -p src/typst-anki/lib
    pip install typst -t src/typst-anki/lib/
    pip install pypandoc -t src/typst-anki/lib/
    cd src/typst-anki && zip -r typst-anki.zip ./*

package:
    cd src/typst-anki && zip -r typst-anki.zip ./*
