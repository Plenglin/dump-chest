from django.core.exceptions import ValidationError
from django.db import models
from jsonfield import JSONField

CONTAINER_TYPE_CHOICES = {
    'BX': 'box',
    'SL': 'shelf',
    'DR': 'drawer',
    'RM': 'room',
    'SR': 'surface',
    'WL': 'wall',
    'OT': 'other'
}


class Node(models.Model):
    name = models.CharField(
        max_length=100
    )
    description = models.TextField('description', blank=True)
    image = models.ImageField(upload_to='container/', null=True)
    location = models.TextField('location', blank=True)

    parent = models.ForeignKey('Container', on_delete=models.SET_NULL, blank=True, null=True)
    container_metadata = JSONField(default={})

    class Meta:
        abstract = True


class Container(Node):
    location = models.TextField('location', blank=True)
    container_type = models.CharField(
        max_length=2,
        choices=CONTAINER_TYPE_CHOICES.items(),
        blank=False,
        default='BX'
    )

    @property
    def link(self):
        return f'/container/{self.id}'

    @property
    def type_verbose(self):
        return CONTAINER_TYPE_CHOICES[self.container_type]

    def __str__(self):
        if self.location != '':
            return f'{self.name} at {self.location}'
        return self.name

    def __repr__(self):
        return f'Container#{self.id}({self.name})'

    def clean(self):
        # Ensure there are no circular parents
        node = self
        while node.parent is not None:
            node = node.parent
            if node == self:
                raise ValidationError(
                    'Containers cannot be circularly contained within themselves... with current technology.')


class ItemTag(models.Model):
    name = models.CharField(verbose_name='name', max_length=30, primary_key=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super().save(*args, **kwargs)

    @property
    def link(self):
        return f'/tag/{self.name}'

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'ItemTag({self.name})'


class Item(Node):
    quantity = models.IntegerField('quantity', default=0)
    alert_quantity = models.IntegerField('alert quantity', default=0)
    source = models.CharField(verbose_name='source', max_length=200, blank=True, default='')
    source_url = models.URLField(verbose_name='source URL', blank=True, null=True)
    tags = models.ManyToManyField(ItemTag)

    @property
    def link(self):
        return f'/item/{self.id}'

    def __str__(self):
        return f'{self.name} × {self.quantity}'

    def __repr__(self):
        return f'Item#{self.id}({self.name})'
