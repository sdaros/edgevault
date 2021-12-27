{ config, lib, pkgs, ... }:

let
  inherit (lib) types mkEnableOption mkIf mkOption;
  cfg = config.modules.acme;
  serverName = config.networking.fqdn;
in {
  options.modules.acme = {
    enable = mkEnableOption "acme";
    email = mkOption {
      type = types.nullOr types.str;
      default = null;
      description =
        "Contact email address for the CA (letsencrypt) to be able to reach you.";
    };
    dnsProvider = mkOption {
      type = types.nullOr types.str;
      default = null;
      description = "Dns provider to use for the ACME stuff";
    };
    credentialsFile = mkOption {
      type = types.nullOr types.path;
      default = null;
      description = "Credentials to store API tokens of your DNS provider";
    };
  };

  config = mkIf cfg.enable {
    # Retrieve TLS certificates from letsencrypt
    security.acme.acceptTerms = true;
    security.acme.email = cfg.email;
    security.acme.certs = {
      "${serverName}" = {
        group = "caddy";
        dnsProvider = cfg.dnsProvider;
        reloadServices = [ "caddy.service" ];
        credentialsFile = cfg.credentialsFile;
      };
    };
  };
}
