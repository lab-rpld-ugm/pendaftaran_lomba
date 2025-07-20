from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateTimeField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class CompetitionEditForm(FlaskForm):
    nama_kompetisi = StringField('Nama Kompetisi', validators=[DataRequired(), Length(max=100)])
    deskripsi = TextAreaField('Deskripsi', validators=[Optional()])
    kategori = SelectField('Kategori', choices=[('individual', 'Individu'), ('team', 'Tim')], validators=[DataRequired()])
    jenis = SelectField('Jenis', choices=[('academic', 'Akademik'), ('creative', 'Kreatif'), ('performance', 'Performa'), ('basketball', 'Basket'), ('esports', 'E-Sports')], validators=[DataRequired()])
    harga_early_bird = IntegerField('Harga Early Bird', validators=[DataRequired(), NumberRange(min=0)])
    harga_reguler = IntegerField('Harga Reguler', validators=[DataRequired(), NumberRange(min=0)])
    tanggal_mulai_early_bird = DateTimeField('Mulai Early Bird', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    tanggal_akhir_early_bird = DateTimeField('Akhir Early Bird', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    deadline_registrasi = DateTimeField('Deadline Registrasi', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    tanggal_kompetisi = DateTimeField('Tanggal Kompetisi', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    min_kelas = IntegerField('Kelas Minimum', validators=[DataRequired(), NumberRange(min=1)])
    max_kelas = IntegerField('Kelas Maksimum', validators=[DataRequired(), NumberRange(min=1)])
    min_anggota = IntegerField('Min Anggota Tim', validators=[Optional(), NumberRange(min=1)])
    max_anggota = IntegerField('Max Anggota Tim', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Simpan Perubahan') 