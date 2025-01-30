import rispy
import re
from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty

# Cargar la ontología
onto = get_ontology("bibliographic_ontology.owl").load()

# Definir clases si no existen
class ReferenciaBibliografica(Thing):
    namespace = onto

class Autor(Thing):
    namespace = onto

class Publicacion(Thing):
    namespace = onto

class Tema(Thing):
    namespace = onto

class PalabraClave(Thing):
    namespace = onto

# Definir propiedades si no existen
class escritoPor(ObjectProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [Autor]

class publicadoEn(ObjectProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [Publicacion]

class relacionadoCon(ObjectProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [Tema]

class tienePalabraClave(ObjectProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [PalabraClave]

class titulo(DataProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [str]

class anio(DataProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [int]

class doi(DataProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [str]

class url(ObjectProperty):  # Cambiado a ObjectProperty para manejar IRI correctamente
    namespace = onto
    domain = [ReferenciaBibliografica]

class palabrasClave(DataProperty):
    namespace = onto
    domain = [ReferenciaBibliografica]
    range = [str]

# Función para limpiar identificadores
def limpiar_identificador(texto):
    texto = re.sub(r"[^\w\s]", "", texto)  # Eliminar caracteres especiales
    texto = texto.replace(" ", "_")  # Reemplazar espacios con _
    return texto.strip()

# Función para procesar archivo .RIS y agregarlo a la ontología
def agregar_referencia_desde_ris(archivo_ris):
    with open(archivo_ris, "r", encoding="utf-8") as f:
        entradas = rispy.load(f)

    for entrada in entradas:
        titulo_ref = entrada.get("title", "Sin título").strip()
        anio_ref = int(entrada["year"]) if "year" in entrada else None
        doi_ref = entrada.get("doi", "").strip()
        url_ref = entrada.get("url", "").strip()
        autores_ref = [autor.strip() for autor in entrada.get("authors", [])]
        palabras_clave = [kw.strip() for kw in entrada.get("keywords", [])]

        # Generar un identificador limpio
        ref_id = limpiar_identificador(f"Referencia_{titulo_ref}")[:50]  # Limitar longitud

        # Crear el individuo de referencia
        ref_ind = ReferenciaBibliografica(ref_id)
        ref_ind.titulo = [titulo_ref]
        if anio_ref:
            ref_ind.anio = [anio_ref]
        if doi_ref:
            ref_ind.doi = [doi_ref]
        if url_ref:
            ref_ind.url.append(url_ref)  # Ahora como ObjectProperty (IRI)

        if palabras_clave:
            ref_ind.palabrasClave = [", ".join(palabras_clave)]

        # Agregar autores
        for autor in autores_ref:
            autor_nombre = limpiar_identificador(autor)
            autor_ind = onto.search_one(iri=f"*{autor_nombre}") or Autor(autor_nombre)
            ref_ind.escritoPor.append(autor_ind)

        # Agregar palabras clave como individuos
        for palabra in palabras_clave:
            palabra_nombre = limpiar_identificador(palabra)
            palabra_ind = onto.search_one(iri=f"*{palabra_nombre}") or PalabraClave(palabra_nombre)
            ref_ind.tienePalabraClave.append(palabra_ind)

        # Relacionar con temas basados en palabras clave
        for palabra in palabras_clave:
            tema_nombre = limpiar_identificador(palabra)
            tema_ind = onto.search_one(iri=f"*{tema_nombre}") or Tema(tema_nombre)
            ref_ind.relacionadoCon.append(tema_ind)

        # Guardar la ontología actualizada
        onto.save(file="bibliographic_ontology_updated.owl", format="rdfxml")

        # Imprimir la representación RDF del individuo
        print("\n======= 📌 INDIVIDUO GENERADO EN RDF 📌 =======\n")
        print(f'<owl:NamedIndividual rdf:about="#{ref_id}">')
        print(f'  <rdf:type rdf:resource="#ReferenciaBibliografica"/>')
        print(f'  <titulo rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{titulo_ref}</titulo>')
        if anio_ref:
            print(f'  <anio rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">{anio_ref}</anio>')
        if doi_ref:
            print(f'  <doi rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{doi_ref}</doi>')
        if url_ref:
            print(f'  <url rdf:resource="{url_ref}"/>')  # Ahora como IRI en lugar de xsd:anyURI
        for autor in autores_ref:
            print(f'  <escritoPor rdf:resource="#{limpiar_identificador(autor)}"/>')
        for palabra in palabras_clave:
            print(f'  <tienePalabraClave rdf:resource="#{limpiar_identificador(palabra)}"/>')
        for palabra in palabras_clave:
            print(f'  <relacionadoCon rdf:resource="#{limpiar_identificador(palabra)}"/>')
        print('</owl:NamedIndividual>\n')
        print("=============================================\n")
        print(f"✅ Se ha agregado la referencia '{titulo_ref}' a la ontología y guardado el archivo.")

# Ejecutar la función con el archivo .RIS de ejemplo
agregar_referencia_desde_ris("references.ris")
