AWS_PROFILE=pol-prod invoke hrv.dump-data localhost -d gamma
read -n 1 -r -s -p $'Press enter to continue... or Ctrl-C\n'
invoke hrv.setup-postgres
read -n 1 -r -s -p $'Press enter to continue... or Ctrl-C\n'
AWS_PROFILE=pol-prod invoke hrv.load-data localhost -s production -d gamma
