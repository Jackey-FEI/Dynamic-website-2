"""
Insta485 upload file handler.

URLs include:
/uploads/<filename>
"""

from pathlib import Path
import flask
import insta485


@insta485.app.route('/uploads/<filename>')
def route_uploads(filename):
    """Route files from /var/uploads/ to the uploads route."""
    if "user" not in flask.session:
        return flask.abort(403)

    file_path = Path(insta485.app.config['UPLOAD_FOLDER'])
    file_path = file_path / filename
    if not file_path.is_file():
        return flask.abort(404)

    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'],
        filename, as_attachment=True
        )
