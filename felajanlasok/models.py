from django.db import models


class Cel(models.Model):
    az = models.IntegerField(primary_key=True, verbose_name="Azonosító")
    megnevezes = models.CharField(max_length=255, verbose_name="Megnevezés")
    civil = models.BooleanField(verbose_name="Civil összefogás")

    def __str__(self):
        return f"{self.az}. {self.megnevezes}"

    class Meta:
        verbose_name = "Cél"
        verbose_name_plural = "Célok"


class Felajanlas(models.Model):
    az = models.AutoField(primary_key=True, verbose_name="Azonosító")
    datum = models.DateField(verbose_name="Dátum")
    celaz = models.ForeignKey(
        Cel, on_delete=models.CASCADE, verbose_name="Cél", related_name="felajanlasok")
    szamlaaz = models.IntegerField(verbose_name="Számla azonosító")
    osszeg = models.IntegerField(verbose_name="Összeg")

    def __str__(self):
        return f"{self.az}. számú felajánlás ({self.datum}): {self.osszeg} Ft"

    class Meta:
        verbose_name = "Felajánlás"
        verbose_name_plural = "Felajánlások"
        ordering = ['datum', 'szamlaaz']
