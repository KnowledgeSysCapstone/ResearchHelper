# Use Node.js image
FROM node:18-alpine AS base

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy app files
COPY . .

# Build Next.js app
RUN npm run build

# Expose frontend port
EXPOSE 3000

CMD ["npm", "run", "start"]
