{
  description = "Collection of python3 scripts to deal with Eu4";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  inputs.flake-compat = {
    url = "github:edolstra/flake-compat";
    flake = false;
  };

  outputs = { nixpkgs, flake-utils, ... }:
    let
      inherit (flake-utils.lib) eachSystem system;
    in
    eachSystem [ system.x86_64-linux ]
      (system:
        let
          pkgs = import nixpkgs
            {
              inherit system;
            };
        in
        {
          devShell = pkgs.mkShell
            {
              name = "Script-Shell";
            };
        }
      );
}
