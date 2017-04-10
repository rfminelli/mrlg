#!/usr/bin/perl -T
##
## Multi-Router Looking Glass
## Written by and Copyright (c) 2000-2014 John Fraizer
## John@op-sec.us
## All Rights Reserved

use strict;
use warnings;
no warnings "once";

$::Version='5.5.0 (IPv6+SSH)';

##
## Original Code Release: 27 NOV 2000
## Copyright (c) 2000 - 2014 John W. Fraizer III <john@op-sec.us>
## *All* copyright notices must remain in place to use this code.
##
## mrlg.conf modification by Stephane Bortzmeyer <bortzmeyer@gitoyen.net>
##
## The latest version of this code is available at:
##
## http://mrlg.op-sec.us/
##
## This file is part of the Multi-Router Looking Glass (MRLG).
##
## Multi-Router Looking Glass (MRLG) is free software; you can redistribute
## it and/or modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2, or (at 
## your option) any later version.
##
## Multi-Router Looking Glass (MRLG) is distributed in the hope that it will
## be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General 
## Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Multi-Router Looking Glass (MRLG); see the file LICENSE.  If not,
## write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
## Boston, MA 02111-1307, USA.
##
## Please leave copyright notices in tact.  If for whatever reason, you 
## desire to remove or modify the notices, drop an email to me at the
## email address above.  I might just make an exception for you!  If I find
## your looking-glass running my code without the copyright notice, and I
## haven't given prior permission for you to remove the notice, I'm likely
## to make a huge stink about it in very public places.
##


require 5.002;
use POSIX;
use Net::Telnet::Cisco;
use Net::SSH::Perl;
use Net::hostent;
use Socket;

require '/etc/mrlg.conf';


# Set this to a directory that is writable by your webserver process.
$ENV{HOME} = $::writable_directory;



# Set default values
if (! defined($::bgp)) 		{
    				$::bgp = 0;
				}

if (! defined($::bgp_plus)) 	{
    				$::bgp_plus = 0;
				}

if (! defined($::multicast)) 	{
    				$::multicast = 0;
				}

if (! defined($::ospf)) 	{
    				$::ospf = 0;
				}

if (! defined($::ospf_v6)) 	{
    				$::ospf_v6 = 0;
				}

if (! defined($::rip)) 		{
    				$::rip = 0;
				}

if (! defined($::ripng)) 		{
    				$::ripng = 0;
				}

if (! defined($::ip_route)) 	{
				$::ip_route = 0;
				}

if (! defined($::ip6_route)) 	{
    				$::ip6_route = 0;
				}

if (! defined($::interfaces)) 	{
    				$::interfaces = 0;
				}

if (! defined($::beacon)) 	{
			    	$::beacon = 0;
				}

$ENV{'PATH'} = "";

my ($server, $login_pass, $login_user, $pass, $bgpd, $zebra, $ospfd, $ospf6d, $ripd, $ripngd, $full_tables, $cisco, $use_ssh, $debug, $use_port);

############################################################
sub set_router
############################################################

{
    if (! $::Routers{$::Form{'router'}}) {
	die "Something is really wrong (no such router $::Form{'router'})";
    }
    
    $server = $::Routers{$::Form{'router'}}{'server'};
    if (! $server) 	{
			die "No 'server' known for router $::Form{'router'}";
    			}
    $login_user = ($::Routers{$::Form{'router'}}{'login_user'} or 'no_login_user_defined');
    
    $login_pass = ($::Routers{$::Form{'router'}}{'login_pass'} or 'no_login_pass_defined');

    $pass = ($::Routers{$::Form{'router'}}{'pass'} or '');



    if ($::Routers{$::Form{'router'}}{'use_port'})	{
			$bgpd = $::Routers{$::Form{'router'}}{'use_port'};

			$zebra = $::Routers{$::Form{'router'}}{'use_port'};

			$ospfd = $::Routers{$::Form{'router'}}{'use_port'};

			$ospf6d = $::Routers{$::Form{'router'}}{'use_port'};

			$ripd = $::Routers{$::Form{'router'}}{'use_port'};

			$ripngd = $::Routers{$::Form{'router'}}{'use_port'};
			}
    else
			{

    			$bgpd = ($::Routers{$::Form{'router'}}{'bgpd'} or '0');

    			$zebra = ($::Routers{$::Form{'router'}}{'zebra'} or '0');

    			$ospfd = ($::Routers{$::Form{'router'}}{'ospfd'} or '0');

    			$ospf6d = ($::Routers{$::Form{'router'}}{'ospf6d'} or '0');

    			$ripd = ($::Routers{$::Form{'router'}}{'ripd'} or '0');

    			$ripngd = ($::Routers{$::Form{'router'}}{'ripngd'} or '0');
			
			}

    $full_tables= ($::Routers{$::Form{'router'}}{'full_tables'} or '0');

    $cisco= ($::Routers{$::Form{'router'}}{'cisco'} or '0');

    $use_ssh= ($::Routers{$::Form{'router'}}{'use_ssh'} or '0');

    $debug= ($::Routers{$::Form{'router'}}{'debug'} or '0');
    
}



############################################################
#Main
############################################################
{

my ($router, $old_value, $old_query);

## Get the form results now so we can override the default router 
get_form();
    
print "Content-type: text/html\n\n";

print '
<html>
<head>
';
print "<title>MRLG - $::mrlghost - Multi-Router Looking Glass</title>\n";
# The following allows me to measure the popularity of MRLG. Please
# leave it in tact.  It is not rendered as visible text on the page.
print "<!-- PLEASE DO NOT REMOVE: MRLG-version $::Version -->\n";
print "<!-- PLEASE DO NOT REMOVE: Written by and (c) 2000-2014, John Fraizer -->\n";
print "<!-- PLEASE DO NOT REMOVE: #BingaWonga #BingaWonga #BingaWonga #BingaWonga -->\n";
print "<!-- PLEASE DO NOT REMOVE: #MRLG-5.5.0 #Sat-Sep-27-03:16:28-UTC-2014 -->\n";

print '
</head>

<body bgcolor=white>
<font face=arial size=3 color=blue>
';

print "
<font color=blue face=arial size=3>
$::mrlghost - Multi-Router Looking Glass (MRLG)</font><br>
<font color=blue face=arial size=2>
Running MRLG Version $::Version</font></br>
A service of $::company.<br>
<font color=red face=arial size=1>
Note: ALL access to this interface is logged.<hr>
</font></font>
";

## Set up the address, pw and ports, etc for the selected router.
set_router();

if ($::Form{'pass1'} eq $::Routers{$::Form{'router'}}{'pass'})
	{
	if ($::output_before_menu)  
		{
		## Set up which command is to be executed (and then execute it!)
		set_command();
		}
	}
else
	{
	print "<font color=red><B>INVALID PASSWORD!</B></font><BR>";
	}

print '
<font face=arial color=black>
';
print "<form METHOD=\"POST\" action=\"$::url\">\n";
print "<B>Router:</B>  <SELECT Name=\"router\" Size=1>\n";
foreach $router (sort (keys (%::Routers))) 
	{
    	print "<OPTION ";
    	if ($router eq $::Form{'router'}) 
		{
		print " SELECTED";
    		}
    	print " Value=\"$router\">$router";
    	if ($::Routers{$router}{'comment'}) 
		{
       		print " - ", $::Routers{$router}{'comment'};
    		}
    	print "\n";
	}
	if (defined ($::Form{'query'})) 
		{
    		$old_query = $::Form{'query'};
		}
else 
		{
    		$old_query = 0;
		}
print "
</select>

<br><B>Password</B>: <input type=password name=pass1 length=20 maxlength=60
value=\"$::Form{'pass1'}\"> (if required)


<br><br>
<B>Query</B>:
<br>
";

if ($::bgp) 		{
			print "
			<input type=radio name=query value=1>show ip bgp<br>
			<input type=radio name=query value=2>show ip bgp summary<br>
			";
			}

if ($::bgp_plus) 	{
			print "
			<input type=radio name=query value=13>show bgp ipv6<br>
			<input type=radio name=query value=14>show bgp ipv6 summary<br>
			";
			}

if ($::multicast) 	{
			print "
			<input type=radio name=query value=5>show ip bgp ipv4 multicast<br>
			<input type=radio name=query value=6>show ip bgp ipv4 multicast  summary<br>
			";
			}

if ($::ospf) 		{
			print "
			<input type=radio name=query value=10>show ip ospf<br>
			";
			}

if ($::ospf6) 		{
			print "
			<input type=radio name=query value=15>show ipv6 ospf<br>
			";
			}

if ($::rip) 		{
			print "
			<input type=radio name=query value=12>show ip rip<br>
			";
			}

print "
<input type=radio name=query value=11>show ip protocols<br>
";

if ($::ip_route) 	{
			print "
			<input type=radio name=query value=3>show ip route<br>
			";
			}

if ($::ipv6_route) 	{
			print "
			<input type=radio name=query value=16>show ipv6 route<br>
			";
			}

if ($::interfaces) 	{
			print "
			<input type=radio name=query value=4>show interface<br>
			";
			}

print "
<input type=radio name=query value=9>show version<br>
";

if ($::beacon) 		{
			print "
			<input type=radio name=query value=7>trace<br>
			<input type=radio name=query value=8>ping<br>
			";
			}

print "
<br>
";

if (defined ($::Form{'arg'})) 	{
    				$old_value = $::Form{'arg'};
				}
else 
				{
    				$old_value = "";
				}
print "<B>Argument:</B> <input type=text name=arg length=20 maxlength=60 value=\"$old_value\"> \
(many commands require an IP address as argument) \
<input type=submit value=Execute></form></font></font>";

if ($::Form{'pass1'} eq $::Routers{$::Form{'router'}}{'pass'})
	{
	if (! $::output_before_menu)  
		{
		## Set up which command is to be executed (and then execute it!)
		set_command();
		}
	}
	else
	{
	print "<font color=red><B>INVALID PASSWORD!</B></font><BR>";
	}


##############################
## You may NOT remove the following notice from this code.
##############################
print "
<br>
<code>$::url</code>
<font color=blue face=arial size=2>
is running:
<br>
";
# Please do not remove the following copyright notice.
# Many thanks! ~ John Fraizer: Author of MRLG
print "Multi-Router Looking Glass version $::Version<br>\n";
print '
&copy; 2000-2014, John Fraizer  -
<a href=http://www.op-sec.us/>OP-SEC.US</a><br>
Source code: <a href=http://mrlg.op-sec.us/>http://mrlg.op-sec.us/</a>.	
<br>
</body>
</html>
';

## All done!

exit (0); 
}


############################################################
sub get_form
############################################################
{
        
    my ($pair, @pairs, $buffer, $length);

        #read STDIN
        $length = ($ENV{'CONTENT_LENGTH'} or 0);
        read(STDIN, $buffer, $length);

        # Split the name-value pairs
        @pairs = split(/&/, $buffer);
  
        # For each name-value pair:
        foreach $pair (@pairs)
                {
                
                # Split the pair up into individual variables.
                my ($name, $value) = split(/=/, $pair);

                # Decode the form encoding on the name and value variables.
                $name =~ tr/+/ /;
                $name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
 
                $value =~ tr/+/ /;
                $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                # If they try to include server side includes, erase them, so they
                # aren't a security risk if the html gets returned.  Another
                # security hole plugged up.
                $name =~ s/<!--(.|\n)*-->//g;
                $value =~ s/<!--(.|\n)*-->//g;

		# Get rid of linebreaks.
		$name =~ s/\n//g;
		$value =~ s/\n//g;
        
		# Get rid of cisco crash attempts
	        $name =~ s/\(\[0-9\]\*\)\(\_\\1\)\+/ 65535_65535 /g;
	        $value =~ s/\(\[0-9\]\*\)\(\_\\1\)\+/ 65535_65535 /g;
	        $name =~ s/\(\.\*\)\(\\1\)\+/ 65535_65535 /g;
	        $value =~ s/\(\.\*\)\(\\1\)\+/ 65535_65535 /g;

                $::Form{$name} = $value ;
                 
                }
        
}       



############################################################
sub set_command
############################################################
{
    if (! defined ($::Form{'query'})) {
	return;
    }

if ($::Form{'query'} eq '1')
	{
	sh_ip_bgp();
	}

elsif ($::Form{'query'} eq '2')
	{
	sh_ip_bgp_sum();
	}

if ($::Form{'query'} eq '3')
	{
	sh_ip_route();
	}

if ($::Form{'query'} eq '4')
	{
	sh_int();
	}

if ($::Form{'query'} eq '5')
	{
	sh_ip_mbgp();
	}

if ($::Form{'query'} eq '6')
	{
	sh_ip_mbgp_sum();
	}

if ($::Form{'query'} eq '7')
	{
	traceroute();
	}

if ($::Form{'query'} eq '8')
	{
	ping();
	}

if ($::Form{'query'} eq '9')
	{
	sh_version();
	}

if ($::Form{'query'} eq '10')
	{
	sh_ip_ospf();
	}
if ($::Form{'query'} eq '11')
	{
	sh_ip_protocols();
	}
if ($::Form{'query'} eq '13')
	{
	sh_ip_bgp_plus();
	}
if ($::Form{'query'} eq '14')
	{
	sh_ip_bgp_plus_sum();
	}
if ($::Form{'query'} eq '15')
	{
	sh_ip_ospf6();
	}
if ($::Form{'query'} eq '16')
	{
	sh_ip6_route();
	}

}



############################################################
sub sh_ip_bgp
############################################################
{
my $port = $bgpd;
my $command = "show ip bgp $::Form{'arg'}";

if ($::Form{'arg'} =~ /ne/)
        {
        print "Sorry. The <b>show ip bgp neighbors</b> command is disabled."
        }
else
{

if ($bgpd eq '0')
	{
	print "Sorry. The <b>show ip bgp</b> command is disabled for this router."
	}
else
{
if ($::Form{'arg'} eq '')
	{
	if ($full_tables eq '1')
		{
$command = "show ip bgp";
		execute_command($command, $port);
		}
	else
		{
		print "Sorry.  Displaying the FULL routing table would put too much load on the router!\n\n";
		}
	}
else
	{
	execute_command($command, $port);
	}
}
}
}





############################################################
sub sh_ip_bgp_plus
############################################################
{
my $port = $bgpd;
my $command = "show bgp ipv6 $::Form{'arg'}";
if ($bgpd eq '0')
	{
	print "Sorry. The <b>show ipv6 bgp</b> command is disabled for this router."
	}
else
{
if ($::Form{'arg'} eq '')
	{
	if ($full_tables eq '1')
		{
$command = "show bgp ipv6";
		execute_command($command, $port);
		}
	else
		{
		print "Sorry.  Displaying the FULL routing table would put too much load on the router!\n\n";
		}
	}
else
	{
	execute_command($command, $port);
	}
}
}

############################################################
sub sh_ip_bgp_sum
############################################################
{
if ($bgpd eq '0')
	{
	print "Sorry. The <b>show ip bgp summary</b> command is disabled for this router."
	}
else
{
	my $port = $bgpd;
	my $command = "show ip bgp summary";
	execute_command($command, $port);
}
}

############################################################
sub sh_ip_bgp_plus_sum
############################################################
{
if ($bgpd eq '0')
	{
	print "Sorry. The <b>show ipv6 bgp summary</b> command is disabled for this router."
	}
else
{
	my $port = $bgpd;
	my $command = "show bgp ipv6 summary";
	execute_command($command, $port);
}
}

############################################################
sub sh_ip_ospf
############################################################
{

if ($ospfd eq '0')
	{
	print "Sorry. The <b>show ip ospf</b> command is disabled for this router."
	}
else
	{
	my $port = $ospfd;
	my $command = "show ip ospf $::Form{'arg'}";
	execute_command($command, $port);
}
}

############################################################
sub sh_ip_ospf6
############################################################
{

if ($ospf6d eq '0')
	{
	print "Sorry. The <b>show ipv6 ospf6</b> command is disabled for this router."
	}
else
	{
	my $port = $ospf6d;
	my $command = "show ipv6 ospf $::Form{'arg'}";
	execute_command($command, $port);
}
}

############################################################
sub sh_ip_route
############################################################
{

if ($zebra eq '0')
	{
	print "Sorry. The <b>show ip route</b> command is disabled for this router."
	}
else
{

	my $port = $zebra;
	my $command = "show ip route $::Form{'arg'}";
	if ($::Form{'arg'} eq '')
		{
		if ($full_tables eq '1')
			{
			execute_command($command, $port);
			}
		else
			{
			print "Sorry.  Displaying the FULL routing table would put too much load on the router!\n\n";
			}
		}
	else
		{
		execute_command($command, $port);
		}
	}

}

############################################################
sub sh_ip6_route
############################################################
{

if ($zebra eq '0')
	{
	print "Sorry. The <b>show ipv6 route</b> command is disabled for this router."
	}
else
{

	my $port = $zebra;
	my $command = "show ipv6 route $::Form{'arg'}";
	if ($::Form{'arg'} eq '')
		{
		if ($full_tables eq '1')
			{
			execute_command($command, $port);
			}
		else
			{
			print "Sorry.  Displaying the FULL routing table would put too much load on the router!\n\n";
			}
		}
	else
		{
		execute_command($command, $port);
		}
	}

}

############################################################
sub sh_int
############################################################
{
if ($zebra eq '0')
	{
	print "Sorry. The <b>show interface</b> command is disabled for this router."
	}
else
	{
	my $port = $zebra;
	my $command = "show interface $::Form{'arg'}";
	execute_command($command, $port);
	}
}


############################################################
sub sh_ip_mbgp
############################################################
{
my $port = $bgpd;
my $command;

if ($cisco eq '1')
	{
	$command = "sh ip bgp ipv4 multicast $::Form{'arg'}"; 
	}
else
	{
$command = "show ip bgp ipv4 multicast $::Form{'arg'}";
	}

if ($::Form{'arg'} eq '')
	{
	if ($full_tables eq '1')
		{
			execute_command($command, $port);
		}
	else
		{
		print "Sorry.  Displaying the FULL routing table would put too much load on the router!\n\n";
		}
	}
else
	{
	execute_command($command, $port);
	}
}

############################################################
sub sh_ip_mbgp_sum
############################################################
{

my $port = $bgpd;
my $command;

if ($cisco eq '1')
        {
        $command = "show ip bgp ipv4 multicast summary";
        }
else
        {
$command = "show ip bgp ipv4 multicast summary";
        }
execute_command($command, $port);

}

############################################################
sub traceroute
############################################################
{

    my ($ipaddress, $hostent);

	if ( $::Form{'arg'} =~ /^(([0-9a-zA-Z-\.]+)([\:\.]+)([\:0-9a-zA-Z-\.]+))$/ )
		{ 
		    my $target = $1;

		if ( $cisco eq '1')
			{
			my $port = $bgpd;
			my $command = "traceroute $target";
			print "Traceroute from $::Form{'router'}.<br> \n\n";
			execute_command($command, $port);
			}
		else
			{
	# Some traceroutes, like the NANOG one, need an IP address when 
	# using -s :-(
	$hostent = gethostbyname ($::mrlghost);
	$ipaddress = inet_ntoa (@{$hostent->addr_list}[0]);
	print "Traceroute from $::mrlghost ($ipaddress).<br> \n\n";
	print "Executing command = traceroute $target\n\n";

	select(STDOUT);  $| = 1;
	open(STDERR, '>&STDOUT');# Redirect stderr onto stdout

	alarm(45);

	print "<pre>\n";

	
# Use this one if using standard traceroute.
#	open(TRACEROUTE,"|$::traceroute -s $ipaddress $target");


# Use this one if using ztraceroute included in mrlg package.
	open(TRACEROUTE,"|$::traceroute $target");


	print <TRACEROUTE>;
	close(TRACEROUTE);

	close (STDERR);

	print "</pre>";
	print "Traceroute completed...<br>";

	}

}

	else {

	print "Invalid address!";

	}

}

############################################################
sub ping
############################################################

{

	if ( $::Form{'arg'} =~ /^(([0-9a-zA-Z-\.]+)([\:\.]+)([\:0-9a-zA-Z-\.]+))$/ )
	{ 
	    my ($target) = $1;

		if ( $cisco eq '1')
			{
                        my $port = $bgpd;
                        my $command = "ping $target";
                        print "Ping from $::Form{'router'}.<br> \n\n";
                        execute_command($command, $port);
                        }


		else
			{
                        print "Ping from $::mrlghost.<br> \n\n";
			print "Executing command = fastping2 100 100 $target\n\n";

			select(STDOUT);  $| = 1;
			open(STDERR, '>&STDOUT');

			alarm(45);

			print "<pre>\n";

			open(PING,"|$::ping 100 100 $target");
			print <PING>;
			close(PING);


			close (STDERR);
			print "</pre>";

			print "[Finished]<br>";

			}

	}

	else
	{

	print "Invalid address!";

	}



}

############################################################
sub sh_ip_rip
############################################################
{

if ($ripd eq '0')
	{
	print "Sorry. The <b>show ip rip</b> command is disabled for this router."
	}
else
	{
	my $port = $ripd;
	my $command = "show ip rip $::Form{'arg'}";
	execute_command($command, $port);
}
}

############################################################
sub sh_ip_protocols
############################################################
{

if ($ripd eq '0')
	{
	print "Sorry. The <b>show ip protocols</b> command is disabled for this router."
	}
else
	{
	my $port = $ripd;
	my $command = "show ip protocols $::Form{'arg'}";
	execute_command($command, $port);
}
}


############################################################
sub sh_version
############################################################
{
	my $port = $bgpd;
	my $command = "show version";
	execute_command($command, $port);
}


############################################################
sub execute_command
############################################################
## This code is based on:
##
## Zebra interactive console
## Copyright (C) 2000 Vladimir B. Grebenschikov <vova@express.ru>
##
{
my  ($cmd, $port) = @_;

if ($::log_queries eq '1')
	{
	my ($time);
	$time = localtime;
	open (LOGFILE,">>$::mrlglog");
	print LOGFILE $time, " - ", $ENV{'REMOTE_ADDR'}, ": (", $::Form{'router'}, ") ", $cmd, " \n";
	close LOGFILE;
	}



print "Executing command = $cmd";

my ($prompt, $termlength, $timeout);

if ($cisco eq '1')
        {
	$prompt='/[\>\#]$/';
	$termlength='0';
	$timeout='30';
        }
	else
        {
	$prompt='/[\>\#] $/';
	$termlength='0';
	$timeout='15';
        }


if ($use_ssh eq '1')
	{
	if ($debug eq '1')
		{
		print "<br><br>DEBUG: Protocol = SSH\n";
		print "<br>DEBUG: Server = $server\n";
		if ($::Routers{$::Form{'router'}}{'use_port'})
			{
			print "<br>DEBUG: use_port is SET";
			}
		else
			{
			print "<br>DEBUG: use_port is UNSET";
			}
		print "<br>DEBUG: Port = $port\n";
		print "<br>DEBUG: login_user = $login_user\n";
		print "<br>DEBUG: login_pass = $login_pass<br>\n";
		}

	my $ssh = Net::SSH::Perl->new($server,
					Prompt => $prompt,
					Port => $port,
					Timeout => $timeout);

	$ssh->login($login_user, $login_pass);

	$ssh->cmd("terminal length $termlength");

	if ($cmd)
		{
		my @output = $ssh->cmd($cmd);
		print "<pre>\n";
		print @output;
		print "</pre>\n";
		}
	}
else
	{
	if ($debug eq '1')
		{
		print "<br><br>DEBUG: Protocol = TELNET\n";
		print "<br>DEBUG: Server = $server\n";
		if ($::Routers{$::Form{'router'}}{'use_port'})
			{
			print "<br>DEBUG: use_port is SET";
			}
		else
			{
			print "<br>DEBUG: use_port is UNSET";
			}
		print "<br>DEBUG: Port = $port\n";
		print "<br>DEBUG: login_user = $login_user\n";
		print "<br>DEBUG: login_pass = $login_pass<br>\n";
		}
	my $telnet = Net::Telnet::Cisco->new(
					Host => $server,
					Port => $port,
					Prompt => $prompt,
					Timeout => $timeout);

	$telnet->login(
			Name => $login_user,
			Password => $login_pass);

	$telnet->cmd("terminal length $termlength");

	if ($cmd)
		{
		my @output = $telnet->cmd($cmd);
		print "<pre>\n";
		print @output;
		print "</pre>\n";
		}
	}

}
### The end.  Now, isn't that special?! ###

