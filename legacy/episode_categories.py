from opal.core import episodes


class AdminDatabase(episodes.EpisodeCategory):
    display_name = "Admin Database"
    detail_template = "detail/admin_database.html"


class BloodBook(episodes.EpisodeCategory):
    display_name = "Blood Book"
    detail_template = "detail/blood_book.html"
