{ config, lib, pkgs, ... }:

let
  inherit (lib) types mkEnableOption mkIf mkOption;
  cfg = config.modules.vaultwarden;
  serverName = config.networking.fqdn;
in {
  options.modules.vaultwarden = {
    enable = mkEnableOption "vaultwarden";
    backupFolder = mkOption {
      type = types.nullOr types.str;
      default = null;
      description =
        "Folder to backup the vaultwarden database (and other assets) to";
    };
  };
  config = mkIf cfg.enable {
    services.vaultwarden.enable = true;
    services.vaultwarden.backupDir = cfg.backupFolder;
    services.vaultwarden.config = {
      signupsAllowed = false;
      invitationsAllowed = false;
      domain = "http://${serverName}";
      rocketPort = 8000;
      websocketEnabled = true;
    };
  };
}
