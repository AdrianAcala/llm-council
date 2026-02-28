# Frontend Dockerfile for LLM Council
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose the Vite dev server port
EXPOSE 5173

# Start the development server
# --host 0.0.0.0 allows external connections
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
