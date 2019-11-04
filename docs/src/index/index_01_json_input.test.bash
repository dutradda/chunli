echo '{"url":"http://localhost:8001/hello"}
{"url":"http://localhost:8001/hello","method":"GET"}' \
    | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz
