echo \
'{"url":"http://localhost:8000/hello","headers":{"x-uuid":"$uuid"}}' \
    | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz
