curl -X POST \
    -i "localhost:8000/start?duration=2s&rps_per_node=100&uuid=uuid.uuid4" \
    --upload-file=/tmp/hello-call.gz
