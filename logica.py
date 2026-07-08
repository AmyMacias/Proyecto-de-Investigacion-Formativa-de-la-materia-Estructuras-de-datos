import json
import random
import os

# Cargar recetas desde el archivo JSON local
ruta_json = os.path.join(os.path.dirname(__file__), 'Recetas.json')
with open(ruta_json, 'r', encoding='utf-8') as f:
    data = json.load(f)

INGREDIENTES = data['ingredientes']
RECETAS = data['recetas']


# ─── Lista Enlazada ───────────────────────────────────────────

class Nodo:
    def __init__(self, ingrediente):
        self.ingrediente = ingrediente
        self.siguiente = None
        self.anterior = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.tamanio = 0

    def agregar(self, ingrediente):
        nuevo = Nodo(ingrediente)
        if self.cabeza is None:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
            nuevo.anterior = actual
        self.tamanio += 1

    def eliminar(self, ingrediente):
        actual = self.cabeza
        while actual:
            if actual.ingrediente == ingrediente:
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                self.tamanio -= 1
                return True
            actual = actual.siguiente
        return False

    def mostrar(self):
        ingredientes = []
        actual = self.cabeza
        while actual:
            ingredientes.append(actual.ingrediente)
            actual = actual.siguiente
        return ingredientes

    def esta_llena(self):
        return self.tamanio == 6


# ─── Árbol de Recetas ─────────────────────────────────────────

class NodoArbol:
    def __init__(self, nombre, ingredientes=None):
        self.nombre = nombre
        self.ingredientes = ingredientes
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)


class ArbolRecetas:
    def __init__(self):
        self.raiz = NodoArbol('Recetas')

    def cargar_desde_json(self, recetas):
        for categoria, platos in recetas.items():
            nodo_categoria = NodoArbol(categoria)
            for nombre_plato, ingredientes in platos.items():
                nodo_receta = NodoArbol(nombre_plato, ingredientes)
                nodo_categoria.agregar_hijo(nodo_receta)
            self.raiz.agregar_hijo(nodo_categoria)

    def buscar_receta(self, seleccion):
        seleccion_ordenada = sorted(seleccion)
        for categoria in self.raiz.hijos:
            for receta in categoria.hijos:
                if sorted(receta.ingredientes) == seleccion_ordenada:
                    return receta.nombre, categoria.nombre
        return None, None


# ─── Lógica del Juego ─────────────────────────────────────────

class JuegoChef:
    def __init__(self):
        self.arbol = ArbolRecetas()
        self.arbol.cargar_desde_json(RECETAS)
        self.banda = ListaEnlazada()
        self.descartes_usados = 0
        self.MAX_DESCARTES = 2
        self.seleccion = []

    def generar_banda(self):
        self.banda = ListaEnlazada()
        self.descartes_usados = 0
        self.seleccion = []
        ingredientes_ronda = random.sample(INGREDIENTES, 6)
        for ing in ingredientes_ronda:
            self.banda.agregar(ing)

    def descartar(self, ingrediente):
        if self.descartes_usados >= self.MAX_DESCARTES:
            return False, 'Ya usaste todos tus descartes'
        if self.banda.eliminar(ingrediente):
            disponibles = [i for i in INGREDIENTES if i not in self.banda.mostrar()]
            reemplazo = random.choice(disponibles)
            self.banda.agregar(reemplazo)
            self.descartes_usados += 1
            return True, reemplazo
        return False, f'{ingrediente} no está en la banda'

    def seleccionar(self, ingrediente):
        if ingrediente in self.seleccion:
            self.seleccion.remove(ingrediente)
            return 'deseleccionado'
        if len(self.seleccion) >= 4:
            return 'lleno'
        self.seleccion.append(ingrediente)
        return 'seleccionado'

    def validar_receta(self):
        if len(self.seleccion) != 4:
            return None, None, 'Selecciona exactamente 4 ingredientes'
        nombre, categoria = self.arbol.buscar_receta(self.seleccion)
        if nombre:
            return nombre, categoria, 'valida'
        return None, None, 'invalida'
