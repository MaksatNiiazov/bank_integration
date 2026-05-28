FROM node:22-alpine

WORKDIR /workspace

COPY turkuaz-ui/package.json ./turkuaz-ui/package.json
COPY turkuaz-ui/src ./turkuaz-ui/src
COPY identity-service/frontend/.npmrc ./identity-service/frontend/.npmrc
COPY identity-service/frontend/package.json identity-service/frontend/package-lock.json* ./identity-service/frontend/

WORKDIR /workspace/identity-service/frontend
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY identity-service/frontend ./

EXPOSE 5177

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5177"]
