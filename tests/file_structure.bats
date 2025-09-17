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

@test "build an empty mkdocs site with minimal configuration" {
    testDir=${fixturesDir}/ok-mkdocs-empty
    cd ${testDir}
    generate_mkdocs_site
    assert_empty_site
}

@test "build an mkdocs site with configuration" {
    testDir=${fixturesDir}/ok-mkdocs-config
    cd ${testDir}
    generate_mkdocs_site
    assert_empty_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/doc.md"
}

@test "build an mkdocs site with configuration and index page" {
    testDir=${fixturesDir}/ok-mkdocs-single
    cd ${testDir}
    generate_mkdocs_site
    assert_not_empty_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/doc.md"
}

@test "build an mkdocs site plugin and simple pages" {
    testDir=${fixturesDir}/ok-mkdocs-simple
    cd ${testDir}
    generate_mkdocs_site
    assert_not_empty_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/doc.md"
    assert_dir_exists "kirby-content/0_listed_section"
    assert_file_exists "kirby-content/0_listed_section/doc.md"
    assert_dir_exists "kirby-content/0_listed_section/1_page2"
    assert_file_exists "kirby-content/0_listed_section/1_page2/doc.md"
    assert_dir_exists "kirby-content/0_listed_section/2_page1"
    assert_file_exists "kirby-content/0_listed_section/2_page1/doc.md"
    assert_dir_exists "kirby-content/0_listed_section/unlisted"
    assert_file_exists "kirby-content/0_listed_section/unlisted/doc.md"
    assert_dir_exists "kirby-content/unlisted_section"
    assert_file_exists "kirby-content/unlisted_section/doc.md"
    assert_dir_exists "kirby-content/unlisted_section/0_hello"
    assert_file_exists "kirby-content/unlisted_section/0_hello/doc.md"
    assert_dir_exists "kirby-content/invisible_section"
    assert_file_exists "kirby-content/invisible_section/doc.md"
    assert_dir_exists "kirby-content/invisible_section/test"
    assert_file_exists "kirby-content/invisible_section/test/doc.md"
}

@test "build an mkdocs site plugin and defined language" {
    testDir=${fixturesDir}/ok-mkdocs-language
    cd ${testDir}
    generate_mkdocs_site
    assert_not_empty_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/doc.en.md"
}
