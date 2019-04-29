# Generated by Django 2.1.4 on 2019-04-29 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selectedturbo', '0002_auto_20190406_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testpoints',
            name='category',
            field=models.CharField(choices=[('GL1', 'GL1'), ('GL2', 'GL2'), ('GL3', 'GL3'), ('GL5', 'GL5'), ('GL8', 'GL8'), ('GL10', 'GL10'), ('GL15', 'GL15'), ('GL20', 'GL20'), ('GL30', 'GL30'), ('GL50', 'GL50')], default='GL3', max_length=10, verbose_name='鼓风机型号'),
        ),
        migrations.AlterField(
            model_name='turbo',
            name='category',
            field=models.CharField(choices=[('GL1', 'GL1'), ('GL2', 'GL2'), ('GL3', 'GL3'), ('GL5', 'GL5'), ('GL8', 'GL8'), ('GL10', 'GL10'), ('GL15', 'GL15'), ('GL20', 'GL20'), ('GL30', 'GL30'), ('GL50', 'GL50')], default='GL1', max_length=10, verbose_name='鼓风机型号'),
        ),
    ]