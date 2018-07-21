{ stdenv, fetchgit, gcc, ninja }:

stdenv.mkDerivation rec {
  name = "jabzff${version}";
  version = "0.1";
  # nix-prefetch-git file:///...
  src = fetchgit {
    url = "file:///...";
    rev = "27a9a156e2755c4ada67e55b32e098089b0a4ef4";
    sha256 = "12srhhpvb0f4fj4cx4jyrzrmlapi2ygdkbvrnr028n15i4s3qm4r";
  };

  nativeBuildInputs = [ gcc ninja ];

  installPhase = ''
    mkdir -p $out/bin
    cp bin/* $out/bin
  '';
}
