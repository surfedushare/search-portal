invoke aws.build service
invoke aws.push service --docker-login
APPLICATION_MODE=acceptance invoke aws.promote service
APPLICATION_MODE=acceptance invoke aws.migrate service acceptance
APPLICATION_MODE=acceptance invoke srv.deploy acceptance
