{ config, lib, pkgs, ... }:

let
  inherit (lib) types mkEnableOption mkIf mkOption;
  inherit (builtins) toString;
  cfg = config.modules.caddy;
  serverName = config.networking.fqdn;
in {
  options.modules.caddy = {
    enable = mkEnableOption "caddy";
    port = mkOption {
      type = types.port;
      default = 6001;
      description =
        "First TCP Port assigned by examesh for publicly exposed services.";
    };
  };
  config = mkIf cfg.enable {
    networking.firewall.allowedTCPPorts = [ cfg.port ];
    services.caddy.enable = true;
    services.caddy.virtualHosts = {
      "${serverName}:${(toString cfg.port)}".extraConfig = ''
        # Location to letsencrypt TLS certificate retrieved by `modules.acme` (lego)
        tls /var/lib/acme/${serverName}/fullchain.pem /var/lib/acme/${serverName}/key.pem

        # Harden caddy's config with the following headers
        header {
             # Enable HTTP Strict Transport Security (HSTS)
             Strict-Transport-Security "max-age=31536000;"
             # Enable cross-site filter (XSS) and tell browser to block detected attacks
             X-XSS-Protection "1; mode=block"
             # Disallow the site to be rendered within a frame (clickjacking protection)
             X-Frame-Options "DENY"
             # Prevent search engines from indexing (optional)
             X-Robots-Tag "none"
             # Server name removing
             -Server
        }

        # Uncomment to allow access to the admin interface only from local networks
        # @insecureadmin {
        #   not remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8
        #   path /admin*
        # }
        # redir @insecureadmin /

        # Notifications redirected to the websockets server
        reverse_proxy /notifications/hub localhost:3012

        # Proxy everything else to Rocket
        reverse_proxy localhost:8000 {
             # Send the true remote IP to Rocket, so that vaultwarden can put this in the
             # log, so that fail2ban can ban the correct IP.
             header_up X-Real-IP {remote_host}
        }
      '';
    };
    services.fail2ban.enable = true;
    environment.etc."fail2ban/filter.d/vaultwarden.local".text = ''
      [INCLUDES]
      before = common.conf

      [Definition]
      failregex = ^.*Username or password is incorrect\. Try again\. IP: <ADDR>\. Username:.*$
      ignoreregex =
      journalmatch = _SYSTEMD_UNIT=vaultwarden.service + _COMM=vaultwarden
    '';
    services.fail2ban.jails.vaultwarden = ''
      enabled = true
      backend = systemd
      port = ${(toString cfg.port)}
      filter = vaultwarden
      maxretry = 5
    '';
    users.users.sd.extraGroups = [ "vaultwarden" "caddy" ];
  };
}
