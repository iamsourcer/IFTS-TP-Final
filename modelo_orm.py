from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField

db = SqliteDatabase('obras-urbanas.db')                                     #Se cambia el nombre de la base de datos según como se indica en la documentación del proyecto


class BaseModel(Model):
    class Meta:
        database = db

class Entorno(BaseModel):
    nombre = CharField(unique=True)

    class Meta:
        db_table = "entornos"

class Etapa(BaseModel):
    nombre = CharField(unique=True)

    class Meta:
        db_table = "etapas"

class TipoObra(BaseModel):
    nombre = CharField(unique=True)

    class Meta:
        db_table = "tipo_obras"

class ContratacionTipo(BaseModel):
    nombre = CharField()

    class Meta:
        db_table = "contratacion_tipo"

class AreaResponsable(BaseModel):
    nombre = CharField()

    class Meta:
        db_table = "area_responsable"

class Comuna(BaseModel):
    nombre = CharField()

    class Meta:
        db_table = "comunas"

class Barrio(BaseModel):
    nombre = CharField()
    comuna = ForeignKeyField(Comuna, backref='comunas')

    class Meta:
        db_table = "barrios"

class Contratista(BaseModel):
    nombre_empresa = CharField()
    cuit_contratista = CharField() 
    nro_contratacion = IntegerField() 
    expediente_numero = CharField(max_length=512, null=True) 
    
    class Meta:
        db_table = "contratistas"

class Direccion(BaseModel):
    ubicacion = CharField()
    barrio = ForeignKeyField(Barrio, backref='barrios')  
    lat = FloatField(null=True)
    lng = FloatField(null=True)

    class Meta:
        db_table = "direccion"

class Obra(BaseModel):
    entorno = ForeignKeyField(Entorno, backref='obras')                     #agregado entorno
    etapa = ForeignKeyField(Etapa, backref='obras')
    tipo = ForeignKeyField(TipoObra, backref='obras')
    contratacion_tipo = ForeignKeyField(ContratacionTipo, backref='obras')
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras') 
    direccion = ForeignKeyField(Direccion, backref='obras')
    licitacion_oferta_empresa = ForeignKeyField(Contratista, backref='obras')

    nombre = CharField()
    descripcion = TextField()
    monto_contrato = FloatField()
    fecha_inicio = DateField()
    fecha_fin_inicial = DateField()
    plazo_meses = IntegerField()     
    porcentaje_avance = FloatField()    
    licitacion_anio = IntegerField()
    imagen_1 = CharField(max_length=512, null=True)
    mano_obra = IntegerField()
    destacada = BooleanField(default=False)                                 #Se agrega la columna destacda que es necesaria para el punto 11
    financiamiento = CharField(max_length=512, null=True)                   #Se agrega la columna financiamiento que es necesaria para el punto 11


    """ def nuevo_proyecto(self):
        try:
            estapa_proyecto, created = Etapa.get_or_create(nombre_etapa = "Proyecto")
            if (created):
                print("Etapa 'Proyecto' creada exitosamente en la DB.")
            self.etapa = estapa_proyecto
            self.save()
            print(f"Obra '{self.nombre}': Etapa iniciada como 'Proyecto'.")
            return True
        except Exception as e:
            print(f"[ERROR] - al iniciar nuevo proyecto para obra '{self.nombre}': {e}")
            return False """
        
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





