This repository contains tools to download, convert and upload scenarios from the annual Delta Green Shotgun Scenario Contest.

You need Python and the dependencies in the `requirements.txt` file.

Use the `download_scenarios.py` script to download all scenarios from the contest document:
```
python download_scenarios.py --contest-doc <contest-doc-url> --output-path <output-dir> --scenario-tsv-path <tsv-file>
```
All scenarios will be download in HTML format to the specified output directory.
Additionally, a TSV file is created, containing metadata for each scenario (ID, title, URL, author, teaser).
Sometimes the contest document is incorrectly parsed, due to inconsistent formatting.
This can lead to mistakes in the metadata. It is recommended to inspect the metadata file and fix such issues manually.

You can also download just a single scenario:
```
python download_scenarios.py --scenario <scenario-doc-url> --output-path <output-file>
```

Use the `convert_scenario.py` script to convert a single scenario from HTML to Wikidot markdown format.
Alternatively, use `convert_scenario_batch.py` to convert a whole batch of scenarios at once:
```
# single
python convert_scenario.py <html-file> <markdown-file>

# batch
python convert_scenario_batch.py <tsv-file> <html-dir> <markdown-dir> --year <year>
```
When you do batch conversion you have to provide the metadata TSV file that was created in the download step.
You also have to provide the year of the contest.

To upload the scenarios in markdown format to the Fairfield Project wiki, use the `upload_scenarios_to_wiki.py` script.
You will need to provide your credentials (username and password) for the wiki in the `config.json` file.
You will also need Firefox and the GeckoDriver. These are used by Selenium for the automated upload.
After configuration you can start the upload process like this:
```
python upload_scenarios_to_wiki.py --tsv-path <tsv-file> --markdown-dir <markdown-dir>
```
