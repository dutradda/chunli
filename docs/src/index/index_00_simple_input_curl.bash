curl -X POST \
    -i 'localhost:8000/run?duration=2&rps_per_node=10' \
    --upload-file /tmp/hello-call.gz
