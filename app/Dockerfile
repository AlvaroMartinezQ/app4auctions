# develop stage
FROM node:18 as develop-stage

ENV TZ="Europe/Madrid"
ENV TIME_ZONE="Europe/Madrid"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
COPY package*.json ./
RUN npm install -g @quasar/cli
COPY . .

# build stage
FROM develop-stage as build-stage
RUN npm install
RUN quasar build

# production stage
FROM nginx:stable-alpine as production-stage
ADD nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
