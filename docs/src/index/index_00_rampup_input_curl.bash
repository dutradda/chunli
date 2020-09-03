curl -X POST \
    -i 'http://localhost:8000/run?duration=10&rps_per_node=10&rampup_time=5' \
    --upload-file /tmp/hello-call.gz
