# Generated by Django 5.2.3 on 2025-06-30 07:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_filter', models.URLField(help_text='URL filter từ trangvangvietnam.com', max_length=1024)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('DONE', 'Done'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Tên công ty')),
                ('phone', models.CharField(blank=True, max_length=100, null=True, verbose_name='Số điện thoại')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Địa chỉ')),
                ('category', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ngành nghề')),
                ('website', models.URLField(blank=True, max_length=500, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businesses', to='trangvang_crawler.crawltask')),
            ],
        ),
    ]
