This is RBHL - an [Opal](https://github.com/openhealthcare/opal) project.

To get started, run the following commands:

```
    python manage.py migrate
    python manage.py runserver
    python manage.py with_history <file name>
    python manage.py import_admin_database <file name>

    # constructs lookup lists from values from the above
    python manage.py construct_lookup_lists
    python manage.py import_peak_flow # currently needs work
    python manage.py import_blood_book # currently needs work

    # import extra data files
    python manage.py other_details <file name>
    python manage.py bronchial_test <file name>
    python manage.py routine_spts <file name>
```


#### Development
```
    pip install pre-commit
    pre-commit install
```


To recompile sass files to css in development:
```
sass --watch rbhl/static/css/rbhl.scss:rbhl/static/css/rbhl.css
```
