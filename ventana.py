import datetime
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import shutil
import os
import subprocess
import platform

class VentanaApp(QMainWindow):

    def __init__(self, ):
        super().__init__()

        # Datos imporntantes
        self.ruta_nand = ""
        self.ruta_game_titles = "./game_titles.txt"
        self.ruta_app_dirs = "./app_dirs.txt"
        self.subcarpetas_saves = "/user/save/0000000000000000/6E02850167B8D24D2B5825C75B5EED33/"

        # Colores
        color_fondo = "#3887BE"
        color_texto = "#191919"
        color_texto_blanco = "#F0ECE5"
        color_botones = "#BF3131"
        color_botones_hover = "#A42222"

        # Configuraciones de la ventana
        self.setWindowTitle('Backup YUZU')

        # No permitir cambiar el tamaño de la ventana
        self.setFixedSize(450, 400)

        # Icono de la ventana
        self.setWindowIcon(QIcon("images/logo.ico")) # Reemplaza con la ruta de tu propio ícono

        # Establecer el fondo de color
        self.setStyleSheet(f"background-color: {color_fondo} ;")

        # Crear la tabla
        self.tabla_juegos = QTableWidget(self)
        self.tabla_juegos.setColumnCount(3)
        self.tabla_juegos.setHorizontalHeaderLabels(['Nombre', 'ID', 'Guardar'])
        self.tabla_juegos.setColumnWidth(0, 200)  # Ancho de la columna 'Nombre'
        self.tabla_juegos.setColumnWidth(1, 150)  # Ancho de la columna 'ID'
        self.tabla_juegos.setColumnWidth(2, 30)  # Ancho de la columna 'Guardar'

        # No permitir que el usuario edite los datos de la tabla
        self.tabla_juegos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Ultima fila debe rellenar el espacio restante
        self.tabla_juegos.horizontalHeader().setStretchLastSection(True)

        # Estilo de la tabla
        self.tabla_juegos.setStyleSheet(f"background-color: white; color: {color_texto}; font-size: {13}px; border: 0px;")

        # Llenar la tabla con datos
        self.logica_app()

        # Botón para seleccionar todos los checkbox
        boton_seleccionar_todos = QPushButton('Marcar/Desmarcar Todos', self)
        boton_seleccionar_todos.clicked.connect(self.seleccionar_todos)

        # Botón para crear backup
        boton_crear_backup = QPushButton('Crear Backup', self)
        boton_crear_backup.clicked.connect(self.crear_backup)

        # Botón para configurar la nand
        boton_crear_nand = QPushButton('Configurar carpeta nand', self)
        boton_crear_nand.clicked.connect(self.configurar_ruta_nand)

        # Botón configuracion game tittles
        boton_ver_ids = QPushButton('Ver IDs Juegos', self)
        boton_ver_ids.clicked.connect(self.abrir_game_titles)

        # Botón configuracion game tittles
        boton_ver_directorio = QPushButton('Ver Directorios', self)
        boton_ver_directorio.clicked.connect(self.abrir_app_dirs)

        # Estilo de los botones
        for boton in [boton_seleccionar_todos, boton_crear_backup, boton_crear_nand, boton_ver_ids, boton_ver_directorio]:
            boton.setFixedSize(430, 30)
            boton.setStyleSheet(f"background-color: {color_botones}; color: {color_texto}; font-size: {14}px; border-radius: {3}px;")
            boton.enterEvent = lambda event, boton=boton, color_hover=color_botones_hover: self.cambiar_estilo(boton, color_hover, color_texto_blanco, 14, 3, True)
            boton.leaveEvent = lambda event, boton=boton, color_botones=color_botones: self.cambiar_estilo(boton, color_botones, color_texto, 14, 3, False)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)

        # Tooltip de los botones
        boton_seleccionar_todos.setToolTip("Marcar o desmarcar todos los juegos")
        boton_crear_backup.setToolTip("Crear un respaldo de los juegos seleccionados")
        boton_crear_nand.setToolTip("Configurar la ruta de la nand (necesaria para leer los saves)")
        boton_ver_ids.setToolTip("Ver los IDs de los juegos registrados")
        boton_ver_directorio.setToolTip("Ver los directorios de los juegos registrados")

        # Layout botones arriba
        layout_botones_arriba = QHBoxLayout()
        layout_botones_arriba.addWidget(boton_seleccionar_todos)

        # Layout botones abajo - arriba
        layout_botones_abajo_a = QVBoxLayout()
        layout_botones_abajo_a.addWidget(boton_crear_backup)
        layout_botones_abajo_a.addWidget(boton_crear_nand)

        # Layout botones abajo - abajo
        layout_botones_abajo_ab = QHBoxLayout()
        layout_botones_abajo_ab.addWidget(boton_ver_ids)
        layout_botones_abajo_ab.addWidget(boton_ver_directorio)

        for boton in [boton_ver_ids, boton_ver_directorio]:
            boton.setFixedSize(210, 30)

        # Layout botones abajo
        layout_botones_abajo = QVBoxLayout()
        layout_botones_abajo.addLayout(layout_botones_abajo_a)
        layout_botones_abajo.addLayout(layout_botones_abajo_ab)

        # Layout principal
        layout_principal = QVBoxLayout()
        
        layout_principal.addLayout(layout_botones_arriba)
        layout_principal.addWidget(self.tabla_juegos)
        layout_principal.addLayout(layout_botones_abajo)

        # Crear un QWidget y configurar el layout principal
        central_widget = QWidget(self)
        central_widget.setLayout(layout_principal)

        # Configurar el widget central de la ventana
        self.setCentralWidget(central_widget)
    
    # Manejo de la interfaz
    def logica_app(self):
        
        # Crear los archivos base
        if not os.path.isfile(self.ruta_game_titles): # Si no existe el archivo se crea
            self.crear_plantilla_game_titles()
        
        if not os.path.isfile(self.ruta_app_dirs): # Si no existe el archivo se crea
            self.crear_plantilla_app_dirs()

        # Obtener la ruta nand
        self.obtener_ruta_nand()

        if self.ruta_nand == "": # Si no se ha configurado la ruta de la nand
            self.configurar_ruta_nand()

        # Rellenar la tabla
        self.rellenar_tabla()

    def rellenar_tabla(self):

        if self.ruta_nand == "": # Si no se ha configurado la ruta de la nand
            return

        print("Rellenando tabla ...")

        # Limpiar la tabla
        self.tabla_juegos.setRowCount(0)

        #Lista de juegos
        juegos = self.obtener_game_titles()

        # Lista de carpetas a respaldar
        carpetas = self.obtener_carpetas_a_respaladar()
        for carpeta in carpetas:
            datos = juegos.get(carpeta, self.ruta_nand)
            self.agregar_fila_tabla(datos, carpeta)

    def agregar_fila_tabla(self, nombre, id_juego):
        fila_actual = self.tabla_juegos.rowCount()
        self.tabla_juegos.insertRow(fila_actual)
        self.tabla_juegos.setItem(fila_actual, 0, QTableWidgetItem(nombre))
        self.tabla_juegos.setItem(fila_actual, 1, QTableWidgetItem(id_juego))

        # Agregar un checkbox en la celda correspondiente a "Guardar"
        checkbox = QTableWidgetItem()
        checkbox.setCheckState(Qt.CheckState.Unchecked)  # Desmarcar por defecto
        self.tabla_juegos.setItem(fila_actual, 2, checkbox)
            
    def seleccionar_todos(self):
        # Seleccionar todos los checkboxes en la tabla

        #Si hay al menos una fila marcada, desmarcar todas
        hay_fila_marcada = False
        
        for fila in range(self.tabla_juegos.rowCount()):
            if self.tabla_juegos.item(fila, 2).checkState() == Qt.CheckState.Checked:
                hay_fila_marcada = True
                break
        
        if hay_fila_marcada:
            for fila in range(self.tabla_juegos.rowCount()):
                self.tabla_juegos.item(fila, 2).setCheckState(Qt.CheckState.Unchecked)
        else:
            for fila in range(self.tabla_juegos.rowCount()):
                self.tabla_juegos.item(fila, 2).setCheckState(Qt.CheckState.Checked)

    def abrir_game_titles(self):

        # Verificar si existe el archivo
        if not os.path.isfile("game_titles.txt"): # Si no existe el archivo se crea
            return

        sistema_operativo = platform.system()
        if sistema_operativo == "Windows":
            try:
                subprocess.run(["start", "game_titles.txt"], shell=True)
            except Exception as e:
                print(f"No se pudo abrir el archivo: {e}")
        elif sistema_operativo == "Linux":
            try:
                subprocess.run(["xdg-open", "game_titles.txt"])
            except Exception as e:
                print(f"No se pudo abrir el archivo: {e}")
        else:
            os.system("game_titles.txt")

    def abrir_app_dirs(self):

        # Verificar si existe el archivo
        if not os.path.isfile("app_dirs.txt"): # Si no existe el archivo se crea
            return

        sistema_operativo = platform.system()
        if sistema_operativo == "Windows":
            try:
                subprocess.run(["start", "app_dirs.txt"], shell=True)
            except Exception as e:
                print(f"No se pudo abrir el archivo: {e}")
        elif sistema_operativo == "Linux":
            try:
                subprocess.run(["xdg-open", "app_dirs.txt"])
            except Exception as e:
                print(f"No se pudo abrir el archivo: {e}")
        else:
            os.system("app_dirs.txt")
    
    def cambiar_estilo(self, boton, color, color_texto, font_size, border_radius, hover=True):
        if hover:
            # Aumentar tamaño, cambiar color de fondo y color de texto
            boton.setStyleSheet(f"background-color: {color}; color: {color_texto}; font-size: {font_size+1}px; border-radius: {border_radius}px;")
        else:
            boton.setStyleSheet(f"background-color: {color}; color: {color_texto}; font-size: {font_size}px; border-radius: {border_radius}px;")

    def crear_plantilla_game_titles(self):
        
        # Crear el archivo
        print("Creando archivo de game tittles ...")
        juegos_backup = {
            "Super Smash Bros. Ultimate": "01006A800016E000",
            "Mario Kart 8 Deluxe": "0100152000022000",
            "Luigi's Mansion 3": "0100DCA0064A6000",
            "Mario + Rabbids Kingdom Battle": "010067300059A000",
            "Mario Party Superstars": "01006FE013472000",
            "Mario Strikers: Battle League": "010019401051C000",
            "Metroid Dread": "010093801237C000",
            "Minecraft Legends": "01007C6012CC8000",
            "New Super Mario Bros. U Deluxe": "0100EA80032EA000",
            "Pikmin 4": "0100B7C00933A000",
            "Splatoon 3": "0100C2500FC20000",
            "Super Mario 3D World + Bowser's Fury": "010028600EBDA000",
            "Super Mario Bros. Wonder": "010015100B514000",
            "Super Mario Odyssey": "0100000000010000",
            "The Legend of Zelda: Breath of the Wild": "01007EF00011E000",
            "The Legend of Zelda: Link's Awakening": "01006BB00C6F0000",
            "The Legend of Zelda: Skyward Sword HD": "01002DA013484000",
            "The Legend of Zelda: Tears of the Kingdom": "0100F2C0115B6000"
        }

        # Escribir en el archivo
        with open(self.ruta_game_titles, "w") as archivo:
            for juego, id_juego in juegos_backup.items():
                archivo.write(f"{juego} = {id_juego}\n")
            archivo.close()
        
        print("Se ha creado el archivo de game tittles")

    def crear_plantilla_app_dirs(self):
        # Crear el archivo
        print("Creando archivo de rutas ...")
        archivo_rutas = open("app_dirs.txt", "w")

        # Escribir en el archivo
    
        archivo_rutas.write("# Aqui se encuentra la configuracion de las rutas de la instalaciónd de YUZU \n\n")
        archivo_rutas.write("# Ruta donde se encuentra la nand del emulador, necesario para poder obtener las copias de seguridad\n")
        archivo_rutas.write("# La ruta en en la opción: emulacion > configurar > Sistema > Sistema de archivos > NAND\n")
        archivo_rutas.write("NAND_PATH = \"\"")
        archivo_rutas.close()

        print("Se ha creado el archivo de rutas")

    def configurar_ruta_nand(self):

        QMessageBox.warning(
            self,
            "Ruta de la NAND",
            "Para encontrar la ruta Abre el emulador, ve a\nemulacion > configurar > Sistema > Sistema de archivos > NAND"
        )

        # Obtener la ruta de la carpeta nand
        nueva_ruta = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de la NAND', '.')
        print(nueva_ruta)
        self.ruta_nand = nueva_ruta

        # Verificar que la ruta termina con la carpeta nand
        if not self.ruta_nand.lower().endswith("nand") or not os.path.isdir(self.ruta_nand):
            QMessageBox.warning(
                self,
                "Ruta no válida",
                "La ruta seleccionada no es la correcta"
            )
            return

        if self.ruta_nand == "":
            QMessageBox.warning(
                self,
                "Ruta no válida",
                "La ruta no se ha guardado correctamente"
            )
            return
        
        # Actualizar la ruta en el archivo
        with open('app_dirs.txt', 'w') as archivo:
            archivo.write("# Aqui se encuentra la configuracion de las rutas de la instalaciónd de YUZU \n\n")
            archivo.write("# Ruta donde se encuentra la nand del emulador, necesario para poder obtener las copias de seguridad\n")
            archivo.write("# La ruta en en la opción: emulacion > configurar > Sistema > Sistema de archivos > NAND\n")
            archivo.write(f"NAND_PATH = \"{ self.ruta_nand}\"")
            archivo.close()

        # Rellenar la tabla
        self.rellenar_tabla()

    #  Logica de la aplicación
    def obtener_ruta_nand(self):
        
        # Verificar si existe el archivo
        if not os.path.isfile(self.ruta_app_dirs): # Si no existe el archivo se crea
            self.crear_plantilla_app_dirs()
            
        # Verificar si existe los game titles
        if not os.path.isfile(self.ruta_game_titles): # Si no existe el archivo se crea
            self.crear_plantilla_game_titles()
        
        with open('app_dirs.txt', 'r') as archivo:
            for linea in archivo:
                if 'NAND_PATH' in linea:
                    ruta = linea.split('=')[1].strip()  # Obtener la parte después del signo igual y eliminar espacios en blanco
                    self.ruta_nand = ruta.strip('"')  # Eliminar comillas si están presentes
                    archivo.close()
                    break  # No es necesario seguir leyendo el archivo después de encontrar la línea
            
            archivo.close()
            
        # Si no se ha configurado la ruta de la nand
        if self.ruta_nand == "":
            QMessageBox.warning(
                self,
                "Ruta de la NAND",
                "No se ha configurado la ruta de la NAND. Por favor, configura NAND\n"
            )
            return

    def obtener_game_titles(self):

        juegos = {}

        # Leer el archivo game_titles.txt y llenar el diccionario
        with open(self.ruta_game_titles, 'r') as archivo:
            for linea in archivo:
                partes = linea.strip().split('=')
                if len(partes) == 2:
                    id_juego = partes[1].strip()
                    nombre_juego = partes[0].strip()
                    juegos[id_juego] = nombre_juego
            
            archivo.close()

        return juegos

    def obtener_carpetas_a_respaladar(self):
        carpetas = []

        #Si esta configurada la ruta de la nand
        if self.ruta_nand == "":
            QMessageBox.warning(
                self,
                "Ruta de la NAND",
                "No se ha configurado la ruta de la NAND. Por favor, configura NAND\n"
            )
            return

        ruta_carpetas = self.ruta_nand + self.subcarpetas_saves

        #Obtener las subcarpetas
        for carpeta in os.listdir(ruta_carpetas):

            # Verificar que sea una carpeta y que tenga archivos
            if os.path.isdir(ruta_carpetas + carpeta) and os.listdir(ruta_carpetas + carpeta):
                carpetas.append(carpeta)

        return carpetas

    def crear_backup(self):
        try:
            #Si esta configurada la ruta de la nand
            if self.ruta_nand == "":
                QMessageBox.warning(
                    self,
                    "Ruta de la NAND",
                    "No se ha configurado la ruta de la NAND. Por favor, configura NAND\n"
                )
                return

            #Si hay al menos una fila marcada, desmarcar todas
            hay_fila_marcada = False

            for fila in range(self.tabla_juegos.rowCount()):
                if self.tabla_juegos.item(fila, 2).checkState() == Qt.CheckState.Checked:
                    hay_fila_marcada = True
                    break
            
            if not hay_fila_marcada:
                QMessageBox.warning(
                    self,
                    "Sin juegos seleccionados",
                    "No se ha seleccionado ningún juego para crear el respaldo"
                )
                return

            #Preguntar por la ruta de destino
            ruta_destino = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta para saves', '.')

            juegos_guardados = {} # Diccionario para guardar los juegos que se han respaldado

            
            # Obtener los datos de las casiilas marcadas
            for fila in range(self.tabla_juegos.rowCount()):
                if self.tabla_juegos.item(fila, 2).checkState() == Qt.CheckState.Checked:
                    nombre = self.tabla_juegos.item(fila, 0).text()
                    id_juego = self.tabla_juegos.item(fila, 1).text()

                    # Obtiene la ruta de la carpeta a respaldar
                    ruta_backup = self.ruta_nand + self.subcarpetas_saves + id_juego

                    # Verificar que la carpeta exista
                    if not os.path.isdir(ruta_backup):
                        print(f"La carpeta {ruta_backup} no existe")
                        continue

                    # Crear la carpeta en la ruta de destino
                    ruta_destino_juego = ruta_destino + "/" + id_juego

                    # Copiar los archivos y carpetas (incluyen subcarpetas)
                    try:
                        # Copiar el directorio y su contenido
                        print(f"Creando backup de '{nombre}'")
                        shutil.copytree(ruta_backup, ruta_destino_juego, dirs_exist_ok=True)
                        print(f"Se ha copiado correctamente de '{ruta_backup}' a '{ruta_destino_juego}'")
                        # Agregar el juego a la lista de juegos guardados
                        juegos_guardados[nombre] = id_juego
                    except Exception as e:
                        print(f"Error al copiar: {e}")


            # Ruta del archivo de juegos guardados
            archivo_juegos_guardados = ruta_destino + "/juegos_guardados.txt"

            # Crear o abrir archivo con resumen de los juegos guardados
            with open(archivo_juegos_guardados, "a+") as archivo:
                juegos_registrados = set()

                # Leer los juegos ya registrados
                archivo.seek(0)
                for linea in archivo:
                    partes = linea.strip().split(" : ")
                    if len(partes) == 2:
                        juego_registrado = partes[0]
                        juegos_registrados.add(juego_registrado)

                for juego, id_juego in juegos_guardados.items():
                    fecha = datetime.datetime.now()
                    fecha = fecha.strftime("%d/%m/%Y %H:%M")

                    # Verificar si el juego ya está registrado
                    if juego in juegos_registrados:
                        # Actualizar la línea si el juego ya está registrado
                        archivo.seek(0)
                        lineas = archivo.readlines()
                        archivo.seek(0)
                        archivo.truncate(0)  # Limpiar el contenido del archivo
                        for i, linea in enumerate(lineas):
                            if juego in linea:
                                lineas[i] = f"{juego} : {id_juego}  -> {fecha}\n"
                            archivo.write(lineas[i])
                    else:
                        # Agregar el juego al final del archivo si no está registrado
                        archivo.write(f"{juego} : {id_juego}  -> {fecha}\n")

                archivo.close()
            
            # Mostrar mensaje de finalización de los respaldos
            if juegos_guardados:
                mensaje = "Se han creado los siguientes respaldos:\n"
                for juego, id_juego in juegos_guardados.items():
                    mensaje += f"{juego} : {id_juego}\n"
                QMessageBox.information(self, "Copia generada", mensaje)
            else:
                QMessageBox.warning(self, "Copia generada", "No se ha creado ningún respaldo")
        
        except Exception as e:
            print(f"Error al crear el respaldo: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaApp()
    ventana.show()
    sys.exit(app.exec())