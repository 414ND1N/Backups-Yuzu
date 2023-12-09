import datetime
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import shutil
import os
import subprocess
import platform

class VentanaApp(QMainWindow):

    def __init__(self, ):
        super().__init__()
        self.inicializarUI()
    
    def inicializarUI(self):

        # Configuraciones de la ventana
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Backup YUZU')

        # Icono de la ventana
        icono = QIcon("images/logo.ico")  # Reemplaza con la ruta de tu propio ícono
        self.setWindowIcon(icono)

        # Establecer el fondo de color
        self.setStyleSheet("background-color: #265073;")

        # Crear la tabla
        self.tabla_juegos = QTableWidget(self)
        self.tabla_juegos.setColumnCount(3)
        self.tabla_juegos.setHorizontalHeaderLabels(['Nombre', 'ID', 'Guardar'])
        self.tabla_juegos.setColumnWidth(0, 200)  # Ancho de la columna 'Nombre'
        self.tabla_juegos.setColumnWidth(1, 100)  # Ancho de la columna 'ID'
        self.tabla_juegos.setColumnWidth(2, 50)  # Ancho de la columna 'Guardar'

        # Llenar la tabla con datos
        self.logica_app()

        # Crear un QVBoxLayout independiente
        layout_principal = QVBoxLayout()
        
        # Botón para seleccionar todos los checkbox
        boton_seleccionar_todos = QPushButton('Marcar/Desmarcar Todos', self)
        boton_seleccionar_todos.clicked.connect(self.seleccionar_todos)

        # Agregar el botón y la tabla al layout
        layout_principal.addWidget(boton_seleccionar_todos)
        layout_principal.addWidget(self.tabla_juegos)

        # Botón configuracion game tittles
        boton_crear_backup = QPushButton('Ver IDs Juegos', self)
        boton_crear_backup.clicked.connect(self.abrir_game_titles)
        layout_principal.addWidget(boton_crear_backup)

        # Botón configuracion game tittles
        boton_crear_backup = QPushButton('Ver Directorios', self)
        boton_crear_backup.clicked.connect(self.abrir_app_dirs)
        layout_principal.addWidget(boton_crear_backup)

        # Botón para crear backup
        boton_crear_backup = QPushButton('Crear Backup', self)
        boton_crear_backup.clicked.connect(self.crear_backup)
        layout_principal.addWidget(boton_crear_backup)

        # Crear un widget central y configurar el layout principal
        central_widget = QWidget()
        central_widget.setLayout(layout_principal)

        # Configurar el widget central de la ventana
        self.setCentralWidget(central_widget)
        
        self.show()
    
    # Manejo de la interfaz
    def logica_app(self):
        
        # Obtener las rutas
        ruta_nand = self.obtener_ruta_nand()

        #Lista de juegos
        juegos = self.obtener_game_titles()

        # Lista de carpetas a respaldar
        carpetas = self.obtener_carpetas_a_respaladar(ruta_nand)
        for carpeta in carpetas:
            datos = juegos.get(carpeta, ruta_nand)
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

    #  Logica de la aplicación
    def obtener_ruta_nand(self):

        ruta_datos_nand = ""
        
        # Verificar si existe el archivo
        if not os.path.isfile("app_dirs.txt"): # Si no existe el archivo se crea
            print("Creando archivo de rutas ...")
            # Crear el archivo
            archivo_rutas = open("app_dirs.txt", "w")

            # Escribir en el archivo
        
            archivo_rutas.write("#Aqui se encuentra la configuracion de las rutas de la instalaciónd de YUZU \n")
            archivo_rutas.write("#Se encuentra la ruta en yuzu > emulacion > configurar > Sistema > Sistema de archivos > NAND\n")
            archivo_rutas.write("NAND_PATH = \"\"")
            archivo_rutas.close()

        # Verificar si existe los game tittles
        if not os.path.isfile("game_titles.txt"): # Si no existe el archivo se crea
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

            # Escribir la lista en el archivo
            with open("game_titles.txt", "w") as archivo:
                for juego, id_juego in juegos_backup.items():
                    archivo.write(f"{juego} = {id_juego}\n")
        
        with open('app_dirs.txt', 'r') as archivo:
            for linea in archivo:
                if 'NAND_PATH' in linea:
                    ruta = linea.split('=')[1].strip()  # Obtener la parte después del signo igual y eliminar espacios en blanco
                    ruta_datos_nand = ruta.strip('"')  # Eliminar comillas si están presentes
                    archivo.close()
                    break  # No es necesario seguir leyendo el archivo después de encontrar la línea
            
            archivo.close()
            

        while ruta_datos_nand == "":
            ruta_datos_nand = self.obtener_ruta_desde_cuadro_dialogo()

            # Verificar que la ruta termina con la carpeta nand
            if not ruta_datos_nand.endswith("nand") or not os.path.isdir(ruta_datos_nand):
                print("La ruta seleccionada no es la correcta !!")
                continue

            # Guardar la ruta en el archivo
            with open('app_dirs.txt', 'w') as archivo:
                archivo.write("#Aqui se encuentra la configuracion de las rutas de la instalaciónd de YUZU \n")
                archivo.write("#Se encuentra la ruta en yuzu > emulacion > configurar > Sistema > Sistema de archivos > NAND\n")
                archivo.write(f"NAND_PATH = \"{ ruta_datos_nand}\"")
                archivo.close()

            if ruta_datos_nand != "":
                break

        return ruta_datos_nand

    def obtener_ruta_desde_cuadro_dialogo(self):
        dialogo = QFileDialog()
        dialogo.setFileMode(QFileDialog.FileMode.Directory)
        dialogo.setOption(QFileDialog.Option.ShowDirsOnly, True)

        if dialogo.exec() == QFileDialog.DialogCode.Accepted:
            rutas_seleccionadas = dialogo.selectedFiles()
            if rutas_seleccionadas:
                ruta_seleccionada = rutas_seleccionadas[0]
                print('ruta seleccionada: ',ruta_seleccionada)
                # Puedes almacenar esta ruta en el archivo o realizar las operaciones necesarias
                return ruta_seleccionada

        return ""

    def obtener_game_titles(self):
        juegos = {}

        # Leer el archivo game_titles.txt y llenar el diccionario
        with open('game_titles.txt', 'r') as archivo:
            for linea in archivo:
                partes = linea.strip().split('=')
                if len(partes) == 2:
                    id_juego = partes[1].strip()
                    nombre_juego = partes[0].strip()
                    juegos[id_juego] = nombre_juego
            
            archivo.close()

        return juegos

    def obtener_carpetas_a_respaladar(self, ruta_datos_nand):
        carpetas = []
        ruta_carpetas = ruta_datos_nand + "/user/save/0000000000000000/6E02850167B8D24D2B5825C75B5EED33/"
       

        #Obtener las subcarpetas
        for carpeta in os.listdir(ruta_carpetas):

            # Verificar que sea una carpeta y que tenga archivos
            if os.path.isdir(ruta_carpetas + carpeta) and os.listdir(ruta_carpetas + carpeta):
                carpetas.append(carpeta)

        return carpetas

    def crear_backup(self):
        #Preguntar por la ruta de destino
        ruta_destino = self.obtener_ruta_desde_cuadro_dialogo()
        if ruta_destino == "":
            return

        juegos_guardados = {}

        # Obtener los datos de las casiilas marcadas
        for fila in range(self.tabla_juegos.rowCount()):
            if self.tabla_juegos.item(fila, 2).checkState() == Qt.CheckState.Checked:
                nombre = self.tabla_juegos.item(fila, 0).text()
                id_juego = self.tabla_juegos.item(fila, 1).text()

                ruta_nand = self.obtener_ruta_nand()

                # Obtiene la ruta de la carpeta a respaldar
                ruta_backup = ruta_nand + "/user/save/0000000000000000/6E02850167B8D24D2B5825C75B5EED33/" + id_juego

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaApp()
    sys.exit(app.exec())