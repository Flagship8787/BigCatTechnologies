# Stage 1: Build
FROM node:20-slim AS builder

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

ARG VITE_AUTH0_DOMAIN
ENV VITE_AUTH0_DOMAIN=${VITE_AUTH0_DOMAIN}

ARG VITE_AUTH0_CLIENT_ID
ENV VITE_AUTH0_CLIENT_ID=${VITE_AUTH0_CLIENT_ID}

ARG VITE_AUTH0_AUDIENCE
ENV VITE_AUTH0_AUDIENCE=${VITE_AUTH0_AUDIENCE}

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
