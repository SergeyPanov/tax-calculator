{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.poppler-utils
    pkgs.tesseract
    pkgs.git
  ];

  shellHook = ''
    if [ ! -d .venv ]; then
      python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install -q -r requirements.txt
  '';
}
