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
    -i 'http://localhost:8000/run?duration=3&rps_per_node=1' \
    --upload-file /tmp/hello-call.gz

```

```
HTTP/1.1 100 Continue

HTTP/1.1 202 Accepted
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 159

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running","signature":"73b40a62fb5e","args_signature":null}

```

Gets chunli's job results:

```bash
sleep 5 && \
    curl -i 'http://localhost:8000/run?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":1.0,"rampup_time":0,"requested_rps_per_node":1.0,"realized_requests":1.0,"realized_rps":1.0,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1,"errors_count":0},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished","signature":"73b40a62fb5e","args_signature":null}

```


## Ramp-up Example

Running the server

```bash
uvicorn chunli:app
```


Create chunli's input file:

```bash
echo http://localhost:8001/hello | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz

```

Start chunli's job:

```bash
curl -X POST \
    -i 'http://localhost:8000/run?duration=10&rps_per_node=10&rampup_time=5' \
    --upload-file /tmp/hello-call.gz

```

```
HTTP/1.1 100 Continue

HTTP/1.1 202 Accepted
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 159

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running","signature":"73b40a62fb5e","args_signature":null}

```

Gets chunli's job results:

```bash
sleep 12 && \
    curl -i 'http://localhost:8000/run?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":10.0,"rampup_time":5,"requested_rps_per_node":10.0,"realized_requests":73.0,"realized_rps":7.3,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1,"errors_count":0},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished","signature":"73b40a62fb5e","args_signature":null}

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
    -i 'http://localhost:8000/run?duration=1&rps_per_node=10' \
    --upload-file /tmp/hello-call.gz

```

```
HTTP/1.1 100 Continue

HTTP/1.1 202 Accepted
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 159

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running","signature":"73b40a62fb5e","args_signature":null}

```

Gets chunli's job results:

```bash
sleep 3 && \
    curl -i 'http://localhost:8000/run?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":1.0,"rampup_time":0,"requested_rps_per_node":1.0,"realized_requests":1.0,"realized_rps":1.0,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1,"errors_count":0},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished","signature":"73b40a62fb5e","args_signature":null}

```


## Json Array Lines Example

Running the server:

```bash
uvicorn chunli:app
```


Create chunli's input file:

```bash
echo '[{"url":"http://localhost:8001/hello"}]
[{"url":"http://localhost:8001/hello","method":"GET"}]
' \
    | gzip > /tmp/hello-call.gz

zcat /tmp/hello-call.gz

```

Start chunli's job:

```bash
curl -X POST \
    -i 'http://localhost:8000/run?duration=1&rps_per_node=10' \
    --upload-file /tmp/hello-call.gz

```

```
HTTP/1.1 100 Continue

HTTP/1.1 202 Accepted
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 159

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running","signature":"73b40a62fb5e","args_signature":null}

```

Gets chunli's job results:

```bash
sleep 3 && \
    curl -i 'http://localhost:8000/run?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":1.0,"rampup_time":0,"requested_rps_per_node":1.0,"realized_requests":1.0,"realized_rps":1.0,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1,"errors_count":0},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished","signature":"73b40a62fb5e","args_signature":null}

```


## Python Script Example

Running the server:

```bash
uvicorn chunli:app
```

Create chunli's input script:

```python
# /tmp/get_calls_block.py

from typing import Generator

from chunli.call import Call


global get_calls_block


def get_calls_block() -> Generator[Call, None, None]:
    yield Call(
        url='http://localhost:8001/hello',
        method='GET',
        headers=None,
        body=None,
    )

```

Start chunli's job:

```bash
curl -X POST \
    -i 'http://localhost:8000/script?duration=1&rps_per_node=10' \
    --upload-file /tmp/get_calls_block.py

```

```
HTTP/1.1 100 Continue

HTTP/1.1 202 Accepted
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 159

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running","signature":"0ecc7ebf73bc","args_signature":null}

```

Gets chunli's job results:

```bash
sleep 3 && \
    curl -i 'http://localhost:8000/script?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":1.0,"rampup_time":0,"requested_rps_per_node":1.0,"realized_requests":1.0,"realized_rps":1.0,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1,"errors_count":0},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished","signature":"0ecc7ebf73bc","args_signature":null}

```


## Python Script With Body Example

Running the server:

```bash
uvicorn chunli:app
```

Create chunli's input script:

```python
# /tmp/get_calls_block_body.py

from typing import Generator

from chunli.call import Call


global get_calls_block


def get_calls_block() -> Generator[Call, None, None]:
    yield Call(
        url='http://localhost:8001/hello-body',
        method='POST',
        headers=None,
        body={'name': 'Me!'},
    )

```

Start chunli's job:

```bash
curl -X POST \
    -i 'http://localhost:8000/script?duration=1&rps_per_node=10' \
    --upload-file /tmp/get_calls_block_body.py

```

```
HTTP/1.1 100 Continue

HTTP/1.1 202 Accepted
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 159

{"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"running","signature":"0ecc7ebf73bc","args_signature":null}

```

Gets chunli's job results:

```bash
sleep 3 && \
    curl -i 'http://localhost:8000/script?task_id=4ee301eb-6487-48a0-b6ed-e5f576accfc2'

```

```
HTTP/1.0 200 OK
date: Thu, 1st January 1970 00:00:00 GMT
server: uvicorn
content-type: application/json
content-length: 409

{"end_time":"1970-01-01T00:00:00+00:00","result":{"duration":1.0,"rampup_time":0,"requested_rps_per_node":1.0,"realized_requests":1.0,"realized_rps":1.0,"latency":{"mean":1.0,"median":1.0,"percentile99":1.0,"percentile95":1.0},"error":null,"nodes_quantity":1,"errors_count":0},"task_id":"4ee301eb-6487-48a0-b6ed-e5f576accfc2","start_time":"1970-01-01T00:00:00+00:00","status":"finished","signature":"0ecc7ebf73bc","args_signature":null}

```
