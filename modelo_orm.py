from peewee import SqliteDatabase, fn, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField

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
    nombre = CharField(unique=True)
    class Meta:
        db_table = "comunas"

class Barrio(BaseModel):
    nombre = CharField()
    comuna = ForeignKeyField(Comuna, backref='barrios')
    class Meta:
        db_table = "barrios"
        indexes = ((("nombre", "comuna"), True),) # Index para asegurar unicidad de nombre por comuna

class Contratista(BaseModel):
    nombre_empresa = CharField()
    cuit_contratista = CharField() 
    nro_contratacion = IntegerField() 
    expediente_numero = CharField(max_length=512, null=True) 
    class Meta:
        db_table = "contratistas"

class Direccion(BaseModel):
    ubicacion = CharField()
    barrio = ForeignKeyField(Barrio, backref='direcciones')  
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
    fecha_inicio = DateField(null=True)
    fecha_fin_inicial = DateField(null=True)
    plazo_meses = IntegerField()     
    porcentaje_avance = FloatField()    
    licitacion_anio = IntegerField()
    imagen_1 = CharField(max_length=512, null=True)
    mano_obra = IntegerField()
    destacada = BooleanField(default=False)                                 #Se agrega la columna destacda que es necesaria para el punto 11
    financiamiento = CharField(max_length=512, null=True)                   #Se agrega la columna financiamiento que es necesaria para el punto 11

    #Métodos para validar 
    def validate(self):
        if self.plazo_meses < 0:
            raise ValueError("El plazo en meses no puede ser negativo.")
        if not (0 <= self.porcentaje_avance <= 100):
            raise ValueError("El porcentaje de avance debe estar entre 0 y 100.")
        if self.monto_contrato < 0:
            raise ValueError("El monto del contrato no puede ser negativo.")
        if self.mano_obra < 0:
            raise ValueError("La mano de obra no puede ser negativa.")
        if not self.nombre or not self.descripcion:
            raise ValueError("El nombre y la descripción no pueden estar vacíos.")

    def save(self, *args, **kwargs):
        self.validate()
        return super().save(*args, **kwargs)

    def nuevo_proyecto(self):
        ...

    def iniciar_contratacion(self):
        ...

    def adjudicar_obra(self):
        ...

    def iniciar_obra(self):
        ...

    def actualizar_porcentaje_avance(self):
        ...

    def incrementar_plazo(self, meses_adicionales):
        self.plazo_meses += meses_adicionales

    def incrementar_mano_obra(self, cantidad_adicional):
        self.mano_obra += cantidad_adicional

    def finalizar_obra(self):
        ...

    def rescindir_obra(self):
        ...

#obra = Obra.get(Obra.id == 1)  # Obtener una obra existente
#obra.incrementar_plazo(3)      # Añadir 3 meses al plazo
#obra.incrementar_mano_obra(5)  # Añadir 5 trabajadores
#obra.save()  # Guardar cambios en la base de datos



