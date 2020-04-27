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
    python manage.py skin_prick_tests
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

#### RBHL specific details
Unique to RBHL (rather than, say Opal)

We have a `field_display` template tag that accepts `model.field` as a string. This renders a display template for the field.

It takes an argument `label` for what to display as the fields display name. If this is excluded it will take it off the model field.

It takes the arguments `label_size` and `field_size` for the bootstrap `col` number. If these are absent it will look at the template context. This mean that an entire form can be structured the same way for example easily to the same sizes.

e.g.

```
{% load rbhl_panels %}


{% with label_size=4 field_size=8 %}
  {% field_display "Demographics.height" %}
  {% field_display "Demographics.post_code" %
{% endwith %}
```

Will display the below field verbose name and value in `col-md-4` for the label and `col-md-8` respectively.
