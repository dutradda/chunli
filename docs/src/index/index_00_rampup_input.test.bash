echo http://localhost:8001/hello | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz
