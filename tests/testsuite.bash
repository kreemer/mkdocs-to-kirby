#!/usr/bin/env bash

_common_setup() {
    load 'test_helper/bats-support/load'
    load 'test_helper/bats-assert/load'
    load 'test_helper/bats-file/load'
}

_common_teardown() {
    echo "Teardown"
    dir=$1
    echo "Cleaning ${dir}"
    rm -rf ${dir}/site/
    rm -f ${dir}/mkdocs.yml
    if [ -f "${dir}/clean.sh" ]; then
        ${dir}/clean.sh
    fi
}
debugger() {
    echo "--- STATUS ---"
    if [ $status -eq 0 ]
    then
        echo "Successful Status Code ($status)"
    else
        echo "Failed Status Code ($status)"
    fi
    echo "--- OUTPUT ---"
    printf '%s\n' "${lines[@]}"
    echo "--------------"
    echo "--- CONFIG ---"
    cat mkdocs.yml
    echo "--------------"
    echo "--- FILES ----"
    tree .
    echo "--------------"
}

generate_mkdocs_site() {
    if [ -f mkdocs-test.yml ]
    then
        cp mkdocs-test.yml mkdocs.yml
    fi
    run mkdocs build --verbose
    debugger
    [ "$status" -eq 0 ]
}

generate_silent_mkdocs_site() {
    if [ -f mkdocs-test.yml ]
    then
        cp mkdocs-test.yml mkdocs.yml
    fi
    run mkdocs build -q
    debugger
    [ "$status" -eq 0 ]
}

assert_not_empty_site() {
    assert_file_exists site/index.html
}

assert_empty_site() {
    assert_file_not_exists site/index.html
}

assert_serve_success() {
    run pgrep -x mkdocs
    debugger
    [ ! -z "$status" ]
}

assert_par_grep() {
    cat site/$1/index.html | \
        awk '/<div class="col-md-9" role="main">/,/<footer class="col-md-12">/' | \
        sed '1d; $d'  | head -n -3 > site/$1.grepout
    echo "--------------"
    echo "-----File-----"
    echo `pwd`/site/$1/index.html
    echo "-----Grep results-----"
    run diff --ignore-blank-lines --ignore-all-space $1.grepout site/$1.grepout
    echo "-----Output-----"
    cat site/$1.grepout
    echo "--------------"
    [ "$status" -eq 0 ]
}

check_site_name() {
    site_name=$(cat mkdocs.yml | sed -n 's/site_name: \(.*\)/\1/p')
    directory_name=${PWD##*/}
    echo "mkdocs site_name: $site_name, directory: $directory_name"
    [ "$site_name" == "$directory_name" ]
}
