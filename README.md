# Grocery Shopper
___

This program is designed to scrape the weekly offers
from the german grocery stores "Penny" and "Edeka".
You will need to configure the links inside the
`config.yaml` file to scrape the data and build a .csv
file. If you want, you can use the reader to start a 
matching process. So pandas will search for items
from the `..//data//standard_einkauf.csv` file and
return a frame with matching products.

## Installation

Python 3.8 or newer is required. The Code and path extraction are designed
for a Windows-system. You can change the path extraction-parts to linux data
system in the config file.

You will need the following packages: `beautifulsoup4==4.12.2`, `pandas==2.0.0`, `PyYAML==6.0`, `selenium==4.8.3`.

To install the required packages, you can navigate to the project folder and
do:

`$ pip install -r requirements.txt`

## Usage
```
usage: main.py [-h] [-a ACTION]
```
1. Configure your `config.yaml` file with needed paths and urls. You will need links to the specific Penny or Edeka 
   store.
   
2. Start the `main.py -a download` to download all data for the current week and save them to `..//data//` path. Where you
can open them with Excel or other tools.
   1. To compare the offer dataframes from each store with your items in the `standard_einkauf.csv` file, you can 
    simply run `main.py -a compare` to compare the items and return a list of matching items.


```
optional arguments:
-h, --help            show this help message and exit
-a ACTION, --action ACTION
        Generate or Download offerlist with compare or download
```