# ProspecTonk

## 1. Raw data

The monkey data is located at `monkeys/source/data.xlsx` 
 
Note: Analysis takes into account only results 
after `2020-02-18`

## 2. Code

### Config

* Install Python3 (and pip). For instance, on MacOS using brew:
        
        brew install python3

* Install dependencies

        pip3 install -r requirements.txt

* Initiate Django (using SQLite)

        python3 manage.py makemigrations
        python3 manage.py migrate


* Import the data


    python3 import_xlsx
    

### Reproduce the figures (and ) 


    python3 main.py
    

### Data viewing
   
#### Config

* Create a superuser
        
        python3 manage.py createsuperuser

* Launch the server
    
       python3 manage.py runserver 
 
 #### Use

Go to http://127.0.0.1:8000/
