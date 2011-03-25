from django.db import models
from django.db.models import signals
from django.conf import settings
from django.dispatch import dispatcher

_USER_APP_NAME, _USER_MODEL_NAME = getattr(settings, 'USER_MODEL', 'auth.User').split('.') # We default to the django.contrib.auth.models.User model
_pending_user_lookups = []

__all__ = ['UserForeignKey',]

class UserForeignKey(models.ForeignKey):
    def __init__(self, **kwargs):
        self._stored_kwargs = kwargs
        self.initialized = False

        user_model = models.get_model(_USER_APP_NAME, _USER_MODEL_NAME, seed_cache=False)

        if user_model is None:
            _pending_user_lookups.append(self)
        else:
            self.__reinit__(user_model)

    def __reinit__(self, to):
        kwargs = self._stored_kwargs
        kwargs['to'] = to
        models.ForeignKey.__init__(self, **kwargs)
        self.initialized = True

    def contribute_to_class(self, cls, name):
        if self.initialized:
            models.ForeignKey.contribute_to_class(self, cls, name)
            if hasattr(self, '_cached_contribute_to_class_args'):
                del self._cached_contribute_to_class_args
        else:
            self._cached_contribute_to_class_args = (cls, name)

def do_user_lookup(sender, **kwargs):
    if _USER_APP_NAME == sender._meta.app_label and _USER_MODEL_NAME == sender._meta.object_name:
        for fk in _pending_user_lookups:
            fk.__reinit__(sender)
            fk.contribute_to_class(*fk._cached_contribute_to_class_args)

models.signals.class_prepared.connect(do_user_lookup)
