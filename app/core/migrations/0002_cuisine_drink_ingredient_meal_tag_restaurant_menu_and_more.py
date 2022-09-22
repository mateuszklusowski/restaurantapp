# Generated by Django 4.0.7 on 2022-09-21 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Drink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('description', models.CharField(max_length=255)),
                ('ingredients', models.ManyToManyField(to='core.ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('post_code', models.CharField(max_length=7)),
                ('phone', models.CharField(max_length=17)),
                ('delivery_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('cuisine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cuisine')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drinks', models.ManyToManyField(to='core.drink')),
                ('meals', models.ManyToManyField(to='core.meal')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.restaurant')),
            ],
        ),
        migrations.AddField(
            model_name='meal',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tag'),
        ),
        migrations.AddField(
            model_name='drink',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tag'),
        ),
    ]