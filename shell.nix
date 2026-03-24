{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.uv
    pkgs.poppler-utils
    pkgs.tesseract
    pkgs.git
  ];

  shellHook = ''
    if [ ! -d .venv ]; then
      uv venv .venv
    fi
    source .venv/bin/activate
    uv pip install -q -r requirements.txt
  '';
}
