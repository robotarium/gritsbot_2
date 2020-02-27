if [[ $1 -eq 0 ]] ; then
    echo 'Please provide the number of working robots on the testbed.'
    exit 0
fi

sudo python3 get_ip_by_mac.py ../config/mac_list.json wlp5s0 -c "./restart_docker.sh" -n $1
