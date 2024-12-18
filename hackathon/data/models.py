from django.db import models


class AddressModel(models.Model):
    address = models.CharField(max_length=256)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    flats = models.IntegerField()
    entrances = models.IntegerField()
    floors = models.IntegerField(null=True)


class Client(models.Model):
    external_id = models.CharField(max_length=16)
    gender = models.BooleanField(null=True)
    age_min = models.IntegerField()
    age_max = models.IntegerField()
    address = models.ForeignKey(AddressModel, on_delete=models.CASCADE,null=True)
    preferred_category = models.CharField(max_length=300, null=True, blank=True)


class ChannelPackege(models.Model):
    name = models.CharField(max_length=64)


class Channel(models.Model):
    packege = models.ManyToManyField(ChannelPackege, related_name='channels')


class Category(models.Model):
    name = models.CharField(max_length=300)


class TVShow(models.Model):
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    name = models.CharField(max_length=300)
    main_category = models.CharField(max_length=300)
    categories = models.ManyToManyField(Category, related_name='tv_shows')


class Viewing(models.Model):
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    device = models.CharField(max_length=16)
    tv_show = models.ForeignKey(TVShow, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

class SimilarClient(models.Model):
    client = models.ForeignKey(Client, related_name="similar_clients", on_delete=models.CASCADE)
    similar_client = models.ForeignKey(Client, related_name="similar_to", on_delete=models.CASCADE)
    similarity_score = models.FloatField()

    class Meta:
        ordering = ['-similarity_score']