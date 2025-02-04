set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"] # Set to powershell v7.

install:
    mkdir -p src/typst-anki/lib
    pip install typst -t src/typst-anki/lib/
    pip install pypandoc -t src/typst-anki/lib/
    cd src/typst-anki && zip -r typst-anki.zip ./*

package:
    cd src/typst-anki && zip -r typst-anki.zip ./*
