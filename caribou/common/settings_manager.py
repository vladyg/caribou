import os
from gi.repository import GConf
from setting_types import *
from settings import settings
import const

class _SettingsManager(object):
    def __init__(self, settings):
        self.groups = settings
        self.gconf_client = GConf.Client.get_default()
        self.gconf_client.add_dir(const.CARIBOU_GCONF,
                                  GConf.ClientPreloadType.PRELOAD_NONE)
        self._settings_map = {}
        self._map_settings(self.groups)

        self._setup_settings()

    def __getattr__(self, name):
        try:
            return self._settings_map[name]
        except KeyError:
            raise AttributeError, "no setting named '%s'" % name

    def _map_settings(self, setting):
        if self._settings_map.has_key(setting.name):
            raise ValueError, \
                "more than one setting has the name '%s'" % setting.name
        self._settings_map[setting.name] = setting
        
        for s in setting:
            self._map_settings(s)

    def _setup_settings(self):
        for setting in self._settings_map.values():
            if isinstance(setting, SettingsGroup):
                continue
            try:
                setting.value = self.gconf_client.get(setting.gconf_key)
            except ValueError:
                val = GConf.Value.new(setting.gconf_type)
                setting.set_gconf_value(val)
                self.gconf_client.set(setting.gconf_key, val)

            self._change_dependant_sensitivity(setting)

            handler_id = setting.connect('value-changed',
                                         self._on_value_changed)

            #self.gconf_client.notify_add(setting.gconf_key,
            #                             self._gconf_setting_changed_cb,
            #                             (setting, handler_id))

    def _change_dependant_sensitivity(self, setting):
        for name in setting.insensitive_when_false:
            self._settings_map[name].sensitive = setting.is_true
        for name in setting.insensitive_when_true:
            self._settings_map[name].sensitive = not setting.is_true
        if setting.allowed:
            index = [a for a, b in setting.allowed].index(setting.value)
            for i, child in enumerate(setting.children):
                child.sensitive = i == index

    def _on_value_changed(self, setting, value):
        if value != self.gconf_client.get(setting.gconf_key):
            val = GConf.Value.new(setting.gconf_type)
            setting.set_gconf_value(val)
            self.gconf_client.set(setting.gconf_key, val)
            self._change_dependant_sensitivity(setting)

    def _gconf_setting_changed_cb(self, client, connection_id, entry, data):
        setting, handler_id = data
        new_value = client.get_value(setting.gconf_key)
        if setting.value != new_value:
            setting.handler_block(handler_id)
            setting.value = new_value
            setting.handler_unblock(handler_id)

    def __call__(self):
        return self

SettingsManager = _SettingsManager(settings)
