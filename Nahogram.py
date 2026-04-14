# ==================================================
# 1. KIVY AYARLARI VE GÜVENLİK (ANDROID SSL DÜZELTMESİ)
# ==================================================
import os
import sys
import certifi

# Android'in internete bağlanmasını engelleyen SSL sorununu çözen pasaport:
os.environ['SSL_CERT_FILE'] = certifi.where()

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'multisamples', '0')

# ==================================================
# 2. KÜTÜPHANELER
# ==================================================
import shutil
import threading
import requests

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarListItem, IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem, \
    ImageLeftWidget
from kivy.utils import platform as os_platform
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp

# NATIVE (TELEFONUN KENDİ) GALERİSİ İÇİN
try:
    from plyer import filechooser
except ImportError:
    pass  # PyCharm kızmasın diye eklendi, PC'de 'pip install plyer' yapmalısın.


# EXE VE APK İÇİN KUSURSUZ LOGO/MEDYA YOL BULUCU
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ==================================================
# 3. BULUT VE VERİTABANI AYARLARI
# ==================================================
IMGBB_API_KEY = "d5c02fcbc393270969c05f80ea7f4b60"
FIREBASE_URL = "https://nahogram-5f474-default-rtdb.europe-west1.firebasedatabase.app"

# ==================================================
# 4. ARAYÜZ (KV DİLİ)
# ==================================================
KV_KODU = '''
ScreenManager:
    LoginScreen:
    SignupScreen:
    MainScreen:
    ChatScreen:

<YorumDialogIcerik>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "350dp"
    MDScrollView:
        MDList:
            id: yorumlar_listesi
    MDTextField:
        id: yorum_girdisi
        hint_text: "Bir yorum yaz..."
        mode: "fill"

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
        FitImage:
            source: app.logo_yolu
            size_hint: None, None
            size: "100dp", "100dp"
            pos_hint: {"center_x": .5}
            radius: [20, 20, 20, 20]
        MDLabel:
            text: "Nahogram"
            font_style: "H4"
            bold: True
            halign: "center"
            theme_text_color: "Primary"
        MDLabel:
            id: hata_mesaji
            text: "İnternet Taranıyor..."
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
                on_press:
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
                hata_mesaji.text = "Kayıt Ekranı"
                hata_mesaji.text_color = 1, 0.8, 0, 1

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
                on_press:
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
    height: icerik_kutusu.height + dp(30)
    elevation: 2
    radius: [15, 15, 15, 15]

    MDBoxLayout:
        id: icerik_kutusu
        orientation: "vertical"
        adaptive_height: True
        spacing: "10dp"

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
                    source: root.profil_foto if root.profil_foto else ""
                    size_hint: None, None
                    size: "40dp", "40dp"
                    radius: [20, 20, 20, 20]
                    opacity: 1 if root.profil_foto else 0
            MDLabel:
                text: root.username
                bold: True
                theme_text_color: "Primary"
                adaptive_height: True

        MDLabel:
            text: root.content
            theme_text_color: "Secondary"
            adaptive_height: True

        AsyncImage:
            source: root.post_resim if (root.post_resim and not root.is_video) else ""
            size_hint_y: None
            height: (self.width / self.image_ratio) if (self.image_ratio and self.source) else dp(0)
            allow_stretch: True
            keep_ratio: True
            opacity: 1 if (root.post_resim and not root.is_video) else 0

        VideoPlayer:
            source: root.post_resim if (root.post_resim and root.is_video) else ""
            size_hint_y: None
            height: "300dp" if (root.post_resim and root.is_video) else "0dp"
            options: {'eos': 'loop'}
            opacity: 1 if (root.post_resim and root.is_video) else 0

        MDBoxLayout:
            adaptive_height: True
            spacing: "15dp"

            MDBoxLayout:
                adaptive_size: True
                spacing: "5dp"
                MDIconButton:
                    icon: "heart" if root.is_liked else "heart-outline"
                    theme_text_color: "Custom"
                    text_color: (1, 0, 0, 1) if root.is_liked else app.theme_cls.text_color
                    on_release: app.gonderi_begen(root.post_id, root.db_hedef)
                    size_hint_x: None
                    width: "36dp"
                MDLabel:
                    text: str(root.like_count)
                    adaptive_size: True
                    pos_hint: {"center_y": .5}

            MDBoxLayout:
                adaptive_size: True
                spacing: "5dp"
                MDIconButton:
                    icon: "comment-outline"
                    on_release: app.yorum_penceresi_ac(root.post_id, root.db_hedef)
                    size_hint_x: None
                    width: "36dp"
                MDLabel:
                    text: str(root.comment_count)
                    adaptive_size: True
                    pos_hint: {"center_y": .5}

            Widget: 

            MDIconButton:
                icon: "trash-can-outline"
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                opacity: 1 if root.is_mine else 0
                disabled: not root.is_mine
                on_release: app.gonderi_sil(root.post_id, root.db_hedef)
                size_hint_x: None
                width: "36dp"

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Nahogram"
            left_action_items: [["cloud-sync", lambda x: app.tum_akisleri_yenile()]]
            right_action_items: [["logout", lambda x: app.cikis_yap()]]
            elevation: 3

        MDBottomNavigation:
            panel_color: app.theme_cls.bg_dark

            MDBottomNavigationItem:
                name: 'screen_home'
                text: 'Akış'
                icon: 'home'
                on_tab_press: app.akis_yenile()
                MDScrollView:
                    MDBoxLayout:
                        id: feed_box
                        orientation: "vertical"
                        spacing: "15dp"
                        padding: "15dp"
                        adaptive_height: True

            MDBottomNavigationItem:
                name: 'screen_nahools'
                text: 'Nahools'
                icon: 'play-box-multiple'
                on_tab_press: app.nahools_yenile()
                MDScrollView:
                    MDBoxLayout:
                        id: nahools_box
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
                    spacing: "15dp"

                    MDLabel:
                        id: lbl_paylasim_uyari
                        text: ""
                        theme_text_color: "Error"
                        halign: "center"
                        adaptive_height: True

                    MDTextField:
                        id: paylasim_kutusu
                        hint_text: "Bugün ne düşünüyorsun?"
                        mode: "fill"
                        multiline: True
                        max_height: "120dp"

                    AsyncImage:
                        id: onizleme_resim
                        source: ""
                        size_hint_y: None
                        height: (self.width / self.image_ratio) if (self.image_ratio and self.source) else dp(0)
                        allow_stretch: True
                        keep_ratio: True

                    MDLabel:
                        id: secili_resim_lbl
                        text: "Medya Eklenmedi"
                        theme_text_color: "Secondary"
                        halign: "center"
                        adaptive_height: True

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "10dp"
                        pos_hint: {"center_x": .5}
                        MDRaisedButton:
                            text: "Medya Ekle"
                            icon: "folder-multiple-image"
                            on_release: app.dosya_seciciyi_ac("post")
                        MDRaisedButton:
                            id: btn_iptal
                            text: "İptal Et"
                            md_bg_color: 1, 0, 0, 1
                            opacity: 0
                            disabled: True
                            on_release: app.resim_iptal()

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "15dp"
                        pos_hint: {"center_x": .5}
                        MDRaisedButton:
                            id: btn_paylas_akis
                            text: "Akış'a Gönder"
                            md_bg_color: app.theme_cls.primary_color
                            on_release: app.gonderi_paylas(paylasim_kutusu.text, "akis")
                        MDRaisedButton:
                            id: btn_paylas_nahools
                            text: "Nahools'a Gönder"
                            md_bg_color: 0.8, 0.2, 0.5, 1 
                            on_release: app.gonderi_paylas(paylasim_kutusu.text, "nahools")
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
                                        source: app.aktif_profil_foto if app.aktif_profil_foto else ""
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
                                        on_release: app.dosya_seciciyi_ac("profil")
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

                        MDTextField:
                            id: profil_bio
                            hint_text: "Biyografi"
                            mode: "rectangle"
                            multiline: True
                        MDTextField:
                            id: profil_hedef
                            hint_text: "Hedeflerimiz"
                            mode: "rectangle"
                            multiline: True
                        MDRaisedButton:
                            id: btn_profil_kaydet
                            text: "Profili Kaydet"
                            pos_hint: {"center_x": .5}
                            on_release: app.profil_guncelle(profil_bio.text, profil_hedef.text)

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
# 5. PYTHON MANTIĞI VE YÜKSEK PERFORMANSLI MOTOR
# ==================================================

class YorumDialogIcerik(MDBoxLayout):
    pass


class LoginScreen(MDScreen): pass


class SignupScreen(MDScreen): pass


class MainScreen(MDScreen): pass


class ChatScreen(MDScreen): pass


class PostCard(MDCard):
    post_id = StringProperty()
    db_hedef = StringProperty("gonderiler")
    username = StringProperty()
    content = StringProperty()
    profil_foto = StringProperty("")
    post_resim = StringProperty("")
    is_video = BooleanProperty(False)
    is_mine = BooleanProperty(False)
    is_liked = BooleanProperty(False)
    like_count = NumericProperty(0)
    comment_count = NumericProperty(0)


class NahogramApp(MDApp):
    aktif_profil_foto = StringProperty("")
    logo_yolu = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aktif_kullanici = ""
        self.aktif_sohbet_hedefi = ""
        self.resim_hedefi = "profil"
        self.gecici_post_resmi = ""
        self.yorum_dialog = None
        self.sohbet_radari = None
        self.odadaki_mesaj_sayisi = -1
        # GÜVENLİ LOGO YOLU BULUCU (APK VE EXE İÇİN)
        self.logo_yolu = resource_path("ngram.jpeg")

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        if os.path.exists(self.logo_yolu):
            self.icon = self.logo_yolu

        # MOBİLDE UYGULAMA AÇILINCA GALERİ İZNİ İSTER (BUNU YAPMAZSAK GALERİ AÇILMAZ)
        if os_platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions(
                    [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])
            except ImportError:
                pass

        return Builder.load_string(KV_KODU)

    def on_start(self):
        self.internet_ve_bulut_kontrol()

    def resmi_buluta_yukle(self, yol):
        try:
            with open(yol, "rb") as file:
                payload = {"key": IMGBB_API_KEY}
                files = {"image": file}
                res = requests.post("https://api.imgbb.com/1/upload", data=payload, files=files, timeout=30,
                                    verify=certifi.where())
                if res.status_code == 200:
                    return res.json()['data']['url']
        except Exception:
            return ""
        return ""

    def internet_ve_bulut_kontrol(self):
        ekran = self.root.get_screen("login")

        def islem():
            try:
                # verify=certifi.where() İLE ANDROID'İN İNTERNET ENGELİNİ AŞIYORUZ!
                cevap = requests.get(f"{FIREBASE_URL}/nahogram.json", timeout=5, verify=certifi.where())
                if cevap.status_code == 200:
                    Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text', "Online: Dünyaya Bağlı 🌍"))
                    Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text_color', (0, 0.8, 0, 1)))
                else:
                    Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text', "Bağlantı Hatası!"))
                    Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text_color', (1, 0, 0, 1)))
            except:
                Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text', "Sunucuya Ulaşılamadı"))
                Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text_color', (1, 0, 0, 1)))

        threading.Thread(target=islem).start()

    # SİYAH EKRAN VEREN ESKİ DOSYA SEÇİCİ ÇÖPE ATILDI, ORİJİNAL GALERİ (PLYER) GELDİ
    def dosya_seciciyi_ac(self, hedef="profil"):
        self.resim_hedefi = hedef
        try:
            filechooser.open_file(on_selection=self.dosya_secildi_callback)
        except Exception as e:
            print("Galeri açılamadı:", e)

    def dosya_secildi_callback(self, selection):
        if selection:
            secilen_yol = selection[0]
            Clock.schedule_once(lambda dt: self.dosya_isle(secilen_yol))

    def dosya_isle(self, secilen_yol):
        if self.resim_hedefi == "post":
            self.gecici_post_resmi = secilen_yol
            screen_add_ids = self.root.get_screen("main").ids
            screen_add_ids.secili_resim_lbl.text = f"Medya Seçildi: {os.path.basename(secilen_yol)}"
            screen_add_ids.secili_resim_lbl.theme_text_color = "Custom"
            screen_add_ids.secili_resim_lbl.text_color = (0, 1, 0, 1)

            is_video = secilen_yol.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
            if not is_video:
                screen_add_ids.onizleme_resim.source = secilen_yol
            else:
                screen_add_ids.onizleme_resim.source = self.logo_yolu

            screen_add_ids.btn_iptal.opacity = 1
            screen_add_ids.btn_iptal.disabled = False
            screen_add_ids.lbl_paylasim_uyari.text = ""

        elif self.resim_hedefi == "profil":
            def islem():
                bulut_linki = self.resmi_buluta_yukle(secilen_yol)
                if bulut_linki:
                    requests.patch(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                                   json={"profil_foto": bulut_linki}, verify=certifi.where())

                    def arayuzu_guncelle(dt):
                        self.aktif_profil_foto = bulut_linki
                        self.tum_akisleri_yenile()

                    Clock.schedule_once(arayuzu_guncelle)

            threading.Thread(target=islem).start()

    def resim_iptal(self):
        self.gecici_post_resmi = ""
        screen_add_ids = self.root.get_screen("main").ids
        screen_add_ids.secili_resim_lbl.text = "Medya Eklenmedi"
        screen_add_ids.secili_resim_lbl.theme_text_color = "Secondary"
        screen_add_ids.onizleme_resim.source = ""
        screen_add_ids.btn_iptal.opacity = 0
        screen_add_ids.btn_iptal.disabled = True
        screen_add_ids.lbl_paylasim_uyari.text = ""

    def giris_yap(self, kullanici_adi, sifre):
        ekran = self.root.get_screen("login")

        def islem():
            try:
                res = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{kullanici_adi}.json", verify=certifi.where())
                if res.status_code == 200 and res.json():
                    kullanici_verisi = res.json()
                    if kullanici_verisi["sifre"] == sifre:
                        def arayuz_giris(dt):
                            self.aktif_kullanici = kullanici_adi
                            self.aktif_profil_foto = kullanici_verisi.get("profil_foto", "")
                            self.profil_bilgilerini_yukle()
                            self.tum_akisleri_yenile()
                            self.root.current = "main"

                        Clock.schedule_once(arayuz_giris)
                    else:
                        Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text', "Şifre Yanlış!"))
                        Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text_color', (1, 0, 0, 1)))
                else:
                    Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text', "Böyle bir kullanıcı yok!"))
                    Clock.schedule_once(lambda dt: setattr(ekran.ids.hata_mesaji, 'text_color', (1, 0, 0, 1)))
            except:
                pass

        threading.Thread(target=islem).start()

    def kayit_ol(self, kullanici_adi, sifre):
        ekran = self.root.get_screen("signup")
        if kullanici_adi and sifre:
            def islem():
                try:
                    kontrol = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{kullanici_adi}.json",
                                           verify=certifi.where())
                    if kontrol.json() is None:
                        # VERİ EZİLMESİNİ ÖNLEYEN YENİ KAYIT SİSTEMİ (Sadece kendi adıyla bir klasör oluşturur)
                        yeni_hesap_bilgileri = {
                            "sifre": sifre, "gonderi": 0, "takipci": 0, "takip": 0,
                            "takip_edilenler": [], "profil_foto": "", "bio": "", "hedef": ""
                        }
                        requests.put(f"{FIREBASE_URL}/nahogram/kullanicilar/{kullanici_adi}.json",
                                     json=yeni_hesap_bilgileri, verify=certifi.where())
                        self.giris_yap(kullanici_adi, sifre)
                    else:
                        Clock.schedule_once(
                            lambda dt: setattr(ekran.ids.hata_mesaji, 'text', "Bu kullanıcı adı alınmış!"))
                except:
                    pass

            threading.Thread(target=islem).start()
        else:
            ekran.ids.hata_mesaji.text = "Boş alan bırakılamaz!"

    def cikis_yap(self):
        self.aktif_kullanici = ""
        self.aktif_profil_foto = ""
        if self.sohbet_radari:
            self.sohbet_radari.cancel()
            self.sohbet_radari = None
        self.root.current = "login"

    def gonderi_begen(self, post_id, db_hedef):
        islem_tipi = ""
        hedef_kutu = self.root.get_screen("main").ids.feed_box if db_hedef == "gonderiler" else self.root.get_screen(
            "main").ids.nahools_box

        for child in hedef_kutu.children:
            if hasattr(child, 'post_id') and child.post_id == post_id:
                if child.is_liked:
                    child.is_liked = False
                    child.like_count = max(0, child.like_count - 1)
                    islem_tipi = "sil"
                else:
                    child.is_liked = True
                    child.like_count += 1
                    islem_tipi = "ekle"
                break

        def islem():
            if islem_tipi == "sil":
                requests.delete(f"{FIREBASE_URL}/nahogram/{db_hedef}/{post_id}/begenenler/{self.aktif_kullanici}.json",
                                verify=certifi.where())
            elif islem_tipi == "ekle":
                requests.patch(f"{FIREBASE_URL}/nahogram/{db_hedef}/{post_id}/begenenler.json",
                               json={self.aktif_kullanici: True}, verify=certifi.where())

        threading.Thread(target=islem).start()

    def yorum_penceresi_ac(self, post_id, db_hedef):
        def islem():
            res = requests.get(f"{FIREBASE_URL}/nahogram/{db_hedef}/{post_id}/yorumlar.json", timeout=10,
                               verify=certifi.where())
            yorumlar = res.json() if res.status_code == 200 and res.json() else {}

            def arayuzu_ciz(dt):
                icerik = YorumDialogIcerik()
                if isinstance(yorumlar, dict):
                    for y_id, y_data in yorumlar.items():
                        icerik.ids.yorumlar_listesi.add_widget(
                            TwoLineAvatarListItem(text=f"@{y_data.get('kullanici', 'Bilinmeyen')}",
                                                  secondary_text=y_data.get('metin', ''))
                        )
                elif isinstance(yorumlar, list):
                    for y_data in yorumlar:
                        if y_data and isinstance(y_data, dict):
                            icerik.ids.yorumlar_listesi.add_widget(
                                TwoLineAvatarListItem(text=f"@{y_data.get('kullanici', 'Bilinmeyen')}",
                                                      secondary_text=y_data.get('metin', ''))
                            )

                self.yorum_dialog = MDDialog(
                    title="Yorumlar",
                    type="custom",
                    content_cls=icerik,
                    buttons=[
                        MDRaisedButton(text="Kapat", md_bg_color=(1, 0, 0, 1),
                                       on_release=lambda x: self.yorum_dialog.dismiss()),
                        MDRaisedButton(text="Gönder",
                                       on_release=lambda x: self.yorum_gonder(post_id, icerik.ids.yorum_girdisi.text,
                                                                              db_hedef))
                    ]
                )
                self.yorum_dialog.open()

            Clock.schedule_once(arayuzu_ciz)

        threading.Thread(target=islem).start()

    def yorum_gonder(self, post_id, metin, db_hedef):
        if not metin.strip(): return

        # YORUM SAYISININ ANINDA GÜNCELLENMESİ
        if self.yorum_dialog:
            icerik = self.yorum_dialog.content_cls
            icerik.ids.yorumlar_listesi.add_widget(
                TwoLineAvatarListItem(text=f"@{self.aktif_kullanici}", secondary_text=metin)
            )
            icerik.ids.yorum_girdisi.text = ""

        hedef_kutu = self.root.get_screen("main").ids.feed_box if db_hedef == "gonderiler" else self.root.get_screen(
            "main").ids.nahools_box
        for child in hedef_kutu.children:
            if hasattr(child, 'post_id') and child.post_id == post_id:
                # Kivy arayüzünü güvenli bir şekilde ana işçiye (Main Thread) güncelletiyoruz
                def sayaci_artir(dt, c=child):
                    c.comment_count += 1

                Clock.schedule_once(sayaci_artir)
                break

        def islem():
            res = requests.get(f"{FIREBASE_URL}/nahogram/{db_hedef}/{post_id}/yorumlar.json", verify=certifi.where())
            mevcut_yorumlar = []
            if res.status_code == 200 and res.json():
                gelen = res.json()
                if isinstance(gelen, dict):
                    mevcut_yorumlar = list(gelen.values())
                elif isinstance(gelen, list):
                    mevcut_yorumlar = [y for y in gelen if y]

            mevcut_yorumlar.append({"kullanici": self.aktif_kullanici, "metin": metin})
            requests.put(f"{FIREBASE_URL}/nahogram/{db_hedef}/{post_id}/yorumlar.json", json=mevcut_yorumlar,
                         verify=certifi.where())

        threading.Thread(target=islem).start()

    def tum_akisleri_yenile(self):
        self.akis_yenile()
        self.nahools_yenile()

    def akis_yenile(self):
        feed_box = self.root.get_screen("main").ids.feed_box
        feed_box.clear_widgets()

        def islem():
            try:
                gonderiler_res = requests.get(f"{FIREBASE_URL}/nahogram/gonderiler.json", verify=certifi.where())
                if gonderiler_res.status_code == 200 and gonderiler_res.json():
                    ham_gonderiler = gonderiler_res.json()

                    gonderiler = {}
                    if isinstance(ham_gonderiler, dict):
                        gonderiler = ham_gonderiler
                    elif isinstance(ham_gonderiler, list):
                        for i, g in enumerate(ham_gonderiler):
                            if g and isinstance(g, dict): gonderiler[str(i)] = g

                    cizilecekler = []
                    post_keys = list(gonderiler.keys())[-50:]

                    for key in reversed(post_keys):
                        gonderi = gonderiler[key]
                        sahibi = gonderi.get('kullanici', '')
                        begenenler = gonderi.get('begenenler', {})
                        yorumlar = gonderi.get('yorumlar', {})
                        is_video = gonderi.get('is_video', False)

                        is_liked = False
                        if isinstance(begenenler, dict):
                            is_liked = self.aktif_kullanici in begenenler
                        elif isinstance(begenenler, list):
                            is_liked = self.aktif_kullanici in [b for b in begenenler if b]

                        if isinstance(yorumlar, dict):
                            c_count = len(yorumlar)
                        elif isinstance(yorumlar, list):
                            c_count = len([y for y in yorumlar if y])
                        else:
                            c_count = 0

                        cizilecekler.append({
                            "post_id": str(key),
                            "db_hedef": "gonderiler",
                            "username": f"@{sahibi}",
                            "content": gonderi.get('icerik', ''),
                            "profil_foto": gonderi.get('profil_foto', ''),
                            "post_resim": gonderi.get("resim", ""),
                            "is_video": is_video,
                            "is_mine": (sahibi == self.aktif_kullanici),
                            "is_liked": is_liked,
                            "like_count": len(begenenler) if isinstance(begenenler, dict) else len(
                                [b for b in begenenler if b]),
                            "comment_count": c_count
                        })

                    def arayuzu_ciz(dt):
                        for veri in cizilecekler:
                            feed_box.add_widget(PostCard(**veri))

                    Clock.schedule_once(arayuzu_ciz)
            except Exception:
                pass

        threading.Thread(target=islem).start()

    def nahools_yenile(self):
        nahools_box = self.root.get_screen("main").ids.nahools_box
        nahools_box.clear_widgets()

        def islem():
            try:
                nahools_res = requests.get(f"{FIREBASE_URL}/nahogram/nahools.json", verify=certifi.where())
                if nahools_res.status_code == 200 and nahools_res.json():
                    gonderiler = nahools_res.json()
                    cizilecekler = []
                    post_keys = list(gonderiler.keys())[-50:]

                    for key in reversed(post_keys):
                        gonderi = gonderiler[key]
                        sahibi = gonderi.get('kullanici', '')
                        begenenler = gonderi.get('begenenler', {})
                        yorumlar = gonderi.get('yorumlar', {})
                        is_video = gonderi.get('is_video', False)

                        is_liked = False
                        if isinstance(begenenler, dict): is_liked = self.aktif_kullanici in begenenler

                        c_count = len(yorumlar) if isinstance(yorumlar, dict) else len([y for y in yorumlar if y])

                        cizilecekler.append({
                            "post_id": str(key),
                            "db_hedef": "nahools",
                            "username": f"@{sahibi}",
                            "content": gonderi.get('icerik', ''),
                            "profil_foto": gonderi.get('profil_foto', ''),
                            "post_resim": gonderi.get("resim", ""),
                            "is_video": is_video,
                            "is_mine": (sahibi == self.aktif_kullanici),
                            "is_liked": is_liked,
                            "like_count": len(begenenler) if isinstance(begenenler, dict) else 0,
                            "comment_count": c_count
                        })

                    def arayuzu_ciz(dt):
                        for veri in cizilecekler:
                            nahools_box.add_widget(PostCard(**veri))

                    Clock.schedule_once(arayuzu_ciz)
            except Exception:
                pass

        threading.Thread(target=islem).start()

    def gonderi_paylas(self, icerik, hedef_tab):
        main_ids = self.root.get_screen("main").ids
        main_ids.lbl_paylasim_uyari.text = ""

        is_video = self.gecici_post_resmi.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))

        if hedef_tab == "akis" and is_video:
            main_ids.lbl_paylasim_uyari.text = "Hata! Akışa video gönderilemez."
            return

        if hedef_tab == "nahools" and not self.gecici_post_resmi:
            main_ids.lbl_paylasim_uyari.text = "Hata! Nahools'a kamerasız (medyasız) gönderi yapılamaz."
            return

        if not icerik.strip() and not self.gecici_post_resmi:
            return

        btn_aktif = main_ids.btn_paylas_akis if hedef_tab == "akis" else main_ids.btn_paylas_nahools
        btn_aktif.text = "Yükleniyor..."
        btn_aktif.disabled = True

        guncel_gonderi_sayisi = int(main_ids.txt_gonderi_sayi.text) + 1

        def islem():
            try:
                son_resim_url = ""
                if self.gecici_post_resmi:
                    if is_video:
                        hedef_klasor = os.path.join(self.user_data_dir, "nahogram_videolar")
                        os.makedirs(hedef_klasor, exist_ok=True)
                        yeni_yol = os.path.join(hedef_klasor, os.path.basename(self.gecici_post_resmi))
                        shutil.copy(self.gecici_post_resmi, yeni_yol)
                        son_resim_url = yeni_yol
                    else:
                        son_resim_url = self.resmi_buluta_yukle(self.gecici_post_resmi)

                yeni_gonderi = {
                    "kullanici": self.aktif_kullanici,
                    "icerik": icerik.strip(),
                    "resim": son_resim_url,
                    "is_video": is_video,
                    "profil_foto": self.aktif_profil_foto
                }

                db_odasi = "gonderiler" if hedef_tab == "akis" else "nahools"
                requests.post(f"{FIREBASE_URL}/nahogram/{db_odasi}.json", json=yeni_gonderi, verify=certifi.where())
                requests.patch(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                               json={"gonderi": guncel_gonderi_sayisi}, verify=certifi.where())

                def arayuzu_sifirla(dt):
                    self.profil_bilgilerini_yukle()
                    self.resim_iptal()
                    main_ids.paylasim_kutusu.text = ""
                    main_ids.btn_paylas_akis.text = "Akış'a Gönder"
                    main_ids.btn_paylas_akis.disabled = False
                    main_ids.btn_paylas_nahools.text = "Nahools'a Gönder"
                    main_ids.btn_paylas_nahools.disabled = False

                    if hedef_tab == "akis":
                        self.akis_yenile()
                    else:
                        self.nahools_yenile()

                Clock.schedule_once(arayuzu_sifirla)

            except Exception:
                def hata_var(dt):
                    btn_aktif.text = "Hata! Tekrar Dene"
                    btn_aktif.disabled = False

                Clock.schedule_once(hata_var)

        threading.Thread(target=islem).start()

    def gonderi_sil(self, post_id, db_hedef):
        def islem():
            requests.delete(f"{FIREBASE_URL}/nahogram/{db_hedef}/{post_id}.json", verify=certifi.where())
            benim_verim = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                                       verify=certifi.where()).json()
            yeni_gonderi_sayisi = max(0, benim_verim.get("gonderi", 1) - 1)
            requests.patch(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                           json={"gonderi": yeni_gonderi_sayisi}, verify=certifi.where())

            def arayuzu_guncelle(dt):
                self.profil_bilgilerini_yukle()
                if db_hedef == "gonderiler":
                    self.akis_yenile()
                else:
                    self.nahools_yenile()

            Clock.schedule_once(arayuzu_guncelle)

        threading.Thread(target=islem).start()

    def kullanici_ara(self, sorgu):
        sorgu = sorgu.strip()
        liste = self.root.get_screen("main").ids.arama_sonuclari_listesi
        bilgi = self.root.get_screen("main").ids.arama_bilgi
        liste.clear_widgets()
        if not sorgu:
            bilgi.text = "Lütfen bir isim yazın."
            return

        def islem():
            res = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar.json", verify=certifi.where())
            if res.status_code == 200 and res.json():
                ham_kullanicilar = res.json()
                kullanicilar = {}
                if isinstance(ham_kullanicilar, dict):
                    kullanicilar = ham_kullanicilar
                elif isinstance(ham_kullanicilar, list):
                    for i, k in enumerate(ham_kullanicilar):
                        if k and isinstance(k, dict): kullanicilar[str(i)] = k

                liste_elemanlari = []
                benim_bilgilerim = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                                                verify=certifi.where()).json()
                takip_listem = benim_bilgilerim.get("takip_edilenler", []) if benim_bilgilerim else []
                if not takip_listem: takip_listem = []

                for k_adi in kullanicilar:
                    if sorgu.lower() in k_adi.lower() and k_adi != self.aktif_kullanici:
                        takipte_mi = k_adi in takip_listem
                        liste_elemanlari.append({
                            "k_adi": k_adi,
                            "takipci": kullanicilar[k_adi].get('takipci', 0),
                            "p_foto": kullanicilar[k_adi].get("profil_foto", ""),
                            "takipte_mi": takipte_mi
                        })

                def arayuzu_ciz(dt):
                    if len(liste_elemanlari) == 0:
                        bilgi.text = "Kullanıcı bulunamadı."
                        return
                    bilgi.text = "Sonuçlar listelendi."
                    for veri in liste_elemanlari:
                        ikon = "check-circle" if veri["takipte_mi"] else "account-plus"
                        renk = "Custom" if veri["takipte_mi"] else "Primary"

                        # PYCHARM KIZMASIN DİYE KUSURSUZ YAZIM ŞEKLİ
                        l_elemani = TwoLineAvatarIconListItem()
                        l_elemani.text = f"@{veri['k_adi']}"
                        l_elemani.secondary_text = f"{veri['takipci']} Takipçi"

                        if veri["p_foto"]:
                            l_elemani.add_widget(ImageLeftWidget(source=veri["p_foto"]))
                        else:
                            l_elemani.add_widget(IconLeftWidget(icon="account-circle"))

                        btn = IconRightWidget(icon=ikon, theme_text_color=renk, text_color=self.theme_cls.primary_color)
                        btn.bind(on_release=lambda instance, hedef=veri['k_adi'], b=btn: self.takip_et(hedef, b))
                        l_elemani.add_widget(btn)
                        liste.add_widget(l_elemani)

                Clock.schedule_once(arayuzu_ciz)

        threading.Thread(target=islem).start()

    def takip_et(self, hedef_kisi, buton_objesi):
        def islem():
            benim_verim = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                                       verify=certifi.where()).json()
            hedef_veri = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{hedef_kisi}.json",
                                      verify=certifi.where()).json()
            takip_listesi = benim_verim.get("takip_edilenler", [])
            if not takip_listesi: takip_listesi = []
            if hedef_kisi in takip_listesi: return
            takip_listesi.append(hedef_kisi)
            yeni_takip_sayim = benim_verim.get("takip", 0) + 1
            yeni_hedef_takipci = hedef_veri.get("takipci", 0) + 1
            requests.patch(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                           json={"takip_edilenler": takip_listesi, "takip": yeni_takip_sayim}, verify=certifi.where())
            requests.patch(f"{FIREBASE_URL}/nahogram/kullanicilar/{hedef_kisi}.json",
                           json={"takipci": yeni_hedef_takipci}, verify=certifi.where())

            def arayuzu_guncelle(dt):
                self.profil_bilgilerini_yukle()
                buton_objesi.icon = "check-circle"
                buton_objesi.theme_text_color = "Custom"
                buton_objesi.text_color = self.theme_cls.primary_color

            Clock.schedule_once(arayuzu_guncelle)

        threading.Thread(target=islem).start()

    def profil_bilgilerini_yukle(self):
        def islem():
            res = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                               verify=certifi.where())
            if res.status_code == 200 and res.json():
                kullanici = res.json()

                def arayuzu_guncelle(dt):
                    main_ids = self.root.get_screen("main").ids
                    main_ids.profil_isim.text = f"@{self.aktif_kullanici}"
                    main_ids.txt_gonderi_sayi.text = str(kullanici.get('gonderi', 0))
                    main_ids.txt_takipci_sayi.text = str(kullanici.get('takipci', 0))
                    main_ids.txt_takip_sayi.text = str(kullanici.get('takip', 0))
                    main_ids.profil_bio.text = kullanici.get('bio', '')
                    main_ids.profil_hedef.text = kullanici.get('hedef', '')

                Clock.schedule_once(arayuzu_guncelle)

        threading.Thread(target=islem).start()

    def profil_guncelle(self, bio_yazisi, hedef_yazisi):
        main_ids = self.root.get_screen("main").ids
        main_ids.btn_profil_kaydet.text = "Kaydediliyor..."

        def islem():
            requests.patch(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                           json={"bio": bio_yazisi, "hedef": hedef_yazisi}, verify=certifi.where())
            Clock.schedule_once(lambda dt: setattr(main_ids.btn_profil_kaydet, 'text', "Profili Kaydet"))

        threading.Thread(target=islem).start()

    def mesaj_listesini_olustur(self):
        liste = self.root.get_screen("main").ids.mesajlar_listesi
        liste.clear_widgets()

        def islem():
            try:
                ben = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar/{self.aktif_kullanici}.json",
                                   verify=certifi.where()).json()
                if not ben: return
                takip_edilenler = ben.get("takip_edilenler", [])

                if not takip_edilenler:
                    def bos_ekran(dt):
                        uyari = TwoLineAvatarListItem()
                        uyari.text = "Sohbet Edecek Kimse Yok"
                        uyari.secondary_text = "Önce birilerini takip etmelisin!"
                        liste.add_widget(uyari)

                    Clock.schedule_once(bos_ekran)
                    return

                ham_kullanicilar = requests.get(f"{FIREBASE_URL}/nahogram/kullanicilar.json",
                                                verify=certifi.where()).json()
                kullanicilar = {}
                if isinstance(ham_kullanicilar, dict):
                    kullanicilar = ham_kullanicilar
                elif isinstance(ham_kullanicilar, list):
                    for i, k in enumerate(ham_kullanicilar):
                        if k and isinstance(k, dict): kullanicilar[str(i)] = k

                arkadaslar_verisi = []
                for k_adi in takip_edilenler:
                    if not k_adi: continue
                    arkadaslar_verisi.append({
                        "k_adi": k_adi,
                        "p_foto": kullanicilar.get(k_adi, {}).get("profil_foto", "")
                    })

                def arayuzu_ciz(dt):
                    for v in arkadaslar_verisi:
                        item = TwoLineAvatarListItem()
                        item.text = f"@{v['k_adi']}"
                        item.secondary_text = "Sohbet başlat..."
                        item.bind(on_release=lambda x, hedef=v['k_adi']: self.sohbet_ac(hedef))
                        if v['p_foto']:
                            item.add_widget(ImageLeftWidget(source=v['p_foto']))
                        else:
                            item.add_widget(IconLeftWidget(icon="account"))
                        liste.add_widget(item)

                Clock.schedule_once(arayuzu_ciz)
            except Exception:
                pass

        threading.Thread(target=islem).start()

    def sohbet_yenile(self, dt):
        oda_id = "_".join(sorted([self.aktif_kullanici, self.aktif_sohbet_hedefi]))

        def islem():
            res = requests.get(f"{FIREBASE_URL}/nahogram/sohbetler/{oda_id}.json", verify=certifi.where())
            if res.status_code == 200 and res.json():
                gelen_veri = res.json()
                mesaj_listesi = []
                if isinstance(gelen_veri, dict):
                    mesaj_listesi = list(gelen_veri.values())
                elif isinstance(gelen_veri, list):
                    mesaj_listesi = [m for m in gelen_veri if m]

                if len(mesaj_listesi) != self.odadaki_mesaj_sayisi:
                    self.odadaki_mesaj_sayisi = len(mesaj_listesi)

                    def arayuzu_ciz(dt_ic):
                        chat_box = self.root.get_screen("chat").ids.chat_box
                        chat_box.clear_widgets()
                        for msj in mesaj_listesi:
                            ben_miyim = (msj.get("gonderen", "") == self.aktif_kullanici)
                            self.balon_olustur(msj.get("metin", ""), ben_miyim)

                    Clock.schedule_once(arayuzu_ciz)

        threading.Thread(target=islem).start()

    def sohbet_ac(self, sohbet_hedefi):
        self.aktif_sohbet_hedefi = sohbet_hedefi
        self.odadaki_mesaj_sayisi = -1

        chat_ekrani = self.root.get_screen("chat")
        chat_ekrani.ids.chat_baslik.title = f"@{sohbet_hedefi}"
        chat_ekrani.ids.chat_box.clear_widgets()

        self.root.transition.direction = "left"
        self.root.current = "chat"

        self.sohbet_yenile(0)
        if self.sohbet_radari:
            self.sohbet_radari.cancel()
        self.sohbet_radari = Clock.schedule_interval(self.sohbet_yenile, 3)

    def mesaj_gonder(self, mesaj):
        if not mesaj.strip(): return

        self.balon_olustur(mesaj, True)
        self.odadaki_mesaj_sayisi += 1
        self.root.get_screen("chat").ids.mesaj_girdisi.text = ""

        def islem():
            oda_id = "_".join(sorted([self.aktif_kullanici, self.aktif_sohbet_hedefi]))
            res = requests.get(f"{FIREBASE_URL}/nahogram/sohbetler/{oda_id}.json", verify=certifi.where())
            mevcut_mesajlar = []
            if res.status_code == 200 and res.json():
                gelen = res.json()
                if isinstance(gelen, dict):
                    mevcut_mesajlar = list(gelen.values())
                elif isinstance(gelen, list):
                    mevcut_mesajlar = [m for m in gelen if m]

            yeni_mesaj = {"gonderen": self.aktif_kullanici, "metin": mesaj}
            mevcut_mesajlar.append(yeni_mesaj)
            requests.put(f"{FIREBASE_URL}/nahogram/sohbetler/{oda_id}.json", json=mevcut_mesajlar,
                         verify=certifi.where())

        threading.Thread(target=islem).start()

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
        if self.sohbet_radari:
            self.sohbet_radari.cancel()
            self.sohbet_radari = None

        self.root.transition.direction = "right"
        self.root.current = "main"


if __name__ == '__main__':
    NahogramApp().run()