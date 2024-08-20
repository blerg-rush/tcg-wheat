# TCG-Wheat

A handy CLI tool for sifting the chaff from your MTG collection.

## Requirements
* Python 3.12
* A collection tracked with [ManaBox](https://manabox.app/)

## Usage
* Export your ManaBox Unsorted folder (or another preferred folder) to a CSV file and place it in the `input` directory
* Rename `.env.example` to `.env` and change the input and output filenames if necessary
* Install TCG-Wheat
```shell
pipx install virtualenv
virtualenv venv --python=python3.12
source venv/bin/activate
pip install .
```
* Load your collection to the TCG-Wheat's database
```shell
python -m tcg_wheat.cli load-collection
```
* Populate with additional data from Moxfield
```shell
# This may take a while. Don't let your computer fall asleep!
python -m tcg_wheat.cli populate-moxfield
```
* Run `find-chaff` to output a CSV report of cards you may be able to cut from your collection
```shell
# Run `python -m tcg_wheat.cli find-chaff --help` instead to see additional options
python -m tcg_wheat.cli find-chaff -o
```
