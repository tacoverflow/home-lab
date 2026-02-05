# Stage 1: building the binary
FROM golang:1.25.4-alpine3.22 AS BUILD
COPY src /opt/src
WORKDIR /opt/src
RUN go mod tidy
RUN go build -o node-janitor

# Stage 2: packaging the binary
FROM golang:1.25.4-alpine3.22
COPY --from=BUILD --chmod=755 /opt/src/node-janitor /bin/node-janitor
CMD /bin/node-janitor

