# Generated by Django 2.1.7 on 2019-04-06 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestPoints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=10, verbose_name='鼓风机型号')),
                ('working_condition', models.IntegerField(default=0, verbose_name='工况')),
                ('working_position', models.IntegerField(default=0, verbose_name='工况点')),
                ('flow_coef', models.FloatField(verbose_name='流量系数')),
                ('pressure_coef', models.FloatField(verbose_name='压力系数')),
                ('efficiency', models.FloatField(verbose_name='效率')),
                ('flow_factor', models.FloatField(verbose_name='流量因子')),
                ('pressure_factor', models.FloatField(verbose_name='压力因子')),
                ('efficiency_factor', models.FloatField(verbose_name='效率因子')),
            ],
        ),
        migrations.CreateModel(
            name='Turbo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=10, verbose_name='鼓风机型号')),
                ('cut_back', models.FloatField(verbose_name='cut back')),
                ('diameter', models.FloatField(verbose_name='直径')),
                ('fix_loss_one', models.FloatField(verbose_name='fix loss one')),
                ('fix_loss_two', models.FloatField(verbose_name='fix loss two')),
                ('var_loss', models.FloatField(verbose_name='var loss')),
                ('size_correction', models.FloatField(verbose_name='size correction')),
            ],
        ),
    ]
