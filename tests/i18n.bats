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


@test "Creating page with i18n plugin index pages" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_silent_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/doc.de.md"

    run cat kirby-content/doc.de.md
    assert_output --stdin <<EOF
Title: Start

----

Text:

# Start
EOF
    assert_file_exists "kirby-content/doc.en.md"
    run cat kirby-content/doc.en.md
    assert_output --stdin <<EOF
Title: Home

----

Text:

# Home
EOF
}


@test "Creating page with i18n plugin custom pages" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_silent_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/0_page1/doc.de.md"

    run cat kirby-content/0_page1/doc.de.md
    assert_output --stdin <<EOF
Title: seite1

----

Text:

Deutsch
EOF
    assert_file_exists "kirby-content/0_page1/doc.en.md"
    run cat kirby-content/0_page1/doc.en.md
    assert_output --stdin <<EOF
Title: page1

----

Text:

English
EOF
}


@test "Creating page with i18n plugin links are correct" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_silent_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/1_page2/doc.de.md"

    run cat kirby-content/1_page2/doc.de.md
    assert_output --stdin <<EOF
Title: page2

----

Text:

[here](../page1)
EOF
    assert_file_exists "kirby-content/1_page2/doc.en.md"
    run cat kirby-content/1_page2/doc.en.md
    assert_output --stdin <<EOF
Title: page2

----

Text:

[here](../page1)
EOF
}

@test "Creating page with i18n plugin wrongfully links are correct" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/2_page3/doc.de.md"

    run cat kirby-content/2_page3/doc.de.md
    assert_output --stdin <<EOF
Title: page3

----

Text:

[hier](../page1)
EOF
    assert_file_exists "kirby-content/2_page3/doc.en.md"
    run cat kirby-content/2_page3/doc.en.md
    assert_output --stdin <<EOF
Title: page3

----

Text:

[here](../page1)
EOF
}


@test "Creating page with i18n plugin section pages are rendered" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/3_section/doc.de.md"

    run cat kirby-content/3_section/doc.de.md
    assert_output --stdin <<EOF
Title: Section

----

Text:

Test
EOF
    assert_file_exists "kirby-content/3_section/doc.en.md"
    run cat kirby-content/3_section/doc.en.md
    assert_output --stdin <<EOF
Title: Section

----

Text:

Test
EOF
}


@test "Creating page with i18n plugin section custom pages are rendered" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/3_section/0_page4/doc.de.md"

    run cat kirby-content/3_section/0_page4/doc.de.md
    assert_output --stdin <<EOF
Title: seite4

----

Text:

Hallo
EOF
    assert_file_exists "kirby-content/3_section/0_page4/doc.en.md"
    run cat kirby-content/3_section/0_page4/doc.en.md
    assert_output --stdin <<EOF
Title: page4

----

Text:

Hello
EOF
}



@test "Creating page with i18n plugin section assets are correctly copied" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/3_section/1_page5/doc.de.md"

    run cat kirby-content/3_section/1_page5/doc.de.md
    assert_output --stdin <<EOF
Title: page5

----

Text:

![image](image.png)
EOF
    assert_file_exists "kirby-content/3_section/1_page5/doc.en.md"
    run cat kirby-content/3_section/1_page5/doc.en.md
    assert_output --stdin <<EOF
Title: page5

----

Text:

![image](image.png)
EOF
    assert_file_exists "kirby-content/3_section/1_page5/image.png"
}

@test "Creating page with i18n plugin section translated assets are correctly copied" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/3_section/2_page6/doc.de.md"

    run cat kirby-content/3_section/2_page6/doc.de.md
    assert_output --stdin <<EOF
Title: seite6

----

Text:

![bild](image_de.png)
EOF
    assert_file_exists "kirby-content/3_section/2_page6/image_de.png"

    assert_file_exists "kirby-content/3_section/2_page6/doc.en.md"
    run cat kirby-content/3_section/2_page6/doc.en.md
    assert_output --stdin <<EOF
Title: page6

----

Text:

![image](image_en.png)
EOF
    assert_file_exists "kirby-content/3_section/2_page6/image_en.png"
}

@test "Creating page with i18n plugin drafts are correctly marked" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/3_section/_page7/doc.de.md"
    assert_file_exists "kirby-content/3_section/_page7/doc.en.md"
}


@test "Creating page with i18n plugin translated drafts are correctly marked" {
    testDir=${fixturesDir}/ok-mkdocs-i18n
    cd ${testDir}
    generate_mkdocs_site
    assert_dir_exists "kirby-content"
    assert_file_exists "kirby-content/3_section/_page8/doc.de.md"
    assert_file_exists "kirby-content/3_section/4_page8/doc.en.md"
}
