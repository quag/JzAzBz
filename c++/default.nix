# nix-env -f . -iA jabzff

with import <nixpkgs> {};

rec {
  jabzff = pkgs.callPackage ./jabzff.nix {  };
}
