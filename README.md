# chunli

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/chunli">
    <img src="https://dutradda.github.io/chunli/chunli.gif" alt="chunli" width="300"/>
  </a>
</p>

<p align="center">
    <em>Distributed load test application</em>
</p>

---

**Documentation**: <a href="https://dutradda.github.io/chunli" target="_blank">https://dutradda.github.io/chunli</a>

**Source Code**: <a href="https://github.com/dutradda/chunli" target="_blank">https://github.com/dutradda/chunli</a>

---


## Key Features

- Distributed load test application
- Receive file with urls
- Receive file with json lines
- Receive python scripts *

*\* feature in development.*


## Requirements

 - Python 3.8+


## Instalation
```
$ pip install chunli
```


## Basic Example

Running the server (needs uvicorn [installed](https://www.uvicorn.org)):

```bash
uvicorn chunli:app
```


Create chunli's input file (needs gzip [installed](https://www.gzip.org)):

```bash
echo http://localhost:8001/hello | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz

```

Start chunli's job (needs curl [installed](https://curl.haxx.se/docs/install.html)):

```bash
curl -X POST \
    -i 'localhost:8000/run?duration=1&rps_per_node=10' \
    --upload-file /tmp/hello-call.gz

```

```
HTTP/1.1 100 Continue

HTTP/1.1 201 Created
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 110

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running"}

```

Gets chunli's job results:

```bash
sleep 2 && \
    curl -i 'localhost:8000/run?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":1.0,"requested_rps_per_node":1.0,"realized_requests":1.0,"realized_rps":1.0,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished"}

```


## Json Lines Example

Running the server:

```bash
uvicorn chunli:app
```


Create chunli's input file:

```bash
echo '{"url":"http://localhost:8001/hello"}
{"url":"http://localhost:8001/hello","method":"GET"}' \
    | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz

```

Start chunli's job:

```bash
curl -X POST \
    -i 'localhost:8000/run?duration=1&rps_per_node=10' \
    --upload-file /tmp/hello-call.gz

```

```
HTTP/1.1 100 Continue

HTTP/1.1 201 Created
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 110

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running"}

```

Gets chunli's job results:

```bash
sleep 2 && \
    curl -i 'localhost:8000/run?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":1.0,"requested_rps_per_node":1.0,"realized_requests":1.0,"realized_rps":1.0,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished"}

```
