from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField, fn
from datetime import datetime

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
    nro_contratacion = CharField() 
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
        try:
            #busca o crea la nueva etapa "Proyecto"
            nueva_etapa_de_proyecto, created = Etapa.get_or_create(nombre = "Proyecto")
            if created:
                print("Etapa 'Proyecto' creada exitosamente en la DB.")
        except Exception as e:
            print(f"[ERROR] - al crear/buscar la etapa 'Proyecto': {e}")
            return False
        
        #validando que existan los registros en la DB
        try:
            existe_tipo = TipoObra.get_or_none(id=self.tipo.id)
            existe_area = AreaResponsable.get_or_none(id=self.area_responsable.id)
            existe_barrio = Barrio.get_or_none(id=self.direccion.barrio.id)
            if not existe_tipo:
                raise ValueError("El tipo de obra no existe en la base de datos.")
            if not existe_area:
                raise ValueError("El área responsable no existe en la base de datos.")
            if not existe_barrio:
                raise ValueError("El barrio no existe en la base de datos.")
        except Exception as e:
            print(f"[ERROR] - al validar los registros': {e}")
            return False

        #Asigno la etapa y guardo
        try:
            self.etapa = nueva_etapa_de_proyecto
            self.save()
            print(f"Obra '{self.nombre}': Etapa iniciada como 'Proyecto'.")
            return True
        except Exception as e:
            print(f"[ERROR] - al iniciar nuevo proyecto para obra '{self.nombre}': {e}")
            return False
        
    def iniciar_contratacion(self):
        try:
            iniciar_contratacion = input("Ingrese el nombre del tipo de contratación para la obra: ").strip()
            nuevo_tipo_contratacion = ContratacionTipo.get_or_none(nombre=iniciar_contratacion)
            if not nuevo_tipo_contratacion:
                raise ValueError("El tipo de contratación ingresado no existe en la Base de Datos.")
        except Exception as e:
            print(f"[ERROR] - al buscar el Tipo de Contratación': {e}")
            return False
        
        try:
            nuevo_nro_contratacion = input("Ingrese el número de contratación: ").strip()
            if not nuevo_nro_contratacion:
                raise ValueError("El número de contratación no puede estar vacío.")
        except Exception as e:
            print(f"[ERROR] - al ingresar número de contratación': {e}")
            return False
            
        try:
            self.contratacion_tipo = nuevo_tipo_contratacion
            self.licitacion_oferta_empresa.nro_contratacion = nuevo_nro_contratacion
            self.licitacion_oferta_empresa.save()
            self.save()
            print(f"Contratación iniciada para la obra '{self.nombre}' con tipo de contratación: '{nuevo_tipo_contratacion.nombre}' y número de contratación: '{nuevo_nro_contratacion}'.")
            return True
        except Exception as e:
            print(f"[ERROR] - al guardar la contratación para la obra '{self.nombre}': {e}")
            return False

    def adjudicar_obra(self):
        try:
            nuevo_nombre_empresa = input("Ingrese el nombre de la empresa adjudicataria: ").strip()
            nuevo_cuit_contratista = input("Ingrese el CUIT de la empresa adjudicataria: ").strip()
            nueva_empresa = Contratista.get_or_none(nombre_empresa=nuevo_nombre_empresa, cuit_contratista=nuevo_cuit_contratista)
            if not nueva_empresa:
                raise ValueError("La empresa ingresada no existe en la Base de Datos.")
        except Exception as e:
            print(f"[ERROR] - al buscar la empresa adjudicataria': {e}")
            return False
            
        try:
            nuevo_numero_expediente = input("Ingrese el número del expediente: ").strip()
            if not nuevo_numero_expediente:
                raise ValueError("El número del expediente no puede estar vacio.")
            
            nueva_empresa.expediente_numero = nuevo_numero_expediente
            nueva_empresa.save()
            
            self.licitacion_oferta_empresa = nueva_empresa
            self.save()
            print(f"La obra '{self.nombre}' fue adjudicada a la empresa: '{nuevo_nombre_empresa}' (CUIT: {nuevo_cuit_contratista}), con el expediente: '{nuevo_numero_expediente}'. ")
            return True
        except Exception as e:
            print(f"[ERROR] - al adjudicar la obra '{self.nombre}': {e}")
            return False

    def iniciar_obra(self):
        try:
            nueva_destacada = input(f"¿Desea destacar la obra '{self.nombre}'? (s/n): ").strip().lower()
            if nueva_destacada == 's':
                self.destacada = True
            else:
                self.destacada = False

            nueva_fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD): ").strip()
            self.fecha_inicio = datetime.strptime(nueva_fecha_inicio, "%Y-%m-%d").date()

            nueva_fecha_fin_inicial = input("Ingrese la fecha de finalización (YYYY-MM-DD): ").strip()
            self.fecha_fin_inicial = datetime.strptime(nueva_fecha_fin_inicial, "%Y-%m-%d").date()

            nueva_fuente_financiamiento = input("Ingrese la fuente de financiamiento: ")
            existe_nuevo_financiamiento = Obra.select().where(Obra.financiamiento == nueva_fuente_financiamiento).exists()
            if not existe_nuevo_financiamiento:
                raise ValueError("La fuente de financiamiento ingresado no existe en la Base de Datos.")
            self.financiamiento = nueva_fuente_financiamiento

            mano_de_obra = int(input("Ingrese la cantidad de mano de obra: ").strip()) 
            if mano_de_obra < 0:
                raise ValueError("La mano de obra ingresada no puede ser negativa.")
            self.mano_obra = mano_de_obra

            self.save()
            print(f"La obra '{self.nombre}' ha sido iniciada correctamente. ")
            return True
        except Exception as e:
            print(f"[ERROR] - al iniciar la obra '{self.nombre}': {e}")
            return False

    def actualizar_porcentaje_avance(self):
        try:
            nuevo_porcentaje_de_avance = float(input(f"Ingrese el nuevo porcentaje de avance para la obra '{self.nombre}' (entre 0 y 100): "))
            if not (0 <= nuevo_porcentaje_de_avance <= 100):
                raise ValueError("El porcentaje de avance debe estar comprendido entre 0 y 100.")
            self.porcentaje_avance = nuevo_porcentaje_de_avance
            self.save()
            print(f"El porcentaje de avance de la obra '{self.nombre}' se ha actualizado a {self.porcentaje_avance}%.")
            return True
        except Exception as e:
            print(f"[ERROR] - al actualizar el porcentaje de avance para la obra '{self.nombre}' : {e}")
            return False

    def incrementar_plazo(self):
        try:
            nuevo_plazo = int(input(f"Ingrese la cantidad de meses a incrementar al plazo para la obra: '{self.nombre}': "))
            if nuevo_plazo < 0:
                raise ValueError("El incremento en el plazo no puede ser negativo.")
            self.plazo_meses += nuevo_plazo
            self.save()
            print(f"El plazo de la obra '{self.nombre}' se incremento en {nuevo_plazo} meses. El nuevo plazo actualizado es: {self.plazo_meses} meses.")
            return True
        except Exception as e:
            print(f"[ERROR] - al incrementar el plazo para la obra '{self.nombre}' : {e}")
            return False

    def incrementar_mano_obra(self):
        try:
            nueva_mano_obra = int(input(f"Ingrese la cantidad de personas a incrementar en la mano de obra de la obra: '{self.nombre}': "))
            if nueva_mano_obra < 0:
                raise ValueError("El incremento en la mano de obra no puede ser negativo.")
            self.mano_obra += nueva_mano_obra
            self.save()
            print(f"La mano de obra para la obra '{self.nombre}' se incremento en {nueva_mano_obra} personas. El nuevo total de mano de obra actualizado es: {self.mano_obra} personas.")
            return True
        except Exception as e:
            print(f"[ERROR] - al incrementar la mano de obra para la obra '{self.nombre}' : {e}")
            return False

    def finalizar_obra(self):
        try:
            nueva_etapa_de_proyecto, created = Etapa.get_or_create(nombre = "Finalizada")
            if created:
                print("Etapa 'Finalizada' creada exitosamente en la DB.")
            self.etapa = nueva_etapa_de_proyecto
            self.porcentaje_avance = 100
            self.save()
            print(f"La obra '{self.nombre}' ha sido finalizada correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR] - al finalizar la obra '{self.nombre}': {e}")
            return False

    def rescindir_obra(self):
        try:
            nueva_etapa_de_proyecto, created = Etapa.get_or_create(nombre = "Rescindida")
            if (created):
                print("Etapa 'Rescindida' creada exitosamente en la DB.")
            self.etapa = nueva_etapa_de_proyecto
            self.save()
            print(f"La obra '{self.nombre}' ha sido rescindida correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR] - al rescindir la obra '{self.nombre}': {e}")
            return False





