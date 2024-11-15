FROM node:lts-alpine

# install simple http server for serving static content

# make the '/app/frontend' folder the current working directory
WORKDIR /app/frontend

# install bash (needed for Git in dev container)
RUN apk add --no-cache bash

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . /app/frontend/

# run development server (needs --host flag in package.json --> scripts --> dev )

EXPOSE 3000

CMD [ "npm", "run", "dev" ]