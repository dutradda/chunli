curl -X POST \
    -i 'http://localhost:8000/run?duration=1&rps_per_node=10' \
    --upload-file /tmp/hello-call.gz
