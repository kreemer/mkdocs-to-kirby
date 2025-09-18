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

@test "Creating page with sections" {
    testDir=${fixturesDir}/ok-mkdocs-sections
    cd ${testDir}
    generate_silent_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_dir_exists "kirby-content/0_section1"
    assert_dir_exists "kirby-content/1_section2"
}


@test "Creating page with sections which are not listed" {
    testDir=${fixturesDir}/ok-mkdocs-sections
    cd ${testDir}
    generate_silent_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_dir_exists "kirby-content/section3"
}
