from peewee import (
    SqliteDatabase, Model, CharField, DateField, ForeignKeyField, IntegerField,
    TextField, BooleanField, FloatField
)
from datetime import date

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
    nombre = CharField(unique=True)
    class Meta:
        db_table = "contratacion_tipo"

class AreaResponsable(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "area_responsable"

class Comuna(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "comunas"

class Barrio(BaseModel):
    nombre = CharField(unique=True)
    comuna = ForeignKeyField(Comuna, backref='barrios')
    class Meta:
        db_table = "barrios"

class Empresa(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "empresas"

class FuenteFinanciamiento(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "fuentes_financiamiento"

class Direccion(BaseModel):
    ubicacion = CharField()
    barrio = ForeignKeyField(Barrio, backref='direcciones')
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    class Meta:
        db_table = "direccion"

class Obra(BaseModel):
    etapa = ForeignKeyField(Etapa, backref='obras')
    tipo = ForeignKeyField(TipoObra, backref='obras')
    tipo_contratacion = ForeignKeyField(ContratacionTipo, backref='obras')
    empresa = ForeignKeyField(Empresa, backref='obras', null=True)
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras') 
    barrio = ForeignKeyField(Barrio, backref='obras')  
    nombre = CharField()
    descripcion = TextField()
    monto_contrato = FloatField()
    licitacion_anio = IntegerField()
    fecha_inicio = DateField(null=True)
    porcentaje_avance = FloatField(default=0)
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    fecha_fin_inicial = DateField(null=True)
    plazo_meses = IntegerField()
    imagen_1 = CharField(max_length=512, null=True)
    imagen_2 = CharField(max_length=512, null=True) 
    imagen_3 = CharField(max_length=512, null=True) 
    imagen_4 = CharField(max_length=512, null=True) 
    nro_contratacion = IntegerField(null=True) 
    cuit_contratista = CharField(null=True) 
    beneficiarios = CharField(null=True) 
    mano_obra = IntegerField(default=0) 
    compromiso = BooleanField(default=False) 
    destacada =  BooleanField(default=False)
    link_interno = CharField(max_length=512, null=True) 
    pliego_descarga = CharField(max_length=512, null=True)
    expediente_numero = CharField(max_length=512, null=True) 
    finalizada = BooleanField(default=False)
    rescindida = BooleanField(default=False)
    fuente_financiamiento = ForeignKeyField(FuenteFinanciamiento, backref='obras', null=True)

    class Meta:
        db_table = "obras"

    def validate(self):
        if self.plazo_meses < 0:
            raise ValueError("El plazo en meses no puede ser negativo.")
        if not (0 <= self.porcentaje_avance <= 100):
            raise ValueError("El porcentaje de avance debe estar entre 0 y 100.")
        if self.monto_contrato < 0:
            raise ValueError("El monto del contrato no puede ser negativo.")
        if self.mano_obra is not None and self.mano_obra < 0:
            raise ValueError("La mano de obra no puede ser negativa.")
        if not self.nombre or not self.descripcion:
            raise ValueError("El nombre y la descripción no pueden estar vacíos.")

    def save(self, *args, **kwargs):
        self.validate()
        return super().save(*args, **kwargs)

    def nuevo_proyecto(self):
        self.etapa = Etapa.get_or_create(nombre="Proyecto")[0]
        self.porcentaje_avance = 0
        self.save()
        
    def iniciar_contratacion(self, tipo_contratacion, nro_contratacion):
        self.etapa = Etapa.get_or_create(nombre="Licitación")[0]
        self.tipo_contratacion = tipo_contratacion
        self.nro_contratacion = nro_contratacion
        self.save()

    def adjudicar_obra(self, empresa, nro_expediente):
        self.empresa = empresa
        self.expediente_numero = str(nro_expediente)
        self.etapa = Etapa.get_or_create(nombre="Adjudicada")[0]
        self.save()

    def iniciar_obra(self, destacada, fecha_inicio, fecha_fin_inicial, fuente_financiamiento, mano_obra):
        self.destacada = destacada 
        self.fecha_inicio = fecha_inicio
        self.fecha_fin_inicial = fecha_fin_inicial
        self.fuente_financiamiento = fuente_financiamiento
        self.mano_obra = mano_obra
        self.etapa = Etapa.get_or_create(nombre="En Ejecucion")[0]
        self.save()

    def actualizar_porcentaje_avance(self, valor):
        if 0 <= valor <= 100:
            self.porcentaje_avance = valor
            self.save()
        else:
            raise ValueError("El porcentaje de avance debe estar entre 0 y 100.")

    def incrementar_plazo(self, cantidad):
        self.plazo_meses += cantidad
        self.save()

    def incrementar_mano_obra(self, cantidad):
        self.mano_obra += cantidad
        self.save()

    def finalizar_obra(self):
        self.etapa = Etapa.get_or_create(nombre="Finalizada")[0]
        self.porcentaje_avance = 100
        self.finalizada = True
        self.save()

    def rescindir_obra(self):
        self.rescindida = True
        self.etapa = Etapa.get_or_create(nombre="Rescindida")[0]
        self.save()

        etapa, _ = Etapa.get_or_create(nombre="Proyecto")
        tipo, _ = TipoObra.get_or_create(nombre="Vial")
        tipo_contratacion, _ = ContratacionTipo.get_or_create(nombre="Licitación Pública")
        empresa, _ = Empresa.get_or_create(nombre="Empresa Test")
        area, _ = AreaResponsable.get_or_create(nombre="Infraestructura")
        barrio, _ = Barrio.get_or_create(nombre="Centro", comuna=1)  # Ajusta comuna si es FK real
        fuente, _ = FuenteFinanciamiento.get_or_create(nombre="Nacional")

# 3. Crear una obra nueva (en estado "Proyecto")
        obra = Obra.create(
        etapa=etapa,
        tipo=tipo,
        tipo_contratacion=tipo_contratacion,
        empresa=empresa,
        area_responsable=area,
        barrio=barrio,
        nombre="Obra de Prueba",
        descripcion="Una obra para testear el flujo.",
        monto_contrato=1000000,
        licitacion_anio=2025,
        porcentaje_avance=0,
        plazo_meses=18,
        mano_obra=0,
        destacada=False,
        fecha_inicio=None,
        fecha_fin_inicial=None,
        fuente_financiamiento=fuente
        )

        print("Obra creada:", obra)

# 4. Probar los métodos de instancia en orden lógico

obra.nuevo_proyecto()
print("Etapa tras nuevo_proyecto:", obra.etapa.nombre, obra.porcentaje_avance)

obra.iniciar_contratacion(tipo_contratacion, 123)
print("Etapa tras iniciar_contratacion:", obra.etapa.nombre, obra.tipo_contratacion.nombre, obra.nro_contratacion)

obra.adjudicar_obra(empresa, "EXP-0001")
print("Etapa tras adjudicar_obra:", obra.etapa.nombre, obra.empresa.nombre, obra.expediente_numero)

obra.iniciar_obra(
    destacada=True,
    fecha_inicio=date.today(),
    fecha_fin_inicial=date(2026, 7, 1),
    fuente_financiamiento=fuente,
    mano_obra=10
)
print("Etapa tras iniciar_obra:", obra.etapa.nombre, obra.destacada, obra.fecha_inicio, obra.fecha_fin_inicial, obra.fuente_financiamiento.nombre, obra.mano_obra)

obra.actualizar_porcentaje_avance(45)
print("Porcentaje avance tras actualizar:", obra.porcentaje_avance)

obra.incrementar_plazo(2)
print("Plazo meses tras incrementar:", obra.plazo_meses)

obra.incrementar_mano_obra(5)
print("Mano obra tras incrementar:", obra.mano_obra)

obra.finalizar_obra()
print("Etapa tras finalizar_obra:", obra.etapa.nombre, obra.porcentaje_avance, obra.finalizada)







