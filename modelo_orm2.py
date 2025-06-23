from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField



db = SqliteDatabase('obras-urbanas.db')


class BaseModel(Model):

    class Meta:
        database = db

class Entorno(BaseModel):

    nombre = CharField(unique=True, null=True)

    class Meta:
        db_table = "entornos"

class Etapa(BaseModel):

    nombre = CharField(unique=True, null=True)

    class Meta:
        db_table = "etapas"


class TipoObra(BaseModel):

    nombre = CharField(unique=True, null=True)

    class Meta:
        db_table = "tipo_obras"

class ContratacionTipo(BaseModel):

    nombre = CharField(unique=True, null=True)

    class Meta:
        db_table = "contratacion_tipo"

class AreaResponsable(BaseModel):

    nombre = CharField(unique=True, null=True)

    class Meta:
        db_table = "area_responsable"


class Comuna(BaseModel):

    nombre = CharField(unique=True, null=True)

    class Meta:
        db_table = "comunas"


class Barrio(BaseModel):

    nombre = CharField(unique=True, null=True)
    comuna = ForeignKeyField(Comuna, backref='comunasa', null=True)

    class Meta:
        db_table = "barrios"


class Contratista(BaseModel):

    nombre_empresa = CharField(null=True)
    cuit_contratista = CharField(null=True)
    nro_contratacion = CharField(null=True)
    expediente_numero = CharField(max_length=512, null=True)

    class Meta:
        db_table = "contratistas"


class Direccion(BaseModel):

    ubicacion = CharField(null=True)
    barrio = ForeignKeyField(Barrio, backref='barrios', null=True)
    lat = FloatField(null=True)
    lng = FloatField(null=True)

    class Meta:
        db_table = "direccion"

class Obra(BaseModel):

    entorno = ForeignKeyField(Entorno, backref='obras', null=True)
    etapa = ForeignKeyField(Etapa, backref='obras', null=True)
    tipo = ForeignKeyField(TipoObra, backref='obras', null=True)
    contratacion_tipo = ForeignKeyField(ContratacionTipo, backref='obras', null=True)
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras', null=True)
    direccion = ForeignKeyField(Direccion, backref='obras', null=True)
    licitacion_oferta_empresa = ForeignKeyField(Contratista, backref='obras', null=True)

    nombre = CharField(null=True)
    descripcion = TextField(null=True)
    monto_contrato = FloatField(null=True)
    fecha_inicio = DateField(null=True)
    fecha_fin_inicial = DateField(null=True)
    plazo_meses = IntegerField()
    porcentaje_avance = FloatField()
    licitacion_anio = IntegerField(null=True)
    imagen_1 = CharField(max_length=512, null=True)
    mano_obra = IntegerField(null=True)
    destacada = BooleanField(default=False, null=True)
    financiamiento = CharField(max_length=512, null=True)

    def nuevo_proyecto(self):
        ...
        try:
            proyecto = Etapa.get_or_create(nombre="Proyecto")
        except Exception as e:
            print(f'[ERROR] - {e}')

        if proyecto:
            print('Proyecto existente')
            return

        proyecto.save()
        print('El proyecto ha sido creado')
        return

        
    def iniciar_contratacion(self):
        ...
    def adjudicar_obra(self):
        ...
    def iniciar_obra(self):
        ...
    def actualizar_porcentaje_avance(self):
        ...
    def incrementar_plazo(self):
        ...
    def incrementar_mano_obra(self):
        ...
    def finalizar_obra(self):
        ...
    def rescindir_obra(self):
        ...
