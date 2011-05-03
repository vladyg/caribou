from caribou.settings.setting_types import *
from caribou.i18n import _

AntlerSettings = SettingsTopGroup(
    _("Antler Preferences"), "/org/gnome/antler/", "org.gnome.antler",
    [SettingsGroup("antler", _("Antler"), [
                SettingsGroup("appearance", _("Appearance"), [
                        BooleanSetting("use_system", _("Use System Theme"),
                                       True, _("Use System Theme"))
                        ])
                ])
     ])
