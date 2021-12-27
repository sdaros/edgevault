{ config, lib, pkgs, ... }:

let
  inherit (lib) types mkEnableOption mkIf mkOption;
  cfg = config.modules.sshd;
in {
  options.modules.sshd = {
    enable = mkEnableOption "sshd";
    port = mkOption {
      type = types.port;
      default = 22;
      description = "TCP Port assigned by examesh for SSH traffic.";
    };

  };
  config = mkIf cfg.enable {
    networking.firewall.allowedTCPPorts = [ cfg.port ];
    services.openssh = {
      enable = true;
      challengeResponseAuthentication = false;
      passwordAuthentication = false;
      permitRootLogin = "no";
      listenAddresses = [{
        addr = "0.0.0.0";
        port = cfg.port;
      }];
    };
  };
}
