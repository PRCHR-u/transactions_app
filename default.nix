{ pkgs ? import <nixpkgs> {} }:
let
  python = pkgs.python312.withPackages (ps: with ps; [ pandas pytest flake8 black ]);
in
pkgs.mkShell {
  buildInputs = [ python ];
}