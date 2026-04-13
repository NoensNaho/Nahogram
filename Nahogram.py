# ==================================================
# 1. KIVY AYARLARI VE OPTİMİZASYON
# ==================================================
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'multisamples', '0')

# ==================================================
# 2. KÜTÜPHANELER
# ==================================================
import json
import os
import shutil
from pathlib import Path
import platform
import threading
import time
import requests

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarListItem, IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem, \
    ImageLeftWidget
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.fitimage import FitImage
from kivy.utils import platform as os_platform
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# --- MERKEZ BANKASI (SUNUCU) LİNKİ ---
FIREBASE_URL = "https://nahogram-5f474-default-rtdb.europe-west1.firebasedatabase.app"
VERI_DOSYASI = "nahogram_veritabani.json"


# Python Sınıfları (KV Dilinden önce tanımlanmalı)
class LoginScreen(MDScreen): pass


class SignupScreen(MDScreen): pass


class MainScreen(MDScreen): pass


class ChatScreen(MDScreen): pass


class YorumDialogContent(MDBoxLayout):
    post_id = StringProperty()


class PostCard(MDCard):
    post_id = StringProperty()
    username = StringProperty()
    content = StringProperty()
    profil_foto = StringProperty("")
    post_foto = StringProperty("")
    kendi_postum = BooleanProperty(False)
    begeni_ikonu = StringProperty("heart-outline")
    begeni_sayisi = StringProperty("0")
    yorum_sayisi = StringProperty("0")


# ==================================================
# 3. ARAYÜZ (KV DİLİ)
# ==================================================
KV_KODU = '''
ScreenManager:
    LoginScreen:
    SignupScreen:
    MainScreen:
    ChatScreen:

<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        spacing: "20dp"
        padding: "30dp"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: None
        width: "350dp"

        # LOGO BURADAN SİLİNDİ, SADECE YAZI KALDI!
        MDLabel:
            text: "Nahogram"
            font_style: "H2"
            bold: True
            halign: "center"
            theme_text_color: "Primary"

        MDLabel:
            id: hata_mesaji
            text: "Bağlantı Kontrol Ediliyor..."
            theme_text_color: "Custom"
            text_color: 1, 0.8, 0, 1
            halign: "center"
            font_style: "Subtitle2"
            bold: True
            adaptive_height: True

        MDTextField:
            id: user_isim
            hint_text: "Kullanıcı Adı"
            icon_left: "account"

        MDRelativeLayout:
            size_hint_y: None
            height: user_sifre.height
            MDTextField:
                id: user_sifre
                hint_text: "Şifre"
                password: True
                icon_left: "key-variant"
            MDIconButton:
                icon: "eye-off"
                pos_hint: {"center_y": .5, "right": 1}
                theme_text_color: "Hint"
                on_release:
                    self.icon = "eye" if self.icon == "eye-off" else "eye-off"
                    user_sifre.password = False if self.icon == "eye" else True

        MDRaisedButton:
            text: "Giriş Yap"
            pos_hint: {"center_x": .5}
            size_hint_x: 1
            on_release: app.giris_yap(user_isim.text, user_sifre.text)

        MDTextButton:
            text: "Hesabın yok mu? Kayıt Ol"
            pos_hint: {"center_x": .5}
            on_release:
                root.manager.transition.direction = "left"
                root.manager.current = "signup"

<SignupScreen>:
    name: "signup"
    MDBoxLayout:
        orientation: "vertical"
        spacing: "20dp"
        padding: "30dp"
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True
        size_hint_x: None
        width: "350dp"
        MDLabel:
            text: "Aramıza Katıl"
            font_style: "H4"
            bold: True
            halign: "center"
            theme_text_color: "Primary"
        MDLabel:
            id: hata_mesaji
            text: ""
            theme_text_color: "Custom"
            text_color: 1, 0, 0, 1
            halign: "center"
            font_style: "Subtitle2"
            bold: True
            adaptive_height: True
        MDTextField:
            id: reg_isim
            hint_text: "Kullanıcı Adı"
            icon_left: "account"
        MDRelativeLayout:
            size_hint_y: None
            height: reg_sifre.height
            MDTextField:
                id: reg_sifre
                hint_text: "Şifre"
                password: True
                icon_left: "key-variant"
            MDIconButton:
                icon: "eye-off"
                pos_hint: {"center_y": .5, "right": 1}
                theme_text_color: "Hint"
                on_release:
                    self.icon = "eye" if self.icon == "eye-off" else "eye-off"
                    reg_sifre.password = False if self.icon == "eye" else True
        MDRaisedButton:
            text: "Kayıt Ol"
            pos_hint: {"center_x": .5}
            size_hint_x: 1
            on_release: app.kayit_ol(reg_isim.text, reg_sifre.text)
        MDTextButton:
            text: "Zaten hesabın var mı? Giriş Yap"
            pos_hint: {"center_x": .5}
            on_release:
                root.manager.transition.direction = "right"
                root.manager.current = "login"

<PostCard>:
    orientation: "vertical"
    padding: "15dp"
    spacing: "10dp"
    size_hint_y: None
    height: self.minimum_height  # İçeriğe göre otomatik büyür
    elevation: 2
    radius: [15, 15, 15, 15]

    # 1. SATIR: PROFİL, İSİM VE ÇÖP KUTUSU
    MDBoxLayout:
        adaptive_height: True
        spacing: "10dp"
        MDRelativeLayout:
            size_hint: None, None
            size: "40dp", "40dp"
            MDIcon:
                icon: "account-circle"
                font_size: "40sp"
                theme_text_color: "Primary"
                opacity: 1 if not root.profil_foto else 0
            FitImage:
                source: root.profil_foto
                size_hint: None, None
                size: "40dp", "40dp"
                radius: [20, 20, 20, 20]
                opacity: 1 if root.profil_foto else 0
        MDLabel:
            text: root.username
            bold: True
            theme_text_color: "Primary"
            adaptive_height: True
            pos_hint: {"center_y": .5}

        Widget: # Sağa yaslamak için boşluk

        # SİLME BUTONU (Sadece kendi postunsa görünür)
        MDIconButton:
            icon: "trash-can-outline"
            theme_text_color: "Error"
            opacity: 1 if root.kendi_postum else 0
            disabled: not root.kendi_postum
            pos_hint: {"center_y": .5}
            on_release: app.gonderi_sil(root.post_id)

    # 2. SATIR: YAZI İÇERİĞİ
    MDLabel:
        text: root.content
        theme_text_color: "Secondary"
        adaptive_height: True

    # 3. SATIR: FOTOĞRAF (SÜNME/KASMA SORUNU ÇÖZÜLDÜ)
    Image:
        source: root.post_foto
        size_hint_y: None
        height: "250dp" if root.post_foto else "0dp"
        allow_stretch: True
        keep_ratio: True
        opacity: 1 if root.post_foto else 0

    # 4. SATIR: BEĞENİ VE YORUM BUTONLARI
    MDBoxLayout:
        adaptive_height: True
        spacing: "5dp"

        MDIconButton:
            icon: root.begeni_ikonu
            theme_text_color: "Custom"
            text_color: (1, 0, 0, 1) if root.begeni_ikonu == "heart" else app.theme_cls.text_color
            on_release: app.begeni_toggle(root.post_id)
        MDLabel:
            text: root.begeni_sayisi
            adaptive_height: True
            pos_hint: {"center_y": .5}

        MDIconButton:
            icon: "comment-outline"
            on_release: app.yorumlari_ac(root.post_id)
        MDLabel:
            text: root.yorum_sayisi
            adaptive_height: True
            pos_hint: {"center_y": .5}

<YorumDialogContent>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "350dp"

    MDScrollView:
        MDList:
            id: yorum_listesi

    MDBoxLayout:
        adaptive_height: True
        spacing: "10dp"
        MDTextField:
            id: yeni_yorum
            hint_text: "Bir yorum yaz..."
            mode: "round"
        MDIconButton:
            icon: "send"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
            pos_hint: {"center_y": .5}
            on_release: 
                app.yorum_gonder(root.post_id, yeni_yorum.text)
                yeni_yorum.text = ""

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            id: ana_baslik
            title: "Nahogram (Bağlanıyor...)"
            left_action_items: [["cloud-sync", lambda x: app.verileri_indir()]]
            right_action_items: [["logout", lambda x: app.cikis_yap()]]
            elevation: 3

        MDBottomNavigation:
            panel_color: app.theme_cls.bg_dark

            # 1. AKIŞ EKRANI (LOGO BURAYA GELDİ)
            MDBottomNavigationItem:
                name: 'screen_home'
                text: 'Akış'
                icon: 'home'
                on_tab_press: app.akis_yenile()
                MDBoxLayout:
                    orientation: "vertical"

                    # LOGO SADECE ANA SAYFADA
                    MDBoxLayout:
                        adaptive_height: True
                        padding: "10dp"
                        Image:
                            source: "ngram.jpeg" if app.logo_var_mi else ""
                            size_hint_y: None
                            height: "50dp" if app.logo_var_mi else "0dp"
                            opacity: 1 if app.logo_var_mi else 0

                    MDScrollView:
                        MDBoxLayout:
                            id: feed_box
                            orientation: "vertical"
                            spacing: "15dp"
                            padding: "15dp"
                            adaptive_height: True

            MDBottomNavigationItem:
                name: 'screen_search'
                text: 'Ara'
                icon: 'magnify'
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "20dp"
                    spacing: "15dp"
                    MDTextField:
                        id: arama_kutusu
                        hint_text: "Kullanıcı Ara"
                        mode: "round"
                        icon_left: "magnify"
                        on_text_validate: app.kullanici_ara(self.text)
                    MDRaisedButton:
                        text: "Ara"
                        pos_hint: {"center_x": .5}
                        on_release: app.kullanici_ara(arama_kutusu.text)
                    MDLabel:
                        id: arama_bilgi
                        text: "Kişileri bul ve takip et."
                        halign: "center"
                        theme_text_color: "Secondary"
                        font_style: "Caption"
                        adaptive_height: True
                    MDScrollView:
                        MDList:
                            id: arama_sonuclari_listesi

            MDBottomNavigationItem:
                name: 'screen_messages'
                text: 'Mesajlar'
                icon: 'chat-processing'
                on_tab_press: app.mesaj_listesini_olustur()
                MDScrollView:
                    MDList:
                        id: mesajlar_listesi

            MDBottomNavigationItem:
                name: 'screen_add'
                text: 'Paylaş'
                icon: 'plus-box-outline'
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "20dp"
                    spacing: "20dp"
                    MDTextField:
                        id: paylasim_kutusu
                        hint_text: "Bugün ne düşünüyorsun?"
                        mode: "fill"
                        multiline: True
                        max_height: "100dp"

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "10dp"
                        MDRaisedButton:
                            text: "Fotoğraf Ekle"
                            icon: "image"
                            size_hint_x: 0.5
                            on_release: app.dosya_seciciyi_ac('post')
                        MDRaisedButton:
                            text: "Paylaş"
                            md_bg_color: app.theme_cls.primary_dark
                            size_hint_x: 0.5
                            on_release: app.gonderi_paylas(paylasim_kutusu.text)

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "5dp"
                        pos_hint: {"center_x": .5}
                        MDLabel:
                            id: secilen_foto_bilgi
                            text: "Fotoğraf Seçilmedi"
                            halign: "right"
                            font_style: "Caption"
                            theme_text_color: "Secondary"
                            adaptive_height: True
                        MDIconButton:
                            id: iptal_butonu
                            icon: "close-circle"
                            theme_text_color: "Error"
                            opacity: 0
                            disabled: True
                            size_hint: None, None
                            size: "24dp", "24dp"
                            pos_hint: {"center_y": .5}
                            on_release: app.fotografi_iptal_et()
                    Widget:

            MDBottomNavigationItem:
                name: 'screen_profile'
                text: 'Profil'
                icon: 'card-account-details-outline'
                on_tab_press: app.profil_bilgilerini_yukle()

                MDScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "20dp"
                        spacing: "20dp"
                        adaptive_height: True

                        MDCard:
                            orientation: "vertical"
                            adaptive_height: True
                            padding: "20dp"
                            spacing: "15dp"
                            radius: [20, 20, 20, 20]
                            elevation: 3

                            MDBoxLayout:
                                adaptive_height: True
                                pos_hint: {"center_x": .5}
                                MDRelativeLayout:
                                    size_hint: None, None
                                    size: "90dp", "90dp"
                                    pos_hint: {"center_x": .5}

                                    MDIcon:
                                        icon: "account-circle"
                                        font_size: "90sp"
                                        pos_hint: {"center_x": .5, "center_y": .5}
                                        opacity: 1 if not app.aktif_profil_foto else 0

                                    FitImage:
                                        source: app.aktif_profil_foto
                                        size_hint: None, None
                                        size: "90dp", "90dp"
                                        radius: [45, 45, 45, 45]
                                        pos_hint: {"center_x": .5, "center_y": .5}
                                        opacity: 1 if app.aktif_profil_foto else 0

                                    MDIconButton:
                                        icon: "camera-plus"
                                        md_bg_color: app.theme_cls.primary_color
                                        theme_text_color: "Custom"
                                        text_color: 1, 1, 1, 1
                                        size_hint: None, None
                                        size: "28dp", "28dp"
                                        pos_hint: {"right": 1, "bottom": 0}
                                        on_release: app.dosya_seciciyi_ac('profil')

                            MDLabel:
                                id: profil_isim
                                text: "@Kullanici"
                                font_style: "H5"
                                bold: True
                                halign: "center"
                                adaptive_height: True

                            MDSeparator:

                            MDBoxLayout:
                                adaptive_height: True
                                padding: "10dp"
                                MDBoxLayout:
                                    orientation: "vertical"
                                    adaptive_height: True
                                    MDLabel:
                                        id: txt_gonderi_sayi
                                        text: "0"
                                        halign: "center"
                                        font_style: "H6"
                                        bold: True
                                    MDLabel:
                                        text: "Gönderi"
                                        halign: "center"
                                        font_style: "Caption"
                                        theme_text_color: "Secondary"
                                MDBoxLayout:
                                    orientation: "vertical"
                                    adaptive_height: True
                                    MDLabel:
                                        id: txt_takipci_sayi
                                        text: "0"
                                        halign: "center"
                                        font_style: "H6"
                                        bold: True
                                    MDLabel:
                                        text: "Takipçi"
                                        halign: "center"
                                        font_style: "Caption"
                                        theme_text_color: "Secondary"
                                MDBoxLayout:
                                    orientation: "vertical"
                                    adaptive_height: True
                                    MDLabel:
                                        id: txt_takip_sayi
                                        text: "0"
                                        halign: "center"
                                        font_style: "H6"
                                        bold: True
                                    MDLabel:
                                        text: "Takip"
                                        halign: "center"
                                        font_style: "Caption"
                                        theme_text_color: "Secondary"

                            MDSeparator:
                            MDTextField:
                                id: bio_girdisi
                                hint_text: "Biyografi (Kendinden Bahset)"
                                mode: "rectangle"
                                multiline: True
                            MDTextField:
                                id: hedef_girdisi
                                hint_text: "Şu Anki Hedefin / Durumun"
                                mode: "rectangle"
                                icon_left: "bullseye-arrow"
                            MDTextButton:
                                text: "Bilgileri Kaydet"
                                pos_hint: {"center_x": .5}
                                theme_text_color: "Custom"
                                text_color: app.theme_cls.primary_color
                                on_release: app.profil_bilgilerini_kaydet(bio_girdisi.text, hedef_girdisi.text)

<ChatScreen>:
    name: "chat"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id: chat_baslik
            title: "Sohbet"
            left_action_items: [["arrow-left", lambda x: app.sohbetten_cik()]]
            elevation: 3
        MDScrollView:
            MDBoxLayout:
                id: chat_box
                orientation: "vertical"
                adaptive_height: True
                padding: "15dp"
                spacing: "10dp"
        MDBoxLayout:
            size_hint_y: None
            height: "70dp"
            padding: "10dp"
            spacing: "10dp"
            md_bg_color: app.theme_cls.bg_dark
            MDTextField:
                id: mesaj_girdisi
                hint_text: "Mesajını yaz..."
                mode: "round"
            MDIconButton:
                icon: "send"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                on_release: app.mesaj_gonder(mesaj_girdisi.text)
'''


# ==================================================
# 4. PYTHON MANTIĞI VE RADAR SİSTEMİ
# ==================================================

class NahogramApp(MDApp):
    aktif_profil_foto = StringProperty("")
    secilen_post_resmi = StringProperty("")
    internet_durumu = False
    logo_var_mi = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.veritabani = {"kullanicilar": {}, "gonderiler": [], "sohbetler": {}}
        self.aktif_kullanici = ""
        self.aktif_sohbet_hedefi = ""
        self.dosya_secici_modu = "profil"
        self.yorum_dialog = None
        self.logo_var_mi = os.path.exists("ngram.jpeg")

        self.file_manager = MDFileManager(
            exit_manager=self.dosya_seciciyi_kapat,
            select_path=self.dosya_secildi,
            ext=['.png', '.jpg', '.jpeg']
        )

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        if self.logo_var_mi:
            self.icon = "ngram.jpeg"
        return Builder.load_string(KV_KODU)

    def on_start(self):
        self.yerel_yukle()
        threading.Thread(target=self.radar_dongusu, daemon=True).start()

    def radar_dongusu(self):
        while True:
            try:
                requests.get("https://www.google.com", timeout=2)
                self.internet_durumu = True
            except:
                self.internet_durumu = False

            Clock.schedule_once(self.arayuzu_guncelle, 0)
            time.sleep(2)

    def arayuzu_guncelle(self, dt):
        login_ekrani = self.root.get_screen("login")
        main_ekrani = self.root.get_screen("main")

        if self.internet_durumu:
            login_ekrani.ids.hata_mesaji.text = "Online 🌍"
            login_ekrani.ids.hata_mesaji.text_color = (0, 0.8, 0, 1)
            main_ekrani.ids.ana_baslik.title = "Nahogram (Online)"
        else:
            login_ekrani.ids.hata_mesaji.text = "Offline 📡"
            login_ekrani.ids.hata_mesaji.text_color = (1, 0, 0, 1)
            main_ekrani.ids.ana_baslik.title = "Nahogram (Çevrimdışı)"

    def verileri_indir(self):
        if self.internet_durumu:
            def islem():
                try:
                    cevap = requests.get(f"{FIREBASE_URL}/nahogram.json", timeout=5)
                    if cevap.status_code == 200 and cevap.json():
                        self.veritabani = cevap.json()
                        self.eski_verileri_guncelle()  # Eski verilere ID basar
                        self.yerel_kaydet()
                        Clock.schedule_once(lambda dt: self.akis_yenile(), 0)
                except Exception as e:
                    pass

            threading.Thread(target=islem).start()

    def veri_kaydet(self):
        self.yerel_kaydet()
        if self.internet_durumu:
            def islem():
                try:
                    requests.put(f"{FIREBASE_URL}/nahogram.json", json=self.veritabani, timeout=5)
                except:
                    pass

            threading.Thread(target=islem).start()

    def yerel_yukle(self):
        if os.path.exists(VERI_DOSYASI):
            with open(VERI_DOSYASI, "r", encoding="utf-8") as d:
                veri = json.load(d)
                if "sohbetler" not in veri: veri["sohbetler"] = {}
                self.veritabani = veri
                self.eski_verileri_guncelle()

    def yerel_kaydet(self):
        with open(VERI_DOSYASI, "w", encoding="utf-8") as d:
            json.dump(self.veritabani, d, indent=4)

    def dosya_seciciyi_ac(self, mod):
        self.dosya_secici_modu = mod
        if os_platform == 'android':
            baslangic_yolu = '/storage/emulated/0/'
        else:
            baslangic_yolu = str(Path.home())
        self.file_manager.show(baslangic_yolu)

    def dosya_secildi(self, secilen_yol):
        self.dosya_seciciyi_kapat()
        if not os.path.exists("nahogram_medya"):
            os.makedirs("nahogram_medya")

        zaman_damgasi = str(int(time.time()))

        if self.dosya_secici_modu == 'profil':
            yeni_isim = f"nahogram_medya/{self.aktif_kullanici}_profil.png"
            try:
                shutil.copy(secilen_yol, yeni_isim)
                self.veritabani["kullanicilar"][self.aktif_kullanici]["profil_foto"] = yeni_isim
                self.veri_kaydet()
                self.aktif_profil_foto = yeni_isim
                self.akis_yenile()
            except:
                pass

        elif self.dosya_secici_modu == 'post':
            yeni_isim = f"nahogram_medya/post_{zaman_damgasi}.png"
            try:
                shutil.copy(secilen_yol, yeni_isim)
                self.secilen_post_resmi = yeni_isim
                ekran = self.root.get_screen("main").ids
                ekran.secilen_foto_bilgi.text = "Fotoğraf Hazır!"
                ekran.secilen_foto_bilgi.theme_text_color = "Custom"
                ekran.secilen_foto_bilgi.text_color = (0, 0.8, 0, 1)
                ekran.iptal_butonu.opacity = 1
                ekran.iptal_butonu.disabled = False
            except:
                pass

    def dosya_seciciyi_kapat(self, *args):
        self.file_manager.close()

    def fotografi_iptal_et(self):
        self.secilen_post_resmi = ""
        ekran = self.root.get_screen("main").ids
        ekran.secilen_foto_bilgi.text = "Fotoğraf Seçilmedi"
        ekran.secilen_foto_bilgi.theme_text_color = "Secondary"
        ekran.secilen_foto_bilgi.text_color = (0.5, 0.5, 0.5, 1)
        ekran.iptal_butonu.opacity = 0
        ekran.iptal_butonu.disabled = True

    def profil_bilgilerini_yukle(self):
        kullanici = self.veritabani["kullanicilar"][self.aktif_kullanici]
        main_ids = self.root.get_screen("main").ids
        main_ids.profil_isim.text = f"@{self.aktif_kullanici}"
        main_ids.txt_gonderi_sayi.text = str(kullanici.get('gonderi', 0))
        main_ids.txt_takipci_sayi.text = str(kullanici.get('takipci', 0))
        main_ids.txt_takip_sayi.text = str(kullanici.get('takip', 0))
        main_ids.bio_girdisi.text = kullanici.get('biyografi', "")
        main_ids.hedef_girdisi.text = kullanici.get('hedef', "")

    def profil_bilgilerini_kaydet(self, bio, hedef):
        self.veritabani["kullanicilar"][self.aktif_kullanici]["biyografi"] = bio
        self.veritabani["kullanicilar"][self.aktif_kullanici]["hedef"] = hedef
        self.veri_kaydet()

    def giris_yap(self, kullanici_adi, sifre):
        ekran = self.root.get_screen("login")
        kullanicilar = self.veritabani.get("kullanicilar", {})
        if kullanici_adi in kullanicilar and kullanicilar[kullanici_adi]["sifre"] == sifre:
            self.aktif_kullanici = kullanici_adi
            self.eski_verileri_guncelle()
            self.aktif_profil_foto = kullanicilar[kullanici_adi].get("profil_foto", "")
            self.verileri_indir()
            self.root.current = "main"
        else:
            ekran.ids.hata_mesaji.text = "Hatalı Giriş veya Kullanıcı Yok!"
            ekran.ids.hata_mesaji.text_color = (1, 0, 0, 1)

    def kayit_ol(self, kullanici_adi, sifre):
        ekran = self.root.get_screen("signup")
        if kullanici_adi and sifre:
            if "kullanicilar" not in self.veritabani: self.veritabani["kullanicilar"] = {}
            if kullanici_adi not in self.veritabani["kullanicilar"]:
                self.veritabani["kullanicilar"][kullanici_adi] = {
                    "sifre": sifre, "gonderi": 0, "takipci": 0, "takip": 0,
                    "takip_edilenler": [], "profil_foto": "", "biyografi": "", "hedef": ""
                }
                self.veri_kaydet()
                self.giris_yap(kullanici_adi, sifre)

    def cikis_yap(self):
        self.aktif_kullanici = ""
        self.aktif_profil_foto = ""
        self.root.current = "login"

    def eski_verileri_guncelle(self):
        k = self.veritabani["kullanicilar"].get(self.aktif_kullanici, {})
        if "takip_edilenler" not in k: k["takip_edilenler"] = []
        if "profil_foto" not in k: k["profil_foto"] = ""
        if "biyografi" not in k: k["biyografi"] = ""
        if "hedef" not in k: k["hedef"] = ""
        if "gonderi" not in k: k["gonderi"] = 0
        if "takipci" not in k: k["takipci"] = 0
        if "takip" not in k: k["takip"] = 0

        # Eski gönderileri yeni sisteme uydurma (Çok Önemli)
        if "gonderiler" not in self.veritabani: self.veritabani["gonderiler"] = []
        for i, gonderi in enumerate(self.veritabani["gonderiler"]):
            if "id" not in gonderi: gonderi["id"] = f"eski_gonderi_{i}_{int(time.time())}"
            if "begenenler" not in gonderi: gonderi["begenenler"] = []
            if "yorumlar" not in gonderi: gonderi["yorumlar"] = []
        self.veri_kaydet()

    def gonderi_paylas(self, icerik):
        if icerik.strip() or self.secilen_post_resmi:
            if "gonderiler" not in self.veritabani: self.veritabani["gonderiler"] = []

            yeni_gonderi = {
                "id": str(int(time.time() * 1000)),  # Her gönderiye özel kimlik kartı
                "kullanici": self.aktif_kullanici,
                "icerik": icerik.strip(),
                "foto_yolu": self.secilen_post_resmi,
                "begenenler": [],
                "yorumlar": []
            }

            self.veritabani["gonderiler"].append(yeni_gonderi)
            self.veritabani["kullanicilar"][self.aktif_kullanici]["gonderi"] += 1
            self.veri_kaydet()
            self.akis_yenile()

            self.fotografi_iptal_et()
            self.root.get_screen("main").ids.paylasim_kutusu.text = ""

    def gonderi_sil(self, post_id):
        # Gönderiyi bul ve veritabanından uçur
        self.veritabani["gonderiler"] = [g for g in self.veritabani["gonderiler"] if g.get("id") != post_id]
        self.veritabani["kullanicilar"][self.aktif_kullanici]["gonderi"] -= 1
        self.veri_kaydet()
        self.akis_yenile()

    def begeni_toggle(self, post_id):
        for gonderi in self.veritabani["gonderiler"]:
            if gonderi.get("id") == post_id:
                if self.aktif_kullanici in gonderi["begenenler"]:
                    gonderi["begenenler"].remove(self.aktif_kullanici)
                else:
                    gonderi["begenenler"].append(self.aktif_kullanici)
                self.veri_kaydet()
                self.akis_yenile()
                break

    def yorumlari_ac(self, post_id):
        icerik = YorumDialogContent(post_id=post_id)

        # Eski yorumları listele
        for gonderi in self.veritabani["gonderiler"]:
            if gonderi.get("id") == post_id:
                for yorum in gonderi.get("yorumlar", []):
                    item = TwoLineAvatarListItem(
                        text=f"@{yorum['kullanici']}",
                        secondary_text=yorum['metin']
                    )
                    item.add_widget(IconLeftWidget(icon="comment-text-outline"))
                    icerik.ids.yorum_listesi.add_widget(item)
                break

        self.yorum_dialog = MDDialog(
            title="Yorumlar",
            type="custom",
            content_cls=icerik,
            buttons=[MDFlatButton(text="KAPAT", theme_text_color="Custom", text_color=self.theme_cls.primary_color,
                                  on_release=lambda x: self.yorum_dialog.dismiss())]
        )
        self.yorum_dialog.open()

    def yorum_gonder(self, post_id, metin):
        if not metin.strip(): return

        for gonderi in self.veritabani["gonderiler"]:
            if gonderi.get("id") == post_id:
                yeni_yorum = {"kullanici": self.aktif_kullanici, "metin": metin.strip()}
                gonderi["yorumlar"].append(yeni_yorum)

                # Anında listeye ekle
                item = TwoLineAvatarListItem(text=f"@{self.aktif_kullanici}", secondary_text=metin.strip())
                item.add_widget(IconLeftWidget(icon="comment-text-outline"))
                self.yorum_dialog.content_cls.ids.yorum_listesi.add_widget(item)

                self.veri_kaydet()
                self.akis_yenile()
                break

    def akis_yenile(self):
        feed_box = self.root.get_screen("main").ids.feed_box
        feed_box.clear_widgets()
        for gonderi in reversed(self.veritabani.get("gonderiler", [])):
            kullanici_bilgisi = self.veritabani["kullanicilar"].get(gonderi['kullanici'], {})

            begenenler = gonderi.get("begenenler", [])
            yorumlar = gonderi.get("yorumlar", [])

            kalp_ikonu = "heart" if self.aktif_kullanici in begenenler else "heart-outline"
            kendi_postum = (gonderi['kullanici'] == self.aktif_kullanici)

            feed_box.add_widget(PostCard(
                post_id=gonderi.get("id", ""),
                username=f"@{gonderi['kullanici']}",
                content=gonderi['icerik'],
                profil_foto=kullanici_bilgisi.get("profil_foto", ""),
                post_foto=gonderi.get("foto_yolu", ""),
                kendi_postum=kendi_postum,
                begeni_ikonu=kalp_ikonu,
                begeni_sayisi=str(len(begenenler)),
                yorum_sayisi=str(len(yorumlar))
            ))

    def kullanici_ara(self, sorgu):
        sorgu = sorgu.strip()
        liste = self.root.get_screen("main").ids.arama_sonuclari_listesi
        liste.clear_widgets()
        if not sorgu: return

        kullanicilar = self.veritabani["kullanicilar"]
        for k_adi in kullanicilar:
            if sorgu.lower() in k_adi.lower() and k_adi != self.aktif_kullanici:
                takipte_mi = k_adi in kullanicilar[self.aktif_kullanici].get("takip_edilenler", [])
                ikon = "check-circle" if takipte_mi else "account-plus"
                renk = "Custom" if takipte_mi else "Primary"

                hedef_metni = kullanicilar[k_adi].get('hedef', 'Hedef belirtilmemiş')

                liste_elemani = TwoLineAvatarIconListItem(
                    text=f"@{k_adi}",
                    secondary_text=f"🎯 {hedef_metni}"
                )

                btn = IconRightWidget(icon=ikon, theme_text_color=renk, text_color=self.theme_cls.primary_color)
                btn.bind(on_release=lambda instance, hedef=k_adi, b=btn: self.takip_et(hedef, b))
                liste_elemani.add_widget(btn)
                liste.add_widget(liste_elemani)

    def takip_et(self, hedef_kisi, buton_objesi):
        kullanicilar = self.veritabani["kullanicilar"]
        benim_listem = kullanicilar[self.aktif_kullanici]["takip_edilenler"]
        if hedef_kisi in benim_listem: return

        benim_listem.append(hedef_kisi)
        kullanicilar[self.aktif_kullanici]["takip"] += 1
        kullanicilar[hedef_kisi]["takipci"] += 1
        self.veri_kaydet()
        buton_objesi.icon = "check-circle"
        buton_objesi.theme_text_color = "Custom"
        buton_objesi.text_color = self.theme_cls.primary_color

    def mesaj_listesini_olustur(self):
        liste = self.root.get_screen("main").ids.mesajlar_listesi
        liste.clear_widgets()
        takip_edilenler = self.veritabani["kullanicilar"][self.aktif_kullanici].get("takip_edilenler", [])
        for k_adi in takip_edilenler:
            item = TwoLineAvatarListItem(text=f"@{k_adi}", secondary_text="Sohbet başlat...")
            item.bind(on_release=lambda x, hedef=k_adi: self.sohbet_ac(hedef))
            liste.add_widget(item)

    def sohbet_ac(self, sohbet_hedefi):
        self.aktif_sohbet_hedefi = sohbet_hedefi
        chat_ekrani = self.root.get_screen("chat")
        chat_ekrani.ids.chat_baslik.title = f"@{sohbet_hedefi}"
        chat_ekrani.ids.chat_box.clear_widgets()
        oda_id = "_".join(sorted([self.aktif_kullanici, sohbet_hedefi]))
        gecmis = self.veritabani.get("sohbetler", {}).get(oda_id, [])
        if gecmis:
            for msj in gecmis:
                self.balon_olustur(msj["metin"], msj["gonderen"] == self.aktif_kullanici)
        self.root.transition.direction = "left"
        self.root.current = "chat"

    def mesaj_gonder(self, mesaj):
        if not mesaj.strip(): return
        self.balon_olustur(mesaj, True)
        self.root.get_screen("chat").ids.mesaj_girdisi.text = ""
        oda_id = "_".join(sorted([self.aktif_kullanici, self.aktif_sohbet_hedefi]))
        if "sohbetler" not in self.veritabani: self.veritabani["sohbetler"] = {}
        if oda_id not in self.veritabani["sohbetler"]: self.veritabani["sohbetler"][oda_id] = []
        self.veritabani["sohbetler"][oda_id].append({"gonderen": self.aktif_kullanici, "metin": mesaj})
        self.veri_kaydet()

    def balon_olustur(self, mesaj, ben_miyim):
        renk = self.theme_cls.primary_color if ben_miyim else (0.2, 0.2, 0.2, 1)
        kart = MDCard(size_hint_y=None, size_hint_x=None, width="250dp", padding="10dp",
                      radius=[15, 15, 0, 15] if ben_miyim else [15, 15, 15, 0], md_bg_color=renk)
        lbl = MDLabel(text=mesaj, theme_text_color="Custom", text_color=(1, 1, 1, 1), adaptive_height=True)
        kart.add_widget(lbl)
        kart.adaptive_height = True
        satir = MDBoxLayout(adaptive_height=True)
        if ben_miyim:
            satir.add_widget(MDBoxLayout()); satir.add_widget(kart)
        else:
            satir.add_widget(kart); satir.add_widget(MDBoxLayout())
        self.root.get_screen("chat").ids.chat_box.add_widget(satir)

    def sohbetten_cik(self):
        self.root.transition.direction = "right"
        self.root.current = "main"


if __name__ == '__main__':
    NahogramApp().run()