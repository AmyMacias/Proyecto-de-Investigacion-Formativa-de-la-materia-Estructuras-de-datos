# %%
import sys
import os
import pygame
from logica import JuegoChef, INGREDIENTES

# INICIALIZACIÓN DE PYGAME
pygame.init()
pygame.font.init()
pygame.mixer.init()  # <--- [NUEVO] Inicializa el sistema de audio

# Dimensiones exactas basadas en tu lienzo
ANCHO, ALTO = 1000, 560  
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Disaster Chef - Estructuras de Datos")
reloj = pygame.time.Clock()

COLOR_TEXTO = (255, 255, 255)
fuente_hud = pygame.font.SysFont("Impact", 24)
fuente_menu = pygame.font.SysFont("Impact", 36)
fuente_ing = pygame.font.SysFont("Arial", 12, bold=True)
fuente_recetas = pygame.font.SysFont("Arial", 14, bold=True)

# MANEJO DE RUTAS Y ENTORNO SEGURO
try:
    carpeta_actual = os.path.dirname(__file__)
except NameError:
    carpeta_actual = os.getcwd()

# CARGA DE ASSETS GRÁFICOS

# Fondo del juego
ruta_fondo = os.path.join(carpeta_actual, "fondo_juego.png")
if os.path.exists(ruta_fondo):
    fondo_img = pygame.image.load(ruta_fondo).convert()
    fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
else:
    print(" Error: No se encontró 'fondo_juego.png'.")
    fondo_img = None

# Logo del menú de inicio
ruta_logo = os.path.join(carpeta_actual, "logo.jpg.jpeg")
if os.path.exists(ruta_logo):
    logo_img = pygame.image.load(ruta_logo).convert()
    logo_img = pygame.transform.scale(logo_img, (ANCHO, ALTO))
else:
    print(" Error: No se encontró 'logo.jpg'.")
    logo_img = None

# ingredientes
IMAGENES_INGREDIENTES = {}
for ing in INGREDIENTES:
    posibles_ext = ['.png', '.jpg', '.jpeg', '.PNG']
    imagen_cargada = False
    for ext in posibles_ext:
        ruta_img = os.path.join(carpeta_actual, f"{ing}{ext}")
        if os.path.exists(ruta_img):
            try:
                img_surf = pygame.image.load(ruta_img).convert_alpha()
                IMAGENES_INGREDIENTES[ing] = pygame.transform.scale(img_surf, (60, 60))
                imagen_cargada = True
                break
            except Exception as e:
                print(f"Error cargando {ruta_img}: {e}")
    if not imagen_cargada:
        print(f"Error: Sin imagen para '{ing}'.")


# ==========================================
# CARGA DE ASSETS DE AUDIO [NUEVO]
# ==========================================
sonidos = {}
ruta_sonidos = r"C:\sonidos"

try:
    # Efectos de sonido desde tu carpeta C:\sonidos
    sonidos['start'] = pygame.mixer.Sound(os.path.join(ruta_sonidos, "start.wav"))
    sonidos['cocinar'] = pygame.mixer.Sound(os.path.join(ruta_sonidos, "sonidodecocinar.wav"))
    sonidos['exito'] = pygame.mixer.Sound(os.path.join(ruta_sonidos, "exito.wav"))
    sonidos['fallo'] = pygame.mixer.Sound(os.path.join(ruta_sonidos, "fallo.wav"))
    sonidos['basura'] = pygame.mixer.Sound(os.path.join(ruta_sonidos, "basura.wav"))
    sonidos['tiempo'] = pygame.mixer.Sound(os.path.join(ruta_sonidos, "tiempoacabado.wav"))
    
    # Música de fondo
    ruta_musica = os.path.join(ruta_sonidos, "musicadefondo.wav")
    if os.path.exists(ruta_musica):
        pygame.mixer.music.load(ruta_musica)
        pygame.mixer.music.set_volume(0.3)  # Volumen de la música de fondo al 30%
except Exception as e:
    print(f"Advertencia: Hubo un problema al cargar sonidos desde {ruta_sonidos}: {e}")
# ==========================================


# INSTANCIA Y GEOMETRÍA DEL TABLERO
juego = JuegoChef()
juego.generar_banda()

# Lista global para el registro visual de recetas completadas
recetas_descubiertas = []

# Variables del Temporizador Real
TIEMPO_INICIAL = 45
tiempo_restante = TIEMPO_INICIAL
EVENTO_TEMPORIZADOR = pygame.USEREVENT + 1
pygame.time.set_timer(EVENTO_TEMPORIZADOR, 1000)

# Coordenadas de la interfaz
rects_banda_slots = [pygame.Rect(46, 50 + (i * 76), 136, 68) for i in range(6)]
rects_tabla_slots = [
    pygame.Rect(280, 230, 100, 90),  
    pygame.Rect(440, 230, 100, 90),   
    pygame.Rect(280, 340, 100, 90),   
    pygame.Rect(440, 340, 100, 90)    
]

# Botones del Juego
btn_cocinar_rect = pygame.Rect(665, 245, 150, 45)  
rect_basurero = pygame.Rect(865, 60, 130, 240)    
btn_salir_rect = pygame.Rect(855, 495, 120, 40)

# Botón del Menú de Inicio
btn_start_rect = pygame.Rect(400, 450, 200, 60)

ingrediente_seleccionado_para_descarte = None
mensaje_consola = "Chef: Haz clic en un ingrediente de la banda para cocinarlo o descartarlo."

# ESTADOS DEL JUEGO
ESTADO_MENU = 0
ESTADO_JUEGO = 1
estado_actual = ESTADO_MENU

def dibujar_libro_recetas(superficie):
    # Contenedor tipo pergamino/pizarra pequeña
    rect_libro = pygame.Rect(250, 15, 260, 160)
    pygame.draw.rect(superficie, (44, 53, 57), rect_libro, border_radius=6)
    pygame.draw.rect(superficie, (230, 126, 34), rect_libro, 2, border_radius=6)
    
    # Título
    txt_titulo = fuente_recetas.render("RECETAS LOGRADAS:", True, (241, 196, 15))
    superficie.blit(txt_titulo, (rect_libro.x + 10, rect_libro.y + 8))
    
    # Mostrar últimas 5 recetas completadas para no saturar el espacio
    desplazamiento_y = 30
    if not recetas_descubiertas:
        txt_vacio = fuente_ing.render("Ninguna receta cocinada aún...", True, (149, 165, 166))
        superficie.blit(txt_vacio, (rect_libro.x + 10, rect_libro.y + desplazamiento_y))
    else:
        for receta in recetas_descubiertas[-5:]:
            txt_receta = fuente_ing.render(f"  {receta['nombre']} ({receta['cat']})", True, (255, 255, 255))
            superficie.blit(txt_receta, (rect_libro.x + 10, rect_libro.y + desplazamiento_y))
            desplazamiento_y += 22

# BUCLE PRINCIPAL
ejecutando = True
while ejecutando:
    pos_mouse = pygame.mouse.get_pos()
    
    # PROCESAMIENTO DE EVENTOS 
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

       # El temporizador solo corre si estamos jugando activamente
        elif evento.type == EVENTO_TEMPORIZADOR and estado_actual == ESTADO_JUEGO:
            if tiempo_restante > 0:
                tiempo_restante -= 1
                
                # --- LÓGICA: Cuenta regresiva de tensión ---
                if tiempo_restante <= 10 and tiempo_restante > 0:
                    print(f"Reloj en {tiempo_restante}... Intentando reproducir sonido.") # <--- Mensaje de prueba
                    if 'tiempo' in sonidos: 
                        sonidos['tiempo'].play()
                    else:
                        print("Error: El sonido 'tiempo' no está cargado en el diccionario.")
                # -------------------------------------------------
                
            else:
                if 'fallo' in sonidos: sonidos['fallo'].play() 
                mensaje_consola = "¡Tiempo agotado! Se penalizó la ronda."
                juego.generar_banda() 
                tiempo_restante = TIEMPO_INICIAL
            
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                
                # CONTROL DE EVENTOS EN EL MENÚ
                if estado_actual == ESTADO_MENU:
                    if btn_start_rect.collidepoint(pos_mouse):
                        if 'start' in sonidos: sonidos['start'].play()  # <--- [REPRODUCIR] Click de inicio
                        try:
                            pygame.mixer.music.play(-1)  # <--- [REPRODUCIR] Música en loop infinito
                        except Exception:
                            pass
                        estado_actual = ESTADO_JUEGO
                        tiempo_restante = TIEMPO_INICIAL
                
                # CONTROL DE EVENTOS EN EL JUEGO
                elif estado_actual == ESTADO_JUEGO:
                    # Salir del programa
                    if btn_salir_rect.collidepoint(pos_mouse):
                        pygame.mixer.music.stop()  # Detener música al salir
                        ejecutando = False
                    
                    # Clic en los ingredientes de la banda
                    ingredientes_cinta = juego.banda.mostrar()
                    for i, rect_slot in enumerate(rects_banda_slots):
                        if i < len(ingredientes_cinta) and rect_slot.collidepoint(pos_mouse):
                            ing = ingredientes_cinta[i]
                            ingrediente_seleccionado_para_descarte = ing
                            
                            resultado = juego.seleccionar(ing)
                            if resultado == 'seleccionado':
                                if 'cocinar' in sonidos: sonidos['cocinar'].play()  # <--- [REPRODUCIR] Agarra ingrediente
                                mensaje_consola = f"Agregado a la tabla: {ing}"
                            elif resultado == 'deseleccionado':
                                if 'cocinar' in sonidos: sonidos['cocinar'].play()  # <--- [REPRODUCIR] Quita ingrediente
                                mensaje_consola = f"Quitado de la tabla: {ing}"
                            elif resultado == 'lleno':
                                if 'fallo' in sonidos: sonidos['fallo'].play()  # <--- [REPRODUCIR] Alerta de tabla llena
                                mensaje_consola = "¡La tabla ya está llena (Máx 4)!"

                    # Enviar al Basurero (Descarte)
                    if rect_basurero.collidepoint(pos_mouse) and ingrediente_seleccionado_para_descarte:
                        exito, msg = juego.descartar(ingrediente_seleccionado_para_descarte)
                        if exito:
                            if 'basura' in sonidos: sonidos['basura'].play()  # <--- [REPRODUCIR] Tirar a la basura
                            mensaje_consola = f"¡Descartado! Entró: {msg} a la banda."
                            if ingrediente_seleccionado_para_descarte in juego.seleccion:
                                juego.seleccion.remove(ingrediente_seleccionado_para_descarte)
                            ingrediente_seleccionado_para_descarte = None
                        else:
                            if 'fallo' in sonidos: sonidos['fallo'].play()  # <--- [REPRODUCIR] Alerta límite de basura
                            mensaje_consola = f"Límite: {msg}"

                    # Validar combinación al oprimir Cocinar
                    if btn_cocinar_rect.collidepoint(pos_mouse):
                        nombre, categoria, estado = juego.validar_receta()
                        if estado == 'valida':
                            if 'exito' in sonidos: sonidos['exito'].play()  # <--- [REPRODUCIR] Receta bien hecha
                            mensaje_consola = f" ¡ÉXITO!: {nombre} ({categoria}). Siguiente ronda."
                            
                            # Guardamos la receta en el registro si no fue agregada antes
                            if not any(r['nombre'] == nombre for r in recetas_descubiertas):
                                recetas_descubiertas.append({'nombre': nombre, 'cat': categoria})
                                
                            juego.generar_banda()
                            ingrediente_seleccionado_para_descarte = None
                            tiempo_restante = TIEMPO_INICIAL # Reiniciamos el reloj tras un acierto
                        elif estado == 'invalida':
                            if 'fallo' in sonidos: sonidos['fallo'].play()  # <--- [REPRODUCIR] Receta fallida
                            mensaje_consola = "Error: Combinación errónea. ¡No existe la receta!"
                        else:
                            if 'fallo' in sonidos: sonidos['fallo'].play()
                            mensaje_consola = f"Peligro {estado}"

    # DIBUJO 
    if estado_actual == ESTADO_MENU:
        # Dibujar pantalla de inicio
        if logo_img:
            pantalla.blit(logo_img, (0, 0))
        else:
            pantalla.fill((44, 62, 80))
            
        # Botón para iniciar "START"
        pygame.draw.rect(pantalla, (230, 126, 34), btn_start_rect, border_radius=10)
        pygame.draw.rect(pantalla, (255, 255, 255), btn_start_rect, 3, border_radius=10)
        txt_start = fuente_menu.render("START", True, COLOR_TEXTO)
        pantalla.blit(txt_start, (btn_start_rect.x + 55, btn_start_rect.y + 8))

    elif estado_actual == ESTADO_JUEGO:
        # Dibujar Tablero de Cocina
        if fondo_img:
            pantalla.blit(fondo_img, (0, 0)) 
        else:
            pantalla.fill((210, 142, 85))

        # 1. Dibujar ingredientes de la cinta
        lista_cinta = juego.banda.mostrar()
        for i, rect_slot in enumerate(rects_banda_slots):
            if i < len(lista_cinta):
                ing = lista_cinta[i]
                if ing == ingrediente_seleccionado_para_descarte:
                    pygame.draw.rect(pantalla, (230, 126, 34), rect_slot, 3, border_radius=4)
                elif ing in juego.seleccion:
                    pygame.draw.rect(pantalla, (46, 204, 113), rect_slot, 3, border_radius=4)
                
                if ing in IMAGENES_INGREDIENTES:
                    img_x = rect_slot.x + (rect_slot.width - 60) // 2
                    img_y = rect_slot.y + (rect_slot.height - 60) // 2
                    pantalla.blit(IMAGENES_INGREDIENTES[ing], (img_x, img_y))
                else:
                    txt = fuente_ing.render(ing, True, COLOR_TEXTO)
                    pantalla.blit(txt, (rect_slot.x + 10, rect_slot.y + 25))

        # 2. Dibujar ingredientes de la Tabla de Picar
        for idx, ing_sel in enumerate(juego.seleccion):
            if idx < 4:
                slot_rect = rects_tabla_slots[idx]
                if ing_sel in IMAGENES_INGREDIENTES:
                    img_x = slot_rect.x + (slot_rect.width - 60) // 2
                    img_y = slot_rect.y + (slot_rect.height - 60) // 2
                    pantalla.blit(IMAGENES_INGREDIENTES[ing_sel], (img_x, img_y))
                else:
                    txt_sel = fuente_ing.render(ing_sel, True, (0, 0, 0))
                    pantalla.blit(txt_sel, (slot_rect.x + 10, slot_rect.y + 35))

        # 3. Componentes HUD interactivos
        
        # Libro de recetas cargadas
        dibujar_libro_recetas(pantalla)

        # Botón Cocinar
        pygame.draw.rect(pantalla, (192, 57, 43), btn_cocinar_rect, border_radius=8) 
        pygame.draw.rect(pantalla, (255, 255, 255), btn_cocinar_rect, 2, border_radius=8) 
        txt_cocinar = fuente_hud.render("COCINAR", True, COLOR_TEXTO)
        pantalla.blit(txt_cocinar, (btn_cocinar_rect.x + 28, btn_cocinar_rect.y + 8))

        # HUD de Tiempo
        pygame.draw.rect(pantalla, (20, 20, 20), (730, 20, 160, 40), border_radius=5)
        txt_tiempo = fuente_hud.render(f"TIME: {tiempo_restante} SEG", True, (241, 196, 15)) 
        pantalla.blit(txt_tiempo, (742, 27))

        # Contador de Descartes (En el basurero)
        pygame.draw.rect(pantalla, (39, 174, 96), (875, 135, 110, 30), border_radius=4) 
        pygame.draw.rect(pantalla, (255, 255, 255), (875, 135, 110, 30), 1, border_radius=4)
        lbl_desc = fuente_ing.render(f"Descartes: {juego.descartes_usados}/{juego.MAX_DESCARTES}", True, COLOR_TEXTO)
        pantalla.blit(lbl_desc, (882, 143))

        # Botón para salir del juego
        pygame.draw.rect(pantalla, (44, 62, 80), btn_salir_rect, border_radius=6) 
        pygame.draw.rect(pantalla, (231, 76, 60), btn_salir_rect, 2, border_radius=6)  
        txt_salir = fuente_hud.render("SALIR >>", True, COLOR_TEXTO)
        pantalla.blit(txt_salir, (btn_salir_rect.x + 18, btn_salir_rect.y + 6))

        # Consola interactiva de logs (Abajo)
        pygame.draw.rect(pantalla, (30, 30, 30), (250, 500, 520, 35), border_radius=6)
        txt_msg = fuente_ing.render(mensaje_consola, True, (46, 204, 113))
        pantalla.blit(txt_msg, (265, 510))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()