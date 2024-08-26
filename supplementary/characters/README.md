# This folder
Kaikki.org is a site which pre-processes Wiktionary site data and uploads it in JSONL format.
This is available for Chinese characters, as part of which the characters' etymologies are present,
and this data forms part of this project.

In order to update this data source (as it may change in the future), you can run the script in this
directory to download and re-process the Kaikki.org data.
It will produce a file, `kanji_etymologies.json`, which will map kanji to their etymologies according to the English Wiktionary.
A stable version of this file is also included in the repository so that you don't need to go through all that just to run the
rest of the program, but the option is nevertheless available.