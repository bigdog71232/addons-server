from django.core.exceptions import ValidationError

from olympia.amo.tests import addon_factory, TestCase
from olympia.hero.models import PrimaryHero, SecondaryHero, SecondaryHeroModule
from olympia.discovery.models import DiscoveryItem


class TestPrimaryHero(TestCase):
    def test_image_url(self):
        ph = PrimaryHero.objects.create(
            disco_addon=DiscoveryItem.objects.create(addon=addon_factory()),
            image='foo.png')
        assert ph.image_url == (
            'http://testserver/static/img/hero/featured/foo.png')

    def test_gradiant(self):
        ph = PrimaryHero.objects.create(
            disco_addon=DiscoveryItem.objects.create(addon=addon_factory()),
            gradient_color='#112233')
        assert ph.gradient == {'start': '#20123A', 'end': '#112233'}

    def test_clean(self):
        ph = PrimaryHero.objects.create(
            disco_addon=DiscoveryItem.objects.create(addon=addon_factory()))
        assert not ph.enabled
        ph.clean()  # it raises if there's an error
        ph.enabled = True
        with self.assertRaises(ValidationError):
            ph.clean()

        assert ph.disco_addon.recommended_status != ph.disco_addon.RECOMMENDED
        ph.disco_addon.update(recommendable=True)
        ph.disco_addon.addon.current_version.update(
            recommendation_approved=True)
        assert ph.disco_addon.recommended_status == ph.disco_addon.RECOMMENDED
        ph.clean()  # it raises if there's an error

    def test_clean_external(self):
        ph = PrimaryHero.objects.create(
            disco_addon=DiscoveryItem.objects.create(addon=addon_factory()),
            is_external=True)
        assert not ph.enabled
        ph.clean()  # it raises if there's an error
        ph.enabled = True
        with self.assertRaises(ValidationError):
            ph.clean()

        ph.disco_addon.addon.homepage = 'https://foobar.com/'
        ph.disco_addon.addon.save()
        ph.clean()  # it raises if there's an error

    def test_clean_only_enabled(self):
        hero = PrimaryHero.objects.create(
            disco_addon=DiscoveryItem.objects.create(addon=addon_factory()))
        hero.disco_addon.update(recommendable=True)
        hero.disco_addon.addon.current_version.update(
            recommendation_approved=True)
        assert not hero.enabled
        assert not PrimaryHero.objects.filter(enabled=True).exists()
        # It should still validate even if there are no other enabled shelves,
        # because we're not changing its enabled state.
        hero.clean()  # it raises if there's an error

        # Enabling the shelf is fine.
        hero.enabled = True
        hero.clean()  # it raises if there's an error
        hero.save()

        # Disabling it again is not.
        hero.enabled = False
        with self.assertRaises(ValidationError):
            hero.clean()

        # But if there's another shelf enabled, then it's fine to disable.
        PrimaryHero.objects.create(
            disco_addon=DiscoveryItem.objects.create(addon=addon_factory()),
            enabled=True)
        hero.clean()


class TestSecondaryHero(TestCase):

    def test_str(self):
        sh = SecondaryHero.objects.create(
            headline='Its a héadline!', description='description')
        assert str(sh) == 'Its a héadline!'

    def test_clean_cta(self):
        hero = SecondaryHero.objects.create()
        assert not hero.enabled
        hero.clean()  # it raises if there's an error

        # neither cta_url or cta_text are set, and that's okay.
        hero.enabled = True
        hero.clean()  # it raises if there's an error.

        # just set the url without the text is invalid when enabled though.
        hero.cta_url = 'http://goo.gl/'
        with self.assertRaises(ValidationError):
            hero.clean()
        hero.cta_url = None
        hero.cta_text = 'click it!'
        with self.assertRaises(ValidationError):
            hero.clean()
        hero.cta_url = ''
        with self.assertRaises(ValidationError):
            hero.clean()

        # No error if not enabled.
        hero.enabled = False
        hero.clean()  # it raises if there's an error

        # And setting both is okay too.
        hero.enabled = True
        hero.cta_url = 'http://goo.gl'
        hero.clean()  # it raises if there's an error

    def test_clean_only_enabled(self):
        hero = SecondaryHero.objects.create(
            headline='Its a héadline!', description='description')
        assert not hero.enabled
        assert not SecondaryHero.objects.filter(enabled=True).exists()
        # It should still validate even if there are no other enabled shelves,
        # because we're not changing its enabled state.
        hero.clean()  # it raises if there's an error

        # Enabling the shelf is fine.
        hero.enabled = True
        hero.clean()  # it raises if there's an error
        hero.save()

        # Disabling it again is not.
        hero.enabled = False
        with self.assertRaises(ValidationError):
            hero.clean()

        # But if there's another shelf enabled, then it's fine to disable.
        SecondaryHero.objects.create(
            headline='Its a héadline!', description='description',
            enabled=True)
        hero.clean()


class TestSecondaryHeroModule(TestCase):

    def test_str(self):
        shm = SecondaryHeroModule.objects.create(
            description='descríption',
            shelf=SecondaryHero.objects.create())
        assert str(shm) == 'descríption'

    def test_clean_cta(self):
        ph = SecondaryHeroModule.objects.create(
            shelf=SecondaryHero.objects.create())

        # neither cta_url or cta_text are set, and that's okay.
        ph.clean()  # it raises if there's an error.

        # just set the url without the text is invalid when enabled though.
        ph.cta_url = 'http://goo.gl/'
        with self.assertRaises(ValidationError):
            ph.clean()
        ph.cta_url = None
        ph.cta_text = 'click it!'
        with self.assertRaises(ValidationError):
            ph.clean()
        ph.cta_url = ''
        with self.assertRaises(ValidationError):
            ph.clean()

        # And setting both is okay too.
        ph.cta_url = 'http://goo.gl'
        ph.clean()  # it raises if there's an error

    def test_icon_url(self):
        ph = SecondaryHeroModule.objects.create(
            shelf=SecondaryHero.objects.create(),
            icon='foo.svg')
        assert ph.icon_url == (
            'http://testserver/static/img/hero/icons/foo.svg')
