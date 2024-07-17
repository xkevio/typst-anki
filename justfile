set windows-shell := ["powershell.exe"]

install:
    mkdir -p src/typst_anki/lib
    pip install typst -t src/typst_anki/lib/
    pip install pypandoc -t src/typst_anki/lib/
    cd src/typst_anki && zip -r typst_anki.zip ./*

package:
    cd src/typst_anki && zip -r typst_anki.zip ./*
