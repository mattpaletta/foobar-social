FROM grpc/php:latest

WORKDIR web_client

COPY www /var/www/html
COPY src /usr/local/lib/php/src 
COPY vendor /usr/local/lib/php/vendor
COPY  php.ini /usr/local/etc/php

CMD ["apache2ctl", "-DFOREGROUND"]
