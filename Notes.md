rabbit-AMQP  = 5672
rabbit-Web-based management UI = 15672
error will be on port 8078
lock MS on port 8079
<!-- Leaving this here for reference
Dahai: rabbit and error need to start 1st
Dahai: then compos will start last
Dahai: followed by the frontend
 -->

 <!-- Error Logging not implemented in
 - email
 - lock
 - payment service
 - rabbitmq
 - telegram
  -->

Atomic Microservice

rabbitMQ will be on port 8078
error will be on port 8079
lock MS on port 8080
testlock MS on port 8080

guest MS on port 8082
staff MS on port 8083
logs MS on port 8084
email MS on port 8088

stripeservice MS on port 8086

rabbit_port = 5672

compositi
notification MS on port 8080
composite
telegram MS on port 8081
enter_park MS on port 8085
payment MS on port 8087


frontend will be on port 8100
OTP service will be on Outsystems