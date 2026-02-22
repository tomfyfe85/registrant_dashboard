
import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('registrants', '0003_rename_date_statuschange_date_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='registrant',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registrants.company'),
        ),
    ]
