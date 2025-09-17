#!/usr/bin/env bats
rootDir=$(pwd)
fixturesDir=${rootDir}/examples
testDir=''

setup() {
    load testsuite
    _common_setup
}

teardown() {
    if [ -z "${testDir}" ]; then
        return
    fi
    _common_teardown ${testDir}
}

##
# Test suites.
#


@test "Simple page not empty" {
    testDir=${fixturesDir}/ok-mkdocs-single
    cd ${testDir}
    generate_silent_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/doc.md"

    run cat kirby-content/doc.md
    assert_output --stdin <<EOF
Title: Home

----

Text: # Home

Hello
EOF
}


@test "Simple page with title from metadata" {
    testDir=${fixturesDir}/ok-mkdocs-simple
    cd ${testDir}
    generate_silent_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/0_listed_section/1_page2/doc.md"

    run cat kirby-content/0_listed_section/1_page2/doc.md
    assert_success
    assert_output --stdin <<EOF
Title: Page-2

----

Text:
EOF
}
