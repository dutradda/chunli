echo '{"url":"http://localhost:8000/hello"}
{"url":"http://localhost:8000/hello","method":"POST","body":"World"}' \
    | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz
