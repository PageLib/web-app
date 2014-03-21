# -*- coding: utf-8 -*-

import re
from wsc.iam import Session


class UserAndSession:
    """
    Classe "user" pour flask-login. Représente une session ouverte dans IAM.
    """

    user_id = None
    session_id = None

    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id

    @staticmethod
    def from_id(user_and_session_id):
        matches = re.match('([a-z0-9]+):([a-z0-9]+)', user_and_session_id)
        if matches:
            return UserAndSession(matches.groups()[0], matches.groups()[1])
        else:
            return None

    def is_authenticated(self):
        # (appel aux webservices pour vérifier que la session est active)
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return '{}:{}'.format(self.user_id, self.session_id)

    def get_wsc_session(self):
        return Session(self.user_id, self.session_id)
