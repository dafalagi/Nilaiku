# Generated by Django 4.2.4 on 2023-09-01 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gradedetail',
            name='student_id',
            field=models.CharField(default='test-student-id', max_length=255),
            preserve_default=False,
        ),
    ]