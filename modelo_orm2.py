from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField

db = SqliteDatabase('observatorio-obras-urbanas.db')


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

class Barrio(BaseModel):
    nombre = CharField()
    comuna = ForeignKeyField(Comuna, backref='comunas')

    class Meta:
        db_table = "barrios"

class Comuna(BaseModel):
    nombre = CharField()

    class Meta:
        db_table = "comunas"

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
    etapa = ForeignKeyField(Etapa, backref='obras')
    tipo = ForeignKeyField(TipoObra, backref='obras')
    contratacion_tipo = ForeignKeyField(ContratacionTipo, backref='obras')
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras') 
    direccion = ForeignKeyField(Direccion, backref='obras')

    nombre = CharField()
    descripcion = TextField()
    monto_contrato = FloatField()
    fecha_inicio = DateField()
    porcentaje_avance = FloatField()
    fecha_fin_inicial = DateField() 
    plazo_meses = IntegerField() 
    licitacion_oferta_empresa = ForeignKeyField(Contratista, backref='obras')
    licitacion_anio = IntegerField()
    imagen_1 = CharField(max_length=512, null=True)
    mano__obra = IntegerField()


    def nuevo_proyecto(self):
        ...
        

    def iniciar_contratacion(self):
        etapa_contratacion, _ = Etapa.get_or_create(nombre="Contratación")
        self.etapa = etapa_contratacion
        self.save()
        print(f"La obra '{self.nombre}' está en etapa: Contratación (tipo: {self.contratacion_tipo.nombre})")

    def adjudicar_obra(self, contratista, nro_expediente):
        self.licitacion_oferta_empresa = contratista
        self.licitacion_oferta_empresa.expediente_numero = nro_expediente
        self.licitacion_oferta_empresa.save()
        etapa_adjudicada, _ = Etapa.get_or_create(nombre="Adjudicada")
        self.etapa, _ = etapa_adjudicada
        self.save()
        print(f"La obra '{self.nombre}' ha sido adjudicada a {contratista.nombre_empresa} con expediente {nro_expediente}.")
        

    def iniciar_obra(self):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin_inicial = fecha_fin_inicial
        self.mano__obra = mano_obra
        etapa_inicio = Etapa.get_or_create(nombre="En Ejecución")
        self.etapa = etapa_inicio
        self.save()
        print(f"La obra '{self.nombre}' ha iniciado con fecha {self.fecha_inicio}.")


    def actualizar_porcentaje_avance(self):
        self.porcentaje_avance = porcentaje_avance
        self.save()
        print(f"El porcentaje de avance de la obra '{self.nombre}' ha sido actualizado a {self.porcentaje_avance}%.")

    def incrementar_plazo(self):
        self.plazo_meses += meses_extra
        self.save()
        print(f"El plazo de la obra '{self.nombre}' ha sido incrementado a {self.plazo_meses} meses.")

    def incrementar_mano_obra(self):
        self.mano__obra += cantidad
        self.save()
        print(f"La mano de obra de la obra '{self.nombre}' ha sido incrementada a {self.mano__obra}.")
        
    def finalizar_obra(self):
        etapa_finalizada, _ = Etapa.get_or_create(nombre="Finalizada")
        self.etapa = etapa_finalizada
        self.porcentaje_avance = 100
        self.save()
        print(f"La obra '{self.nombre}' ha sido finalizada.")

    def rescindir_obra(self):
        etapa_rescindida, _ = Etapa.get_or_create(nombre="Rescindida")
        self.etapa = etapa_rescindida
        self.porcentaje_avance = 0
        self.save()
        print(f"La obra '{self.nombre}' ha sido rescindida.")





