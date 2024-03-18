FROM node:16-alpine as DIST
WORKDIR /web
COPY frontend .
RUN npm install --registry=https://registry.npmmirror.com -g yarn --force \
    && yarn install --registry=https://registry.npmmirror.com \
    && yarn build

FROM nginx:1.21-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY ./deployment/web/nginx.conf /etc/nginx/conf.d/lunar_link.conf
COPY ./backend/static_root  /www/LunarLink/static
COPY --from=DIST /web/dist /usr/share/nginx/html
