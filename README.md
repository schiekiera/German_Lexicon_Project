## German Lexicon Project (jsPsych)

This repository contains the jsPsych implementation of the **German Lexicon Project** lexical decision task, plus server-side scripts for ID management and data storage.

In another repository, the [German Lexicon Multilab Monitoring Repository](https://github.com/schiekiera/German_Lexicon_Multilab_Monitoring), we track the number of datasets collected across all participating labs in the German Lexicon Project.


### Structure

- **Experiment HTML**  
  - `experiment.html` – full experiment  
  - `test_experiment.html` – full experiment with test settings (IDs, save paths, block sizes)  
  - `short_experiment.html` – shortened experiment  
  - `test_short_experiment.html` – short experiment with test settings  

- **Stimuli** (`stimuli/`)  
  - `stimulus_list.js` – full stimulus set (words & nonwords)  
  - `practice_trials.js` – practice items  

- **Consent & reimbursement** (`consent_forms/`)  
  - HTML consent forms for each site  
  - `combined_mapping.json` – maps `?uni=` parameters to consent forms and completion text  
  - `build_consent.py` – helper to (re)build consent HTML/text from templates  
  - `check_consent_form_sync.py` – checks that consent forms and mapping files are in sync across both GitHub repos and the HU web server  

- **ID management & saving**  
  - `ID_management/manageID.php`, `cleanupID.php` (+ `*_test.php`) – assign and release participant IDs  
  - `save_data.php`, `save_data_test.php` – store CSV data per university and create progress markers  

- **Client checks**  
  - `browserCheck.js` – blocks unsupported browsers/mobile and enforces desktop Chrome/Firefox  