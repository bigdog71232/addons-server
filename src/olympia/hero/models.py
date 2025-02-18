import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.widgets import RadioSelect

from olympia.amo.models import ModelBase
from olympia.discovery.models import DiscoveryItem


GRADIENT_START_COLOR = '#20123A'
GRADIENT_CHOICES = (
    ('#054096', 'BLUE70'),
    ('#068989', 'GREEN70'),
    ('#C60184', 'PINK70'),
    ('#712290', 'PURPLE70'),
    ('#582ACB', 'VIOLET70'),
)
FEATURED_IMAGE_PATH = os.path.join(
    settings.ROOT, 'static', 'img', 'hero', 'featured')
MODULE_ICON_PATH = os.path.join(
    settings.ROOT, 'static', 'img', 'hero', 'icons')
FEATURED_IMAGE_URL = f'{settings.STATIC_URL}img/hero/featured/'
MODULE_ICON_URL = f'{settings.STATIC_URL}img/hero/icons/'


class GradientChoiceWidget(RadioSelect):
    option_template_name = 'hero/gradient_option.html'
    option_inherits_attrs = True

    def create_option(self, name, value, label, selected, index,
                      subindex=None, attrs=None):
        attrs['gradient_end_color'] = value
        attrs['gradient_start_color'] = GRADIENT_START_COLOR
        return super().create_option(
            name=name, value=value, label=label, selected=selected,
            index=index, subindex=subindex, attrs=attrs)


class ImageChoiceWidget(RadioSelect):
    option_template_name = 'hero/image_option.html'
    option_inherits_attrs = True
    image_url_base = FEATURED_IMAGE_URL

    def create_option(self, name, value, label, selected, index,
                      subindex=None, attrs=None):
        attrs['image_url'] = f'{self.image_url_base}{value}'
        return super().create_option(
            name=name, value=value, label=label, selected=selected,
            index=index, subindex=subindex, attrs=attrs)


class IconChoiceWidget(ImageChoiceWidget):
    image_url_base = MODULE_ICON_URL


class DirImageChoices:
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        self.os_iter = os.scandir(self.path)
        return self

    def __next__(self):
        entry = self.os_iter.__next__()
        return (entry.name, entry.name)


class WidgetCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.widget = kwargs.pop('widget', None)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'widget': self.widget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class PrimaryHero(ModelBase):
    image = WidgetCharField(
        choices=DirImageChoices(path=FEATURED_IMAGE_PATH),
        max_length=255, widget=ImageChoiceWidget)
    gradient_color = WidgetCharField(
        choices=GRADIENT_CHOICES, max_length=7, widget=GradientChoiceWidget)
    enabled = models.BooleanField(db_index=True, null=False, default=False,)
    disco_addon = models.OneToOneField(
        DiscoveryItem, on_delete=models.CASCADE, null=False)
    is_external = models.BooleanField(null=False, default=False)

    def __str__(self):
        return str(self.disco_addon)

    @property
    def image_url(self):
        return f'{FEATURED_IMAGE_URL}{self.image}'

    @property
    def gradient(self):
        return {'start': GRADIENT_START_COLOR, 'end': self.gradient_color}

    def clean(self):
        super().clean()
        if self.enabled:
            if self.is_external and not self.disco_addon.addon.homepage:
                raise ValidationError(
                    'External primary shelves need a homepage defined in '
                    'addon details.')
            elif not self.is_external:
                recommended = (self.disco_addon.recommended_status ==
                               self.disco_addon.RECOMMENDED)
                if not recommended:
                    raise ValidationError(
                        'Only recommended add-ons can be enabled for '
                        'non-external primary shelves.')
        else:
            if list(PrimaryHero.objects.filter(enabled=True)) == [self]:
                raise ValidationError(
                    'You can\'t disable the only enabled primary shelf.')


class CTACheckMixin():
    def clean(self):
        super().clean()
        both_or_neither = not (bool(self.cta_text) ^ bool(self.cta_url))
        if getattr(self, 'enabled', True) and not both_or_neither:
            raise ValidationError(
                'Both the call to action URL and text must be defined, or '
                'neither, for enabled shelves.')


class SecondaryHero(CTACheckMixin, ModelBase):
    headline = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=100, blank=False)
    cta_url = models.CharField(max_length=255, blank=True)
    cta_text = models.CharField(max_length=20, blank=True)
    enabled = models.BooleanField(db_index=True, null=False, default=False)

    def __str__(self):
        return str(self.headline)

    def clean(self):
        super().clean()
        if not self.enabled:
            if list(SecondaryHero.objects.filter(enabled=True)) == [self]:
                raise ValidationError(
                    'You can\'t disable the only enabled secondary shelf.')


class SecondaryHeroModule(CTACheckMixin, ModelBase):
    icon = WidgetCharField(
        choices=DirImageChoices(path=MODULE_ICON_PATH),
        max_length=255, widget=IconChoiceWidget)
    description = models.CharField(max_length=50, blank=False)
    cta_url = models.CharField(max_length=255, blank=True)
    cta_text = models.CharField(max_length=20, blank=True)
    shelf = models.ForeignKey(
        SecondaryHero, on_delete=models.CASCADE,
        related_name='modules'
    )

    def __str__(self):
        return str(self.description)

    @property
    def icon_url(self):
        return f'{MODULE_ICON_URL}{self.icon}'
