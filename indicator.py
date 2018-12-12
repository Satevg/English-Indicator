import gi
import requests
import configparser

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib
from gi.repository import Notify
from pathlib import Path
from random_word import RandomWords


config = configparser.ConfigParser()
config.read(Path(__file__).resolve().parent.joinpath('config.ini'))
APPINDICATOR_ID = config['DEFAULT']['APPINDICATOR_ID']
MINUTES_INTERVAL = int(config['DEFAULT']['MINUTES_INTERVAL'])
YANDEX_TRANSLATE_KEY = config['YANDEX']['API_KEY']
YANDEX_TRANSLATE_BASE_URL = config['YANDEX']['TRANSLATE_BASE_URL']


class EnglishIndicator:
    def __init__(self):
        self.random_service = RandomWords()

        self.ind = appindicator.Indicator.new(
            APPINDICATOR_ID,
            str(Path(__file__).resolve().parent.joinpath('./img/book.png')),
            appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        item = Gtk.MenuItem()
        item.set_label("Exit")
        item.connect("activate", self.quit)
        self.menu.append(item)
        self.menu.show_all()
        self.ind.set_menu(self.menu)

    def main(self):
        Notify.init(APPINDICATOR_ID)
        GLib.timeout_add_seconds(MINUTES_INTERVAL * 60, self.get_word)
        Gtk.main()

    def get_word(self):
        word = self.random_service.get_random_word()
        response = requests.get(f'{YANDEX_TRANSLATE_BASE_URL}?text={word}&lang=en-ru&key={YANDEX_TRANSLATE_KEY}').json()
        try:
            translation = response.get('text', [])[0]
        except IndexError:
            translation = 'Error :('

        if translation == word:
            translation = 'Hmm, wtf is this, m?..'

        Notify.Notification.new('<b>It\'s English time, Eugene:</b>', f'{word} - {translation}', None).show()
        return True

    def quit(self, widget):
        Notify.uninit()
        Gtk.main_quit()


if __name__ == '__main__':
    indicator = EnglishIndicator()
    indicator.main()
