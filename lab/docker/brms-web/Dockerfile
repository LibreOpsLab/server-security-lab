# The Boab Ridge website as one image: Eleventy builds the pages, then nginx serves them.
# Build context is this folder (lab/docker/brms-web). LAB_DOMAIN decides the email domain printed on the site.
FROM node:22-alpine AS build
WORKDIR /build
COPY site/package.json site/package-lock.json ./
RUN npm ci
COPY site/ ./
ARG LAB_DOMAIN=boab.lab
ENV LAB_DOMAIN=${LAB_DOMAIN}
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /build/_site /usr/share/nginx/html
