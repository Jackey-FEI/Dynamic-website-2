"""Views, one for each Insta485 page."""
from insta485.views.index import show_index, show_explore
from insta485.views.accounts import account_operations, \
    show_login, show_create, show_edit, show_delete, show_password, \
    handle_logout
from insta485.views.uploads import route_uploads
from insta485.views.post_reqs import handle_comments, handle_following, \
    handle_likes, handle_posts
from insta485.views.users import relationship, show_followers, show_following
