curl -X POST \
    -i 'localhost:8000/script?duration=1&rps_per_node=10' \
    --upload-file /tmp/get_calls_block_body.py
