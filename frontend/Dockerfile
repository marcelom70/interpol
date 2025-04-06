FROM node:18 AS build
WORKDIR /app
ENV VITE_BACKEND_URL=163.172.160.209
COPY . .
RUN npm install && npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
