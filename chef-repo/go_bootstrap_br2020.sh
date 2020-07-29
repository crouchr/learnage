# Run as crouchr on xw6600
# br2020 is the hostname of the node being bootstrapped into Chef Server
echo "First time bootstrap the CentOS7 honeypot into Hosted Chef Server..."
knife bootstrap --sudo \
-U vagrant \
-P vagrant \
--ssh-verify-host-key never \
br2020.ddns.net

#--ssh-user: This flag is deprecated. Use -U/--connection-user instead.
#--ssh-password: This flag is deprecated. Use -P/--connection-password instead.
#--[no-]host-key-verify: This flag is deprecated. Use --ssh-verify-host-key instead.

