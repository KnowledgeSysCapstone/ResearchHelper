# Use Node.js image on recent alpine 3.21.
FROM node:20-alpine3.21

# Set working directory to /app.
WORKDIR /app

# Install dependencies front next.js packages.
COPY package.json package-lock.json ./
RUN npm install

# Copy app files.
COPY . .

# Build Next.js app
RUN npm run build

# Expose frontend port
EXPOSE 3000

CMD ["npm", "run", "start"]
