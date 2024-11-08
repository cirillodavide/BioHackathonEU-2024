# genderTracker

`genderTracker` is a Python program originally developed in the [BioHackathon Germany 2023](https://github.com/bsc-life/biohackathon_germany_2023/tree/wg3/WG3/genderTracker) that predicts the gender of authors listed in a JSON file. This version has been adapted to the current challenge to make predictions solely based on the authors name by making use of the [Genderize](https://genderize.io/) package, the program takes in JSON data containing first and last author names, associates a reference paper ID with each entry (default PMCID), and outputs a CSV file with gender predictions (male/female) along with a probability score for each prediction.

## Features

- **JSON Input:** Accepts JSON files with first and last author names and a reference ID for each entry.
- **Gender Prediction:** Uses the Genderize API to predict gender based on author names.
- **CSV Output:** Outputs predictions to a CSV file containing the `Gender Prediction`, and `Probability Score` for each of the authors.
- **Verbose Mode:** Optional verbosity for detailed logging during execution.

## Usage

python -m genderTracker -j <your_data.json> -od <output_folder> -v True
