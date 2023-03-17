AWS_PROFILE=pol-acc invoke hrv.dump-data localhost -d gamma
read -n 1 -r -s -p $'Press enter to continue... or Ctrl-C\n'
invoke hrv.setup-postgres
read -n 1 -r -s -p $'Press enter to continue... or Ctrl-C\n'
AWS_PROFILE=pol-acc invoke hrv.load-data localhost -s acceptance -d gamma
