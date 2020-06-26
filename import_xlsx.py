import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "ProspecTonk.settings")
django.setup()

from data_interface.import_export import import_data_xlsx


if __name__ == "__main__":

    import_data_xlsx(data_file='data.xlsx', starting_date="2020-02-18")
