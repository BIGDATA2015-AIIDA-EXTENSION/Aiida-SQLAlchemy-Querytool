#!/usr/bin/env bash

script="query.py"
command="python query.py"

function create_command() {
    version="$1"
    query="$2"

    ret="$command $version $query"
    echo $ret
}

function restart_pgsql() {
    # Assume you use a debian based system.
    sudo service postgresql restart
}

for v in "old" "new"; do
    echo $v
    for n in `seq 1 4`; do
        echo $n
        restart_pgsql
        echo -n "["
        for i in `seq 1 10`; do
            c=$(create_command $v $n)
            res=$($c)
            echo -n "$res"
            if [[ $i -lt 10 ]]; then
                echo -n ", "
            fi
        done
        echo "]"
    done
done


