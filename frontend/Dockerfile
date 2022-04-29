FROM nginx:1.21.6-alpine
COPY frontend/build /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

CMD if [ "$PORT" ]; then sed -i -e 's/$PORT/'"$PORT"'/g' /etc/nginx/conf.d/default.conf; else sed -i -e 's/$PORT/'80'/g' /etc/nginx/conf.d/default.conf; fi && nginx -g 'daemon off;'