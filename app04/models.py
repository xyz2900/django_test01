from django.db import models


class DatForex(models.Model):
   """為替データ"""

   class Meta:
      db_table = 'dat_forex'

   no   = models.CharField(verbose_name='シンボル', max_length=10)
   dtime = models.DateField(verbose_name='日時')
   open = models.FloatField(verbose_name='始値')
   high = models.FloatField(verbose_name='高値')
   low  = models.FloatField(verbose_name='安値')
   close = models.FloatField(verbose_name='終値')
   volume = models.IntegerField(verbose_name='出来高')

   created_at = models.DateTimeField(verbose_name='登録日時', auto_now_add=True)
   updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

   def __str__(self):
      return self.no + ' ' + self.date


