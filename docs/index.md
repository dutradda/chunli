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
{!./src/index/index_00_simple_input.test.bash!}
```

Start chunli's job (needs curl [installed](https://curl.haxx.se/docs/install.html)):

```bash
{!./src/index/index_00_simple_input_curl.bash!}
```

```
{!./src/index/index_00_simple_input_curl.bash.output!}
```

Gets chunli's job results:

```bash
{!./src/index/index_00_simple_input_curl2.bash!}
```

```
{!./src/index/index_00_simple_input_curl2.bash.output!}
```


## Ramp-up Example

Running the server

```bash
uvicorn chunli:app
```


Create chunli's input file:

```bash
{!./src/index/index_00_simple_input.test.bash!}
```

Start chunli's job:

```bash
{!./src/index/index_00_rampup_input_curl.bash!}
```

```
{!./src/index/index_00_rampup_input_curl.bash.output!}
```

Gets chunli's job results:

```bash
{!./src/index/index_00_rampup_input_curl2.bash!}
```

```
{!./src/index/index_00_rampup_input_curl2.bash.output!}
```


## Json Lines Example

Running the server:

```bash
uvicorn chunli:app
```


Create chunli's input file:

```bash
{!./src/index/index_01_json_input.test.bash!}
```

Start chunli's job:

```bash
{!./src/index/index_01_json_input_curl.bash!}
```

```
{!./src/index/index_01_json_input_curl.bash.output!}
```

Gets chunli's job results:

```bash
{!./src/index/index_01_json_input_curl2.bash!}
```

```
{!./src/index/index_01_json_input_curl2.bash.output!}
```


## Json Array Lines Example

Running the server:

```bash
uvicorn chunli:app
```


Create chunli's input file:

```bash
{!./src/index/index_02_json_array_input.test.bash!}
```

Start chunli's job:

```bash
{!./src/index/index_02_json_array_input_curl.bash!}
```

```
{!./src/index/index_02_json_array_input_curl.bash.output!}
```

Gets chunli's job results:

```bash
{!./src/index/index_02_json_array_input_curl2.bash!}
```

```
{!./src/index/index_02_json_array_input_curl2.bash.output!}
```


## Python Script Example

Running the server:

```bash
uvicorn chunli:app
```

Create chunli's input script:

```python
# /tmp/get_calls_block.py

{!./src/index/get_calls_block.py!}
```

Start chunli's job:

```bash
{!./src/index/index_03_script_input_curl.bash!}
```

```
{!./src/index/index_03_script_input_curl.bash.output!}
```

Gets chunli's job results:

```bash
{!./src/index/index_03_script_input_curl2.bash!}
```

```
{!./src/index/index_03_script_input_curl2.bash.output!}
```


## Python Script With Body Example

Running the server:

```bash
uvicorn chunli:app
```

Create chunli's input script:

```python
# /tmp/get_calls_block_body.py

{!./src/index/get_calls_block_body.py!}
```

Start chunli's job:

```bash
{!./src/index/index_04_script_body_input_curl.bash!}
```

```
{!./src/index/index_04_script_body_input_curl.bash.output!}
```

Gets chunli's job results:

```bash
{!./src/index/index_04_script_body_input_curl2.bash!}
```

```
{!./src/index/index_04_script_body_input_curl2.bash.output!}
```
