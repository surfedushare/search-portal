invoke aws.build service
invoke aws.push service --docker-login
APPLICATION_MODE=development invoke aws.promote service
APPLICATION_MODE=development invoke aws.migrate service development
APPLICATION_MODE=development invoke srv.deploy development
