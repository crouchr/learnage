#!/usr/bin/perl

    use strict ;
    use Net::Flow qw(decode) ;
    use IO::Socket::INET;
    use Sys::Syslog qw( :DEFAULT setlogsock);
     
    # no longer used, but left here to show how to call C function from Perl
    #use glowormlogic;
    
    my $srcIP     = undef;
    my $srcPort   = undef;
    my $dstIP     = undef;
    my $dstPort   = undef;
    my $proto     = undef;
    my $pkts      = undef;
    my $bytes     = undef;
    my $flags     = undef;
    my $start     = undef;
    my $end       = undef;
    my $inIf      = undef;
    my $outIf     = undef;
    my $direction = undef;
    my $myip      = undef;

    # new fields from Layer 2 and Security Monitoring Netflow feature
    #my $ipid    = undef;
    #my $field25 = undef;
    #my $field26 = undef;
    #my $field51 = undef;
    #my $field52 = undef;
    #my $field53 = undef;
    #my $field54 = undef;

    # Some Flexible Netflow export fields
    #my $field313       = undef;
    #my $field314       = undef;
    #my $field208       = undef;
    #my $field89        = undef;    
    #my $field197       = undef;   
    #my $field88        = undef;    
    #my $sectionHeader  = undef;
    #my $sectionPayload = undef;                        
    #my $direction      = undef;
        
    my $flow    = undef;
      
    # Netflow source (i.e. router name) is first command-line argument
    #my $netflow_source = "bg_rtr";
    #my $netflow_source = $ARGV[0] ;
    
    # The DMZ IP address to listen for flows from
    my $myip = $ARGV[0];
    #printf "blackrain_netflow.pl : IP to be ignored = %s\n" , $myip; 
        
    # Listening port is second command-line parameter
    my $receive_port = 2055 ;
    #my $receive_port = $ARGV[1] ;
    
    #printf "netflow_source : %s\n" , $netflow_source; 
    printf "blackrain_netflow.pl : receive_port (UDP) = %s\n" , $receive_port; 
        
    # Write pid to file so can be monitored by monit    
    #writePid();     
    
    # Initialise syslog with correct name
    #openlog("netflow-".$ARGV[0],'user');
    openlog("blackrain_netflow",'user');
  
    # myIP = IP address of the honeypot system itself -> do not log this netflow traffic
    printf "blackrain_netflow.pl : honeypot management IP (myip), ignore = %s\n" , $myip;
    my @subnetFields = split('\.',$myip);
    #printf "subnet fields = %s\n", @subnetFields[0];
    #printf "subnet fields = %s\n", @subnetFields[1];
    my $subnet = @subnetFields[0] . '.' . @subnetFields[1] . '.' . @subnetFields[2] . '.';
    #printf "blackrain_netflow.pl : local subnet = %s\n" , $subnet;
      
    my $packet = undef ;
    my $TemplateArrayRef = undef ;
    my $sock = IO::Socket::INET->new( LocalPort =>$receive_port, Proto => 'udp') ;

    printf "blackrain_netflow.pl : waiting for netflow packets...\n";
    while ($sock->recv($packet,15000)) {

        my ($HeaderHashRef,$FlowArrayRef,$ErrorsArrayRef)=() ;

          ( $HeaderHashRef,
            $TemplateArrayRef,
            $FlowArrayRef,
            $ErrorsArrayRef)
            = Net::Flow::decode(
                                \$packet,
                                $TemplateArrayRef
                                ) ;

        grep{ print "$_\n" }@{$ErrorsArrayRef} if( @{$ErrorsArrayRef} ) ;

        #print "\n- Header Information -\n" ;
        #foreach my $Key ( sort keys %{$HeaderHashRef} ){
        #    printf " %s = %3d\n",$Key,$HeaderHashRef->{$Key} ;
        #}

        foreach my $TemplateRef ( @{$TemplateArrayRef} ){
            #print "\n-- Template Information --\n" ;
        
             foreach my $TempKey ( sort keys %{$TemplateRef} ){
                if( $TempKey eq "Template" ){
                    #printf "  %s = \n",$TempKey ;
                    foreach my $Ref ( @{$TemplateRef->{Template}}  ){
                        foreach my $Key ( keys %{$Ref} ){
                            printf "   %s=%s", $Key, $Ref->{$Key} if 0;
                        }
                        print "\n" if 0 ;
                    }
                } else {
                    printf "  %s = %s\n", $TempKey, $TemplateRef->{$TempKey} if 0;
                }
            }
        }


        foreach my $FlowRef ( @{$FlowArrayRef} ){
            
            $srcIP   = num2ip(hex(unpack("H*",$FlowRef->{'8'})));
            $dstIP   = num2ip(hex(unpack("H*",$FlowRef->{'12'})));
            $srcPort = hex(unpack("H*",$FlowRef->{'7'}));
            $dstPort = hex(unpack("H*",$FlowRef->{'11'}));
            $proto   = hex(unpack("H*",$FlowRef->{'4'}));
            $pkts    = hex(unpack("H*",$FlowRef->{'2'}));
            $bytes   = hex(unpack("H*",$FlowRef->{'1'}));
            $flags   = hex(unpack("H*",$FlowRef->{'6'}));
            
            # uptime in msecs when flow started
            $start   = hex(unpack("H*",$FlowRef->{'22'}));
            # uptime in msecs when flow finished
            $end     = hex(unpack("H*",$FlowRef->{'21'}));
            
            $inIf    = hex(unpack("H*",$FlowRef->{'10'}));
            $outIf   = hex(unpack("H*",$FlowRef->{'14'}));
            
            
            # myIP = IP address of the honeypot system itself -> do not log this netflow traffic
            #@subnetFields = split(/\./,$myIP);
            #subnet = subnetFields[0] . '.' . subnetFields[1] . '.' . subnetFields[2]
            #print subnet;

            
            
            if ($srcIP ne $myip and $dstIP ne $myip)  {
                
                if ($dstIP eq "192.168.1.3" or $srcIP eq "192.168.1.3") {
                    #printf "prelude VM Host, so ignore\n";
                    next;
                }    

                
                #printf "myip is %s\n" , $myip;
                my @dstIPsubnetFields = split('\.',$dstIP);
                my $dstIPsubnet = @dstIPsubnetFields[0] . '.' . @dstIPsubnetFields[1] . '.' . @dstIPsubnetFields[2] . '.';
                my @srcIPsubnetFields = split('\.',$srcIP);
                my $srcIPsubnet = @srcIPsubnetFields[0] . '.' . @srcIPsubnetFields[1] . '.' . @srcIPsubnetFields[2] . '.';
                
                #printf "blackrain_netflow.pl : flow received : %s -> %s port=%s pr=%s inIf=%s outIf=%s pkts=%s bytes=%s\n", $srcIP,$dstIP,$dstPort,$proto,$inIf,$outIf,$pkts,$bytes;

                #printf "srcIPsubnet is %s\n" , $srcIPsubnet;
                #printf "dstIPsubnet is %s\n" , $dstIPsubnet;
                #printf "localSubnet is %s\n" , $subnet;
                
                if ($dstIPsubnet eq $subnet) {            
                    $direction = "in";
                } else {
                    $direction = "out";
                }   
                
                my $duration = int($end) - int($start);
                
                #$flow = "netflow_record dir=" . $direction . " sIP=" . $srcIP . " sP=" . $srcPort ." dIP=" . $dstIP . " dP=" . $dstPort . " pr=" . $proto . " B=" . $bytes . " p=" . $pkts . " fl=" . $flags . " t=" . $duration; 
                
                if ($dstIP eq "255.255.255.255") {
                    #printf "dstIP %s is broadcast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    

                if ($dstIP eq "224.0.0.1") {
                    #printf "dstIP %s is ALL HOSTS multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    

                if ($dstIP eq "224.0.0.2") {
                    #printf "dstIP %s is ALL ROUTERS multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
                
                if ($dstIP eq "224.0.0.5") {
                    #printf "dstIP %s is OSPF ALL D ROUTERS multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
                
                if ($dstIP eq "224.0.0.18") {
                    #printf "dstIP %s is VRRP multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
               
               if ($dstIP eq "224.0.0.19" or $dstIP eq "224.0.0.20" or $dstIP eq "224.0.0.21") {
                    #printf "dstIP %s is IS-IS multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
               
               if ($dstIP eq "224.0.0.22") {
                    #printf "dstIP %s is IGMPv3 multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
               
               if ($dstIP eq "224.0.0.102") {
                    #printf "dstIP %s is HSRP multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
               
               if ($dstIP eq "224.0.0.251") {
                    #printf "dstIP %s is zeroconf mDNS multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    

                if ($dstIP eq "224.0.0.252") {
                    next;
                }    

               if ($dstIP eq "224.0.1.1") {
                    #printf "dstIP %s is NTP multicast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
                
                if ($dstIP eq "239.255.255.250") {
                    next;
                }    

                if ($dstIP eq "239.255.255.253") {
                    next;
                }    

                my $broadcast = $subnet . '255';
                if ($dstIP eq $broadcast) {
                    #printf "dstIP %s is subnet broadcast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
                                                
                my $broadcast = $subnet . '255';
                if ($dstIP eq $broadcast) {
                    #printf "dstIP %s is subnet broadcast, so ignore\n" , $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
                
                # source and destination are on local subnet
                if ($srcIPsubnet eq $dstIPsubnet) {
                    #printf "intra subnet traffic, %s -> %s , so ignore\n" , $srcIP, $dstIP;
                    next;
                    #syslog('info|local0',$flow);
                }    
                
                #if ($dstIPsubnet eq $subnet) {            
                #    $direction = "in";
                #} else {
                #    $direction = "out";
                #}   
                
                # flow got past all the pre-filtering above so it is valid
                $flow = "netflow_record dir=" . $direction . " sIP=" . $srcIP . " sP=" . $srcPort ." dIP=" . $dstIP . " dP=" . $dstPort . " pr=" . $proto . " B=" . $bytes . " p=" . $pkts . " fl=" . $flags . " t=" . $duration; 
                
                #printf "netflow : %s -> %s port=%s pr=%s inIf=%s outIf=%s pkts=%s bytes=%s\n", $srcIP,$dstIP,$dstPort,$proto,$inIf,$outIf,$pkts,$bytes;
                printf "netflow : %s -> %s port=%s pr=%s pkts=%s\n", $srcIP,$dstIP,$dstPort,$proto,$pkts;

                 
            } else {
                next;	
                # flow was for honeypot host IP not honeypot applications so log with local0
                #$direction = "N/A"
                #my $duration = int($end) - int($start);
                #$flow = "dir=" . $direction . " sIP=" . $srcIP . " sP=" . $srcPort ." dIP=" . $dstIP . " dP=" . $dstPort . " pr=" . $proto . " B=" . $bytes . " p=" . $pkts . " fl=" . $flags . " t=" . $duration; 
                #print $flow . "\n";
                #syslog('info|local0',$flow);

            }
            
            # Honeypot flow so log with local1
            #my $duration = int($end) - int($start);
            #$flow = "dir=" . $direction . " sIP=" . $srcIP . " sP=" . $srcPort ." dIP=" . $dstIP . " dP=" . $dstPort . " pr=" . $proto . " B=" . $bytes . " p=" . $pkts . " fl=" . $flags . " t=" . $duration; 
            #print $flow . "\n";
            syslog('info|local2',$flow);
                         
     }                                                                                                      
}
                                                                                                                                
sub num2ip {
  return(join(".",unpack("C4",pack("N",$_[0]))));
  }

sub writePid {
  open (FILE, "> /var/run/netflow.pid");
  print FILE "$$\n";
  close (FILE);
}                     
          