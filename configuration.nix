{ config, lib, pkgs, ... }:

let
  inherit (builtins) elemAt;
  defaultLocale = "de_DE.UTF-8";
  timeZone = "Europe/Berlin";
  hostName = "key-keeper";
  domainName = "z.cip.li";
  examesh = {
    ipv4.address = "10.237.1.26";
    ipv4.prefixLength = 24;
    defaultGateway = "10.237.1.1";
    allowedTCPPorts = [ 22 6001 ];
  };
  ssh.pubKey =
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICUVCcNS/DQXPNmW0ohhRXGYgoZ7u6SBWcHDXzoi5AWf nixos@forseti";

in {
  modules.sshd = {
    enable = true;
    port = (elemAt examesh.allowedTCPPorts 0);
  };
  modules.acme = {
    enable = false;
    email = "john.doe@cip.li";
    dnsProvider = "cloudflare";
    credentialsFile = ./credentials.env;
  };
  modules.caddy = {
    enable = false;
    port = (elemAt examesh.allowedTCPPorts 1);
  };
  modules.vaultwarden = {
    enable = false;
    backupFolder = "/etc/nixos/vaultwarden";
  };

  imports = [
    ./modules/sshd.nix
    ./modules/acme.nix
    ./modules/caddy.nix
    ./modules/vaultwarden.nix
  ];

  i18n.defaultLocale = defaultLocale;
  time.timeZone = timeZone;
  networking.firewall.enable = true;
  networking.hostName = hostName;
  networking.domain = domainName;
  networking.nameservers = [ "9.9.9.9" "1.1.1.1" "8.8.8.8" ];
  networking.defaultGateway = examesh.defaultGateway;
  networking.interfaces.eth0.ipv4.addresses = [{
    address = examesh.ipv4.address;
    prefixLength = examesh.ipv4.prefixLength;
  }];

  environment.systemPackages = with pkgs; [ git vim curl ];

  users.users.nixos = {
    name = "nixos";
    description = "The primary user account";
    extraGroups = [ "wheel" ];
    isNormalUser = true;
    group = "users";
    uid = 1000;
    openssh.authorizedKeys.keys = [ ssh.pubKey ];
  };

  nix = {
    trustedUsers = [ "nixos" ];
    allowedUsers = [ "nixos" ];
    gc = {
      automatic = true;
      dates = "weekly";
      options = "--delete-older-than 30d";
    };
  };

  boot = {
    kernelPackages = pkgs.linuxPackages_latest;
    loader = {
      grub.enable = false;
      generic-extlinux-compatible.enable = true;
    };
  };

  fileSystems = {
    "/" = {
      device = "/dev/disk/by-label/NIXOS_SD";
      fsType = "ext4";
    };
    # Spare our SD Card from abuse by logging everything to RAM
    "/var/log" = {
      fsType = "tmpfs";
      options = [ "size=40M" ];
    };
  };
  zramSwap.enable = true;
  swapDevices = [ ];

  services.journald.extraConfig = "SystemMaxUse=20M";
  systemd = {
    services.clear-log = {
      description = "Clear >1 month-old logs every week";
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${pkgs.systemd}/bin/journalctl --vacuum-time=30d";
      };
    };
    timers.clear-log = {
      wantedBy = [ "timers.target" ];
      partOf = [ "clear-log.service" ];
      timerConfig.OnCalendar = "weekly UTC";
    };
  };
}
