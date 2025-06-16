
import pygetwindow


def is_webfishing_actively_being_played():
    return "WEBFISHING v" in str(pygetwindow.getActiveWindowTitle())