curl -X POST \
    -i 'http://localhost:8000/run?duration=3&rps_per_node=1' \
    --upload-file /tmp/hello-call.gz
