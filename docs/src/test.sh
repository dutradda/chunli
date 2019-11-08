#!/bin/bash

echo -e '\n---------------------------------------'
echo -e 'Running examples outputs assertion...\n'

source ${VIRTUAL_ENV}/bin/activate

test_path=$(dirname ${BASH_SOURCE[0]})
test_regex="s%${test_path}/[^/]+/(.*)\.test.bash%\1%g"
test_files="$(find ${test_path}/**/*.test.bash)"
md5_cmd=$(which md5sum >/dev/null 2>&1 && echo md5sum || echo 'md5 -r')


for filepath in ${test_files}; do
    filename=$(echo ${filepath} | sed -r -e ${test_regex})
    test_dir=$(dirname ${filepath})
    curl_file=${test_dir}/${filename}_curl.bash 
    output_tmpfile=/tmp/${filename}.output
    output_file=${curl_file}.output
    checksum_file=/tmp/${filename}.checksum
    curl_file2=${test_dir}/${filename}_curl2.bash 
    tmp_curl_file2=/tmp/${filename}_curl2.bash 
    output_file2=${curl_file2}.output
    output_tmpfile2=/tmp/${filename}2.output
    checksum_file2=/tmp/${filename}2.checksum
    date_regex="^date: .*"
    date_sub="date: Thu, 1st January 1970 00:00:00 GMT"
    task_time_regex='"(start|end)_time":"[0-9T:+-]+"'
    task_time_sub='"\1_time":"1970-01-01T00:00:00+00:00"'
    task_id_regex='.*"task_id":"([0-9a-z-]+)".*'
    task_id_sub='\1'
    uvicorn_output_file=/tmp/uvicorn-${filename}.output
    uvicorn_hello_output_file=/tmp/uvicorn-index_hello_app.output
    test_module=$(echo ${filepath} | tr '/' '.' | sed -r -e 's/\.py//g')
    PYTHONPATH=${test_dir}:${PYTHONPATH}

    echo Testing ${filename}..
    coverage run -p $(which gunicorn) chunli:app -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py >${uvicorn_output_file} 2>&1 &
    coverage run -p $(which uvicorn) --port 8001 index_hello_app:app \
        >${uvicorn_hello_output_file} 2>&1 &
    sleep 5

    bash ${test_dir}/${filename}.test.bash >/dev/null 2>&1

    bash ${curl_file} 2>/dev/null | \
        sed -r -e "s/${date_regex}/${date_sub}/g" \
            -e "s/${task_time_regex}/${task_time_sub}/g" \
            -e '$ s/(.*)/\1\n/g' > ${output_tmpfile}
    task_id=$(\
        cat ${output_tmpfile} | \
        grep -E "${task_id_regex}" | \
        sed -r -e "s/.*${task_id_regex}.*/${task_id_sub}/g" \
    )
    sed ${output_tmpfile} -i -r -e \
        "s/${task_id}/4ee301eb-6487-48a0-b6ed-e5f576accfc2/g" 2>/dev/null
    $md5_cmd ${output_file} ${output_tmpfile} > ${checksum_file}

    cp ${curl_file2} ${tmp_curl_file2}
    sed ${tmp_curl_file2} -i -r -e \
        "s/4ee301eb-6487-48a0-b6ed-e5f576accfc2/${task_id}/g" 2>/dev/null
    bash ${tmp_curl_file2} 2>/dev/null | \
        sed -r -e "s/${date_regex}/${date_sub}/g" \
            -e "s/${task_time_regex}/${task_time_sub}/g" \
            -e '$ s/(.*)/\1\n/g' > ${output_tmpfile2}
    sed ${output_tmpfile2} -i -r \
        -e "s/${task_id}/4ee301eb-6487-48a0-b6ed-e5f576accfc2/g" \
        -e "s/content-length: 4[0-9]{2}/content-length: 409/g" \
        -e 's/[0-9]+\.[0-9]+/1.0/g' 2>/dev/null

    $md5_cmd ${output_file2} ${output_tmpfile2} > ${checksum_file2}

    ps ax | (ps ax | awk "/uvicorn index_hello_app:app/ {print \$1}" | xargs kill -SIGTERM 2>/dev/null)
    ps ax | (ps ax | awk "/gunicorn chunli:app/ {print \$1}" | xargs kill -SIGTERM 2>/dev/null)

    output=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file} | uniq | wc -l)

    if ! [ ${output} -eq 1 ]; then
        echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
        diff -u ${output_file} ${output_tmpfile}
        echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
        cat ${uvicorn_output_file}
        exit 1
    fi

    output2=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file2} | uniq | wc -l)

    if ! [ ${output2} -eq 1 ]; then
        echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
        diff -u ${output_file2} ${output_tmpfile2}
        echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
        cat ${uvicorn_output_file}
        exit 1
    fi

    echo OK
done

echo 'Docs examples outputs assertion passed!'
echo -e '---------------------------------------\n'
