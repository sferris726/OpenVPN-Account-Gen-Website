#!/usr/bin/expect -f

set timeout -1

spawn su server
expect {Password:} {send "server\n"}

cd /var/www/FlaskApps/client-configs/

spawn /var/www/FlaskApps/client-configs/genClientCerts.sh
#expect {Enter pass phrase for client.key:} {send "client\n"}
#expect {Verifying - Enter pass phrase for client.key:} {send "client\n"}
#expect {Enter pass phrase for client.key:} {send "client\n"}
expect -re {Country Name \(2 letter code\) [^:]*:} {send "\n"}
expect -re {State or Province Name \(full name\) [^:]*:} {send "\n"}
expect -re {Locality Name \(eg, city\) [^:]*:} {send "\n"}
expect -re {Organization Name \(eg, company\) [^:]*:} {send "\n"}
expect -re {Organizational Unit Name \(eg, section\) [^:]*:} {send "\n"}
expect -re {Common Name \(e.g. server FQDN or YOUR name\) [^:]*:} {send "client\n"}
expect -re {Email Address [^:]*:} {send "\n"}
expect -re {A challenge password [^:]*:} {send "\n"}
expect -re {An optional company name [^:]*:} {send "\n"}
expect eof

cd /var/www/FlaskApps/client-configs/

spawn /var/www/FlaskApps/client-configs/CASign.sh
expect {Enter pass phrase for ca.key:} {send "cert\n"}
expect eof
