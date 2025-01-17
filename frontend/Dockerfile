# Development Dockerfile for React app
FROM node:22

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./

RUN npm install

# Copy the entire project
COPY ./ /app

# # Expose port 5173 (or the port your development server uses)
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev"]

# # Step 1: Use official Node.js image as the base image
# FROM node:18-alpine

# # Step 2: Set the working directory
# WORKDIR /app

# # Step 3: Copy package.json and package-lock.json (or yarn.lock) to the container
# COPY package*.json ./

# # Step 4: Install dependencies
# RUN npm install

# # Step 5: Copy the rest of the application code to the container
# COPY . .

# # Step 6: Expose the port for the React app (default is 3000)
# EXPOSE 3000

# # Step 7: Start the app
# CMD ["npm", "run", "dev"]