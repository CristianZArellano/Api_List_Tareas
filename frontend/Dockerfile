# frontend/Dockerfile
# Etapa 1: Build de la app
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --production=false
COPY . .
RUN npm run build

# Etapa 2: Imagen final con Nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Opcional: archivo de salud
COPY public/healthcheck.html /usr/share/nginx/html/healthcheck.html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 