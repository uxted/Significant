FROM node:18-alpine

WORKDIR /app

# Copy package files first for Docker layer caching
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose React dev server port
EXPOSE 3000

# Start React development server
CMD ["npm", "start"]
