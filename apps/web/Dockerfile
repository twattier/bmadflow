FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start development server (listen on 0.0.0.0 for Docker)
# Use exec to replace shell with vite process for proper signal handling
CMD ["sh", "-c", "echo 'Starting Vite server...' && exec npx vite --host 0.0.0.0 2>&1"]
