# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
# FROM node:26 AS build-stage

# WORKDIR /app

# COPY ./frontend/package*.json /app/

# RUN npm install

# COPY ./frontend /app/

# RUN npm run build

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1  AS final-stage

# COPY --from=build-stage /app/dist/ /usr/share/nginx/html

# Copy the custom nginx.conf to the container
COPY ./nginx.conf /etc/nginx/conf.d/app.conf
