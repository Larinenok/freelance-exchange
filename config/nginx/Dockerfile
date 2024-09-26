FROM nginx:1.24
 
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
 
# ADD ./config/nginx/uwsgi_params /etc/nginx/
ADD ./config/nginx/proxy_params /etc/nginx/
ADD ./config/nginx/nginx.conf /etc/nginx/conf.d/default.conf
