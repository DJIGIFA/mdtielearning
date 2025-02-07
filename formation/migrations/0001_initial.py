# Generated by Django 4.2.8 on 2024-04-12 17:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='')),
                ('slug', models.SlugField()),
            ],
        ),
        migrations.CreateModel(
            name='Chapitre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('progression', models.FloatField(default=0)),
                ('terminer', models.BooleanField(default=False)),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Examen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=250)),
                ('reponse', models.CharField(max_length=250)),
                ('duree', models.IntegerField()),
                ('point', models.IntegerField()),
                ('correct', models.BooleanField(default=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Formation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('miniature', models.ImageField(upload_to='')),
                ('prix', models.FloatField()),
                ('slug', models.SlugField()),
                ('nombre_heur', models.FloatField()),
                ('description', models.TextField(blank=True, null=True)),
                ('prerequis', models.TextField(blank=True, null=True)),
                ('profile_destine', models.TextField(blank=True, null=True)),
                ('objectif_du_cours', models.TextField(blank=True, null=True)),
                ('publier', models.BooleanField(default=False)),
                ('moderer', models.BooleanField(default=False)),
                ('ajout_terminer', models.BooleanField(default=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('date_de_publication', models.DateField(auto_now_add=True)),
                ('dernier_mise_a_jour', models.DateField(auto_now=True)),
                ('instructeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Qcm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=2500)),
                ('description', models.TextField()),
                ('duree', models.IntegerField()),
                ('date', models.DateField(auto_now_add=True)),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.formation')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('point', models.IntegerField()),
                ('qcm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.qcm')),
            ],
        ),
        migrations.CreateModel(
            name='Reponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reponse', models.TextField()),
                ('correcte', models.BooleanField()),
                ('date', models.DateField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.question')),
            ],
        ),
        migrations.CreateModel(
            name='SousCategorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='')),
                ('slug', models.SlugField()),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.categorie')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200)),
                ('duree', models.IntegerField()),
                ('video', models.FileField(upload_to='')),
                ('ordre', models.IntegerField()),
                ('chapitre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.chapitre')),
            ],
        ),
        migrations.CreateModel(
            name='VideoVue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('cour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.cour')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.video')),
            ],
        ),
        migrations.CreateModel(
            name='Temoignage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('vue', models.BooleanField(default=False)),
                ('moderer', models.BooleanField(default=False)),
                ('actif', models.BooleanField(default=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.formation')),
            ],
        ),
        migrations.CreateModel(
            name='Suive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('terminer', models.BooleanField(default=False)),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('souscategorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.souscategorie')),
            ],
        ),
        migrations.CreateModel(
            name='SeanceTravail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=512)),
                ('lien_de_la_reunion', models.URLField()),
                ('confirmer_par_apprenant', models.BooleanField(default=False)),
                ('confirmer_par_instructeur', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('date_de_la_reunion', models.DateField()),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.formation')),
            ],
        ),
        migrations.CreateModel(
            name='ResultatExamen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('examen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.examen')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.question')),
                ('response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.reponse')),
            ],
        ),
        migrations.CreateModel(
            name='Participer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField(blank=True, null=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('qcm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.qcm')),
            ],
        ),
        migrations.CreateModel(
            name='PaiementFormation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=512, unique=True)),
                ('payer', models.BooleanField(default=False)),
                ('moyen_paiement', models.CharField(choices=[('Orange Money', 'Orange Money'), ('Moov Money', 'Moov Money'), ('Sama Money', 'Sama Money'), ('Carte Visa', 'Carte Visa')], max_length=50)),
                ('date_soumission', models.DateTimeField(auto_now_add=True)),
                ('date_validation', models.DateTimeField(null=True)),
                ('montant', models.FloatField()),
                ('numero', models.CharField(max_length=30, null=True)),
                ('strip_link', models.URLField(null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.formation')),
            ],
        ),
        migrations.AddField(
            model_name='formation',
            name='sous_categorie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.souscategorie'),
        ),
        migrations.AddField(
            model_name='examen',
            name='qcm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.qcm'),
        ),
        migrations.CreateModel(
            name='Discution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('envoyer_par_apprenant', models.BooleanField()),
                ('date', models.DateField(auto_now_add=True)),
                ('lue', models.BooleanField(default=False)),
                ('apprenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('formation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.formation')),
            ],
        ),
        migrations.AddField(
            model_name='cour',
            name='formation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.formation'),
        ),
        migrations.AddField(
            model_name='chapitre',
            name='formation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='formation.formation'),
        ),
    ]
