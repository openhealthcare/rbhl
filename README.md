This is RBHL - an [Opal](https://github.com/openhealthcare/opal) project.

To get started, run the following commands:

```
    python manage.py migrate
    python manage.py runserver
    python manage.py with_history <file name>
    python manage.py import_admin_database <file name>
    python manage.py import_peak_flow # currently needs work
    python manage.py import_blood_book # currently needs work
```

To run the server run (runs runserver and sass)
```
    make -j
```
