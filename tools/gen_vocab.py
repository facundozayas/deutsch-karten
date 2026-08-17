#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera data/vocab-a1.json a partir de las listas curadas de vocabulario A1
(basadas en la lista oficial del Goethe-Zertifikat A1 / Start Deutsch 1).

Formato de cada tupla: (de, es, en, kind, ejemplo_de, ejemplo_es)
  kind: "der" | "die" | "das" (sustantivo) | "verbo" | "frase" | "adjetivo"
        | "adverbio" | "partícula" | "número"
"""
import json
import re
import unicodedata

CATEGORIES = {}

def cat(name):
    CATEGORIES[name] = []
    return CATEGORIES[name]

# ---------------------------------------------------------------------------
saludos = cat("saludos y presentaciones")
saludos += [
    ("Hallo", "hola", "hello", "frase", "Hallo! Wie geht es dir?", "¡Hola! ¿Cómo estás?"),
    ("Guten Morgen", "buenos días (mañana)", "good morning", "frase", "Guten Morgen! Hast du gut geschlafen?", "¡Buenos días! ¿Dormiste bien?"),
    ("Guten Tag", "buenos días / buenas tardes", "good day", "frase", "Guten Tag, wie kann ich Ihnen helfen?", "Buenos días, ¿en qué puedo ayudarle?"),
    ("Guten Abend", "buenas noches (saludo)", "good evening", "frase", "Guten Abend, kommen Sie herein.", "Buenas noches, pase usted."),
    ("Gute Nacht", "buenas noches (despedida)", "good night", "frase", "Gute Nacht, schlaf gut!", "¡Buenas noches, que duermas bien!"),
    ("Auf Wiedersehen", "adiós (formal)", "goodbye", "frase", "Auf Wiedersehen, bis morgen!", "Adiós, ¡hasta mañana!"),
    ("Tschüss", "chau", "bye", "frase", "Tschüss, bis später!", "¡Chau, hasta luego!"),
    ("Bis bald", "hasta pronto", "see you soon", "frase", "Bis bald, ich melde mich.", "Hasta pronto, te escribo."),
    ("Bis später", "hasta luego", "see you later", "frase", "Bis später, ich muss jetzt los.", "Hasta luego, ya me tengo que ir."),
    ("Wie geht es dir?", "¿cómo estás?", "how are you?", "frase", "Hallo, wie geht es dir heute?", "Hola, ¿cómo estás hoy?"),
    ("Mir geht es gut", "estoy bien", "I'm fine", "frase", "Danke, mir geht es gut.", "Gracias, estoy bien."),
    ("Danke", "gracias", "thanks", "frase", "Danke für deine Hilfe!", "¡Gracias por tu ayuda!"),
    ("Bitte", "por favor / de nada", "please / you're welcome", "frase", "Kannst du mir bitte helfen?", "¿Me puedes ayudar, por favor?"),
    ("Entschuldigung", "disculpa / perdón", "excuse me / sorry", "frase", "Entschuldigung, wo ist der Bahnhof?", "Disculpe, ¿dónde está la estación?"),
    ("Ja", "sí", "yes", "partícula", "Ja, das stimmt.", "Sí, eso es correcto."),
    ("Nein", "no", "no", "partícula", "Nein, das ist nicht richtig.", "No, eso no es correcto."),
    ("vielleicht", "tal vez", "maybe", "adverbio", "Vielleicht komme ich morgen vorbei.", "Tal vez pase mañana."),
    ("der Name", "el nombre", "the name", "der", "Wie ist dein Name?", "¿Cuál es tu nombre?"),
    ("Ich heiße...", "me llamo...", "my name is...", "frase", "Ich heiße Facundo.", "Me llamo Facundo."),
    ("Wie heißt du?", "¿cómo te llamas?", "what's your name?", "frase", "Hallo, wie heißt du?", "Hola, ¿cómo te llamas?"),
    ("Ich komme aus...", "vengo de...", "I come from...", "frase", "Ich komme aus Argentinien.", "Vengo de Argentina."),
    ("Woher kommst du?", "¿de dónde eres?", "where are you from?", "frase", "Woher kommst du genau?", "¿De dónde eres exactamente?"),
    ("das Land", "el país", "the country", "das", "Deutschland ist ein schönes Land.", "Alemania es un país lindo."),
    ("die Sprache", "el idioma", "the language", "die", "Deutsch ist eine schwere Sprache.", "El alemán es un idioma difícil."),
    ("sprechen", "hablar", "to speak", "verbo", "Ich spreche ein bisschen Deutsch.", "Hablo un poco de alemán."),
    ("verstehen", "entender", "to understand", "verbo", "Ich verstehe dich nicht.", "No te entiendo."),
    ("Ich verstehe nicht", "no entiendo", "I don't understand", "frase", "Entschuldigung, ich verstehe nicht.", "Disculpa, no entiendo."),
    ("Können Sie das wiederholen?", "¿puede repetirlo?", "can you repeat that?", "frase", "Können Sie das bitte wiederholen?", "¿Puede repetirlo, por favor?"),
]

# ---------------------------------------------------------------------------
familia = cat("familia")
familia += [
    ("die Familie", "la familia", "the family", "die", "Meine Familie wohnt in Berlin.", "Mi familia vive en Berlín."),
    ("die Mutter", "la madre", "the mother", "die", "Meine Mutter kocht sehr gut.", "Mi madre cocina muy bien."),
    ("der Vater", "el padre", "the father", "der", "Mein Vater arbeitet viel.", "Mi padre trabaja mucho."),
    ("die Eltern", "los padres", "the parents", "die", "Meine Eltern kommen mich besuchen.", "Mis padres vienen a visitarme."),
    ("das Kind", "el niño / la niña", "the child", "das", "Das Kind spielt im Park.", "El niño juega en el parque."),
    ("der Sohn", "el hijo", "the son", "der", "Ihr Sohn geht schon zur Schule.", "Su hijo ya va a la escuela."),
    ("die Tochter", "la hija", "the daughter", "die", "Seine Tochter ist zwei Jahre alt.", "Su hija tiene dos años."),
    ("der Bruder", "el hermano", "the brother", "der", "Mein Bruder lebt in München.", "Mi hermano vive en Múnich."),
    ("die Schwester", "la hermana", "the sister", "die", "Meine Schwester ruft mich oft an.", "Mi hermana me llama seguido."),
    ("die Geschwister", "los hermanos (conjunto)", "siblings", "die", "Ich habe zwei Geschwister.", "Tengo dos hermanos."),
    ("der Großvater", "el abuelo", "the grandfather", "der", "Mein Großvater erzählt gern Geschichten.", "A mi abuelo le gusta contar historias."),
    ("die Großmutter", "la abuela", "the grandmother", "die", "Meine Großmutter backt jeden Sonntag Kuchen.", "Mi abuela hornea torta todos los domingos."),
    ("der Onkel", "el tío", "the uncle", "der", "Mein Onkel wohnt in Hamburg.", "Mi tío vive en Hamburgo."),
    ("die Tante", "la tía", "the aunt", "die", "Meine Tante arbeitet als Ärztin.", "Mi tía trabaja como médica."),
    ("der Cousin", "el primo", "the cousin (m.)", "der", "Mein Cousin studiert in Köln.", "Mi primo estudia en Colonia."),
    ("die Cousine", "la prima", "the cousin (f.)", "die", "Meine Cousine besucht mich am Wochenende.", "Mi prima me visita el fin de semana."),
    ("der Mann", "el hombre / esposo", "the man / husband", "der", "Der Mann dort ist mein Nachbar.", "Ese hombre de ahí es mi vecino."),
    ("die Frau", "la mujer / esposa", "the woman / wife", "die", "Die Frau arbeitet im Büro.", "La mujer trabaja en la oficina."),
    ("der Freund", "el amigo / novio", "the friend / boyfriend", "der", "Mein Freund hilft mir beim Umzug.", "Mi amigo me ayuda con la mudanza."),
    ("die Freundin", "la amiga / novia", "the friend / girlfriend", "die", "Meine Freundin kommt aus Spanien.", "Mi amiga es de España."),
    ("verheiratet", "casado / casada", "married", "adjetivo", "Bist du verheiratet?", "¿Estás casado/a?"),
    ("ledig", "soltero / soltera", "single", "adjetivo", "Ich bin noch ledig.", "Todavía estoy soltero/a."),
    ("das Baby", "el bebé", "the baby", "das", "Das Baby schläft gerade.", "El bebé está durmiendo."),
    ("die Verwandten", "los parientes", "the relatives", "die", "Alle Verwandten kommen zum Fest.", "Vienen todos los parientes a la fiesta."),
]

# ---------------------------------------------------------------------------
numeros = cat("números y cantidades")
numeros += [
    ("null", "cero", "zero", "número", "Die Nummer beginnt mit null.", "El número empieza con cero."),
    ("eins", "uno", "one", "número", "Ich habe nur eins.", "Tengo solo uno."),
    ("zwei", "dos", "two", "número", "Ich möchte zwei Kaffee, bitte.", "Quiero dos cafés, por favor."),
    ("drei", "tres", "three", "número", "Wir sind zu dritt.", "Somos tres."),
    ("vier", "cuatro", "four", "número", "Der Tisch hat vier Stühle.", "La mesa tiene cuatro sillas."),
    ("fünf", "cinco", "five", "número", "Ich warte seit fünf Minuten.", "Espero desde hace cinco minutos."),
    ("sechs", "seis", "six", "número", "Der Bus kommt um sechs Uhr.", "El colectivo llega a las seis."),
    ("sieben", "siete", "seven", "número", "Die Woche hat sieben Tage.", "La semana tiene siete días."),
    ("acht", "ocho", "eight", "número", "Ich stehe um acht Uhr auf.", "Me levanto a las ocho."),
    ("neun", "nueve", "nine", "número", "Der Laden öffnet um neun.", "El local abre a las nueve."),
    ("zehn", "diez", "ten", "número", "Das kostet zehn Euro.", "Eso cuesta diez euros."),
    ("elf", "once", "eleven", "número", "Wir treffen uns um elf.", "Nos encontramos a las once."),
    ("zwölf", "doce", "twelve", "número", "Ein Jahr hat zwölf Monate.", "Un año tiene doce meses."),
    ("dreizehn", "trece", "thirteen", "número", "Sie ist dreizehn Jahre alt.", "Ella tiene trece años."),
    ("vierzehn", "catorce", "fourteen", "número", "In vierzehn Tagen bin ich zurück.", "En catorce días vuelvo."),
    ("fünfzehn", "quince", "fifteen", "número", "Es dauert fünfzehn Minuten.", "Tarda quince minutos."),
    ("sechzehn", "dieciséis", "sixteen", "número", "Er wird bald sechzehn.", "Pronto cumple dieciséis."),
    ("siebzehn", "diecisiete", "seventeen", "número", "Sie hat siebzehn Nachrichten.", "Tiene diecisiete mensajes."),
    ("achtzehn", "dieciocho", "eighteen", "número", "Mit achtzehn darf man wählen.", "A los dieciocho se puede votar."),
    ("neunzehn", "diecinueve", "nineteen", "número", "Der Zug hat neunzehn Minuten Verspätung.", "El tren lleva diecinueve minutos de retraso."),
    ("zwanzig", "veinte", "twenty", "número", "Das Zimmer kostet zwanzig Euro pro Nacht.", "La habitación cuesta veinte euros por noche."),
    ("dreißig", "treinta", "thirty", "número", "Ich bin dreißig Jahre alt.", "Tengo treinta años."),
    ("vierzig", "cuarenta", "forty", "número", "Er arbeitet vierzig Stunden pro Woche.", "Él trabaja cuarenta horas por semana."),
    ("fünfzig", "cincuenta", "fifty", "número", "Das Ticket kostet fünfzig Euro.", "El pasaje cuesta cincuenta euros."),
    ("sechzig", "sesenta", "sixty", "número", "Eine Stunde hat sechzig Minuten.", "Una hora tiene sesenta minutos."),
    ("siebzig", "setenta", "seventy", "número", "Meine Oma wird siebzig.", "Mi abuela cumple setenta."),
    ("achtzig", "ochenta", "eighty", "número", "Der Ort liegt achtzig Kilometer entfernt.", "El lugar queda a ochenta kilómetros."),
    ("neunzig", "noventa", "ninety", "número", "Das Auto fährt neunzig Kilometer pro Stunde.", "El auto va a noventa kilómetros por hora."),
    ("hundert", "cien", "hundred", "número", "Das Zimmer ist hundert Quadratmeter groß.", "La habitación tiene cien metros cuadrados."),
    ("tausend", "mil", "thousand", "número", "Die Stadt hat tausend Einwohner.", "La ciudad tiene mil habitantes."),
    ("viel", "mucho", "a lot / much", "adverbio", "Ich habe heute viel zu tun.", "Hoy tengo mucho para hacer."),
    ("wenig", "poco", "little / few", "adverbio", "Ich habe wenig Zeit.", "Tengo poco tiempo."),
    ("alle", "todos", "all / everyone", "partícula", "Alle sind schon da.", "Todos ya están acá."),
    ("nichts", "nada", "nothing", "partícula", "Ich habe nichts gegessen.", "No comí nada."),
]

# ---------------------------------------------------------------------------
tiempo = cat("días, meses y hora")
tiempo += [
    ("Montag", "lunes", "Monday", "der", "Am Montag fange ich meinen neuen Job an.", "El lunes empiezo mi nuevo trabajo."),
    ("Dienstag", "martes", "Tuesday", "der", "Der Termin ist am Dienstag.", "La cita es el martes."),
    ("Mittwoch", "miércoles", "Wednesday", "der", "Mittwoch ist mein freier Tag.", "El miércoles es mi día libre."),
    ("Donnerstag", "jueves", "Thursday", "der", "Wir treffen uns Donnerstag.", "Nos encontramos el jueves."),
    ("Freitag", "viernes", "Friday", "der", "Endlich ist Freitag!", "¡Por fin es viernes!"),
    ("Samstag", "sábado", "Saturday", "der", "Am Samstag gehe ich einkaufen.", "El sábado voy de compras."),
    ("Sonntag", "domingo", "Sunday", "der", "Sonntags schlafe ich lange.", "Los domingos duermo hasta tarde."),
    ("Januar", "enero", "January", "der", "Im Januar ist es sehr kalt.", "En enero hace mucho frío."),
    ("Februar", "febrero", "February", "der", "Der kürzeste Monat ist Februar.", "El mes más corto es febrero."),
    ("März", "marzo", "March", "der", "Im März beginnt der Frühling.", "En marzo empieza la primavera."),
    ("April", "abril", "April", "der", "Im April regnet es oft.", "En abril llueve seguido."),
    ("Mai", "mayo", "May", "der", "Im Mai blühen die Blumen.", "En mayo florecen las flores."),
    ("Juni", "junio", "June", "der", "Im Juni fängt der Sommer an.", "En junio empieza el verano."),
    ("Juli", "julio", "July", "der", "Im Juli sind die Ferien.", "En julio son las vacaciones."),
    ("August", "agosto", "August", "der", "Im August ist es sehr heiß.", "En agosto hace mucho calor."),
    ("September", "septiembre", "September", "der", "Im September beginnt die Schule wieder.", "En septiembre empieza la escuela otra vez."),
    ("Oktober", "octubre", "October", "der", "Im Oktober wird es kühler.", "En octubre empieza a refrescar."),
    ("November", "noviembre", "November", "der", "Im November ist es oft grau.", "En noviembre suele estar nublado."),
    ("Dezember", "diciembre", "December", "der", "Im Dezember feiern wir Weihnachten.", "En diciembre festejamos Navidad."),
    ("die Uhrzeit", "la hora (del reloj)", "the time", "die", "Kannst du mir die Uhrzeit sagen?", "¿Me puedes decir la hora?"),
    ("die Stunde", "la hora (duración)", "the hour", "die", "Die Fahrt dauert eine Stunde.", "El viaje dura una hora."),
    ("die Minute", "el minuto", "the minute", "die", "Ich komme in fünf Minuten.", "Llego en cinco minutos."),
    ("heute", "hoy", "today", "adverbio", "Was machst du heute?", "¿Qué haces hoy?"),
    ("morgen", "mañana", "tomorrow", "adverbio", "Bis morgen!", "¡Hasta mañana!"),
    ("gestern", "ayer", "yesterday", "adverbio", "Gestern habe ich Deutsch gelernt.", "Ayer estudié alemán."),
    ("die Woche", "la semana", "the week", "die", "Nächste Woche fahre ich nach Berlin.", "La semana que viene voy a Berlín."),
    ("das Jahr", "el año", "the year", "das", "Dieses Jahr lerne ich Deutsch.", "Este año aprendo alemán."),
    ("der Monat", "el mes", "the month", "der", "Ich bin seit einem Monat hier.", "Estoy acá desde hace un mes."),
    ("der Tag", "el día", "the day", "der", "Ich hatte einen guten Tag.", "Tuve un buen día."),
    ("jetzt", "ahora", "now", "adverbio", "Ich muss jetzt gehen.", "Ahora me tengo que ir."),
    ("später", "después / más tarde", "later", "adverbio", "Wir reden später darüber.", "Hablamos de eso después."),
    ("Wie spät ist es?", "¿qué hora es?", "what time is it?", "frase", "Entschuldigung, wie spät ist es?", "Disculpa, ¿qué hora es?"),
]

# ---------------------------------------------------------------------------
comida = cat("comida y bebida")
comida += [
    ("das Brot", "el pan", "the bread", "das", "Ich kaufe frisches Brot beim Bäcker.", "Compro pan fresco en la panadería."),
    ("das Wasser", "el agua", "the water", "das", "Ein Glas Wasser, bitte.", "Un vaso de agua, por favor."),
    ("der Kaffee", "el café", "the coffee", "der", "Ich trinke jeden Morgen Kaffee.", "Tomo café todas las mañanas."),
    ("der Tee", "el té", "the tea", "der", "Möchtest du Tee oder Kaffee?", "¿Querés té o café?"),
    ("die Milch", "la leche", "the milk", "die", "Ich brauche noch Milch für den Kaffee.", "Todavía necesito leche para el café."),
    ("der Saft", "el jugo", "the juice", "der", "Der Orangensaft ist sehr lecker.", "El jugo de naranja está muy rico."),
    ("der Wein", "el vino", "the wine", "der", "Wir trinken einen Wein zum Essen.", "Tomamos un vino con la comida."),
    ("das Bier", "la cerveza", "the beer", "das", "In Deutschland trinkt man viel Bier.", "En Alemania se toma mucha cerveza."),
    ("der Zucker", "el azúcar", "the sugar", "der", "Ich nehme keinen Zucker im Kaffee.", "No le pongo azúcar al café."),
    ("das Salz", "la sal", "the salt", "das", "Kannst du mir das Salz geben?", "¿Me pasás la sal?"),
    ("der Käse", "el queso", "the cheese", "der", "Ich mag deutschen Käse sehr.", "Me gusta mucho el queso alemán."),
    ("die Butter", "la manteca", "the butter", "die", "Das Brot mit Butter ist lecker.", "El pan con manteca está rico."),
    ("das Ei", "el huevo", "the egg", "das", "Zum Frühstück esse ich ein Ei.", "En el desayuno como un huevo."),
    ("das Obst", "la fruta", "the fruit", "das", "Ich esse gern frisches Obst.", "Me gusta comer fruta fresca."),
    ("das Gemüse", "las verduras", "the vegetables", "das", "Gemüse ist gesund.", "Las verduras son saludables."),
    ("der Apfel", "la manzana", "the apple", "der", "Ein Apfel am Tag ist gesund.", "Una manzana por día es saludable."),
    ("die Banane", "la banana", "the banana", "die", "Die Banane ist noch nicht reif.", "La banana todavía no está madura."),
    ("die Kartoffel", "la papa", "the potato", "die", "Kartoffeln sind in Deutschland sehr beliebt.", "Las papas son muy populares en Alemania."),
    ("die Tomate", "el tomate", "the tomato", "die", "Der Salat hat viele Tomaten.", "La ensalada tiene muchos tomates."),
    ("das Fleisch", "la carne", "the meat", "das", "Ich esse selten Fleisch.", "Como carne pocas veces."),
    ("der Fisch", "el pescado", "the fish", "der", "Freitags essen wir oft Fisch.", "Los viernes comemos pescado seguido."),
    ("das Hähnchen", "el pollo", "the chicken", "das", "Das Hähnchen schmeckt sehr gut.", "El pollo está muy rico."),
    ("die Suppe", "la sopa", "the soup", "die", "Im Winter esse ich gern Suppe.", "En invierno me gusta comer sopa."),
    ("der Reis", "el arroz", "the rice", "der", "Reis passt gut zum Gemüse.", "El arroz combina bien con las verduras."),
    ("die Nudeln", "los fideos", "the noodles / pasta", "die", "Die Kinder lieben Nudeln.", "A los chicos les encantan los fideos."),
    ("der Kuchen", "la torta", "the cake", "der", "Zum Geburtstag gibt es Kuchen.", "Para el cumpleaños hay torta."),
    ("das Frühstück", "el desayuno", "the breakfast", "das", "Das Frühstück ist die wichtigste Mahlzeit.", "El desayuno es la comida más importante."),
    ("das Mittagessen", "el almuerzo", "the lunch", "das", "Wir machen das Mittagessen um zwölf.", "Almorzamos a las doce."),
    ("das Abendessen", "la cena", "the dinner", "das", "Das Abendessen ist fertig.", "La cena está lista."),
    ("der Hunger", "el hambre", "hunger", "der", "Ich habe großen Hunger.", "Tengo mucha hambre."),
    ("der Durst", "la sed", "thirst", "der", "Nach dem Sport habe ich Durst.", "Después de hacer deporte tengo sed."),
    ("essen", "comer", "to eat", "verbo", "Wir essen zusammen zu Mittag.", "Almorzamos juntos."),
    ("trinken", "beber / tomar", "to drink", "verbo", "Trink genug Wasser!", "¡Tomá suficiente agua!"),
    ("bestellen", "pedir (en un restaurante)", "to order", "verbo", "Was möchten Sie bestellen?", "¿Qué desea pedir?"),
    ("bezahlen", "pagar", "to pay", "verbo", "Kann ich bitte bezahlen?", "¿Puedo pagar, por favor?"),
    ("lecker", "rico / sabroso", "tasty", "adjetivo", "Das Essen ist sehr lecker.", "La comida está muy rica."),
    ("die Speisekarte", "el menú", "the menu", "die", "Können wir die Speisekarte haben?", "¿Nos puede traer el menú?"),
    ("das Restaurant", "el restaurante", "the restaurant", "das", "Wir gehen heute ins Restaurant.", "Hoy vamos al restaurante."),
    ("Ich möchte...", "quisiera...", "I would like...", "frase", "Ich möchte einen Kaffee, bitte.", "Quisiera un café, por favor."),
    ("Die Rechnung, bitte", "la cuenta, por favor", "the bill, please", "frase", "Entschuldigung, die Rechnung, bitte.", "Disculpe, la cuenta, por favor."),
    ("Guten Appetit!", "¡buen provecho!", "enjoy your meal!", "frase", "Guten Appetit! Lass es dir schmecken.", "¡Buen provecho! Que lo disfrutes."),
    ("süß", "dulce", "sweet", "adjetivo", "Der Kuchen ist sehr süß.", "La torta es muy dulce."),
    ("sauer", "ácido / agrio", "sour", "adjetivo", "Die Zitrone ist sehr sauer.", "El limón es muy ácido."),
]

# ---------------------------------------------------------------------------
casa = cat("casa y hogar")
casa += [
    ("das Haus", "la casa", "the house", "das", "Wir wohnen in einem kleinen Haus.", "Vivimos en una casa chica."),
    ("die Wohnung", "el departamento", "the apartment", "die", "Meine Wohnung hat zwei Zimmer.", "Mi departamento tiene dos ambientes."),
    ("das Zimmer", "la habitación", "the room", "das", "Das Zimmer ist sehr hell.", "La habitación es muy luminosa."),
    ("das Schlafzimmer", "el dormitorio", "the bedroom", "das", "Mein Schlafzimmer ist klein.", "Mi dormitorio es chico."),
    ("das Wohnzimmer", "la sala de estar", "the living room", "das", "Wir sitzen im Wohnzimmer.", "Estamos sentados en la sala."),
    ("die Küche", "la cocina", "the kitchen", "die", "Die Küche ist neu renoviert.", "La cocina está recién renovada."),
    ("das Badezimmer", "el baño", "the bathroom", "das", "Das Badezimmer ist im Flur.", "El baño está en el pasillo."),
    ("die Toilette", "el inodoro / baño", "the toilet", "die", "Wo ist die Toilette, bitte?", "¿Dónde está el baño, por favor?"),
    ("der Balkon", "el balcón", "the balcony", "der", "Wir frühstücken auf dem Balkon.", "Desayunamos en el balcón."),
    ("der Garten", "el jardín", "the garden", "der", "Der Garten hat viele Blumen.", "El jardín tiene muchas flores."),
    ("die Tür", "la puerta", "the door", "die", "Kannst du die Tür schließen?", "¿Podés cerrar la puerta?"),
    ("das Fenster", "la ventana", "the window", "das", "Mach bitte das Fenster auf.", "Abrí la ventana, por favor."),
    ("der Tisch", "la mesa", "the table", "der", "Das Essen steht auf dem Tisch.", "La comida está sobre la mesa."),
    ("der Stuhl", "la silla", "the chair", "der", "Nimm dir einen Stuhl.", "Agarrá una silla."),
    ("das Bett", "la cama", "the bed", "das", "Ich gehe früh ins Bett.", "Me voy a la cama temprano."),
    ("der Schrank", "el armario", "the closet / cupboard", "der", "Meine Kleidung ist im Schrank.", "Mi ropa está en el armario."),
    ("die Lampe", "la lámpara", "the lamp", "die", "Mach bitte die Lampe an.", "Prendé la lámpara, por favor."),
    ("der Fernseher", "el televisor", "the TV", "der", "Der Fernseher ist kaputt.", "El televisor está roto."),
    ("das Sofa", "el sillón / sofá", "the sofa", "das", "Wir sitzen auf dem Sofa.", "Estamos sentados en el sofá."),
    ("der Kühlschrank", "la heladera", "the fridge", "der", "Im Kühlschrank ist nichts mehr.", "En la heladera ya no queda nada."),
    ("die Miete", "el alquiler", "the rent", "die", "Die Miete ist diesen Monat gestiegen.", "El alquiler subió este mes."),
    ("wohnen", "vivir (residir)", "to live (reside)", "verbo", "Ich wohne seit einem Jahr in Berlin.", "Vivo en Berlín desde hace un año."),
    ("putzen", "limpiar", "to clean", "verbo", "Samstags putze ich die Wohnung.", "Los sábados limpio el departamento."),
    ("kochen", "cocinar", "to cook", "verbo", "Er kocht gern für Freunde.", "A él le gusta cocinar para sus amigos."),
    ("aufräumen", "ordenar", "to tidy up", "verbo", "Ich muss noch mein Zimmer aufräumen.", "Todavía tengo que ordenar mi cuarto."),
    ("der Schlüssel", "la llave", "the key", "der", "Ich habe meinen Schlüssel verloren.", "Perdí mi llave."),
    ("sauber", "limpio", "clean", "adjetivo", "Die Küche ist jetzt sauber.", "La cocina ahora está limpia."),
    ("schmutzig", "sucio", "dirty", "adjetivo", "Meine Schuhe sind schmutzig.", "Mis zapatillas están sucias."),
    ("groß", "grande", "big", "adjetivo", "Die Wohnung ist sehr groß.", "El departamento es muy grande."),
    ("klein", "chico / pequeño", "small", "adjetivo", "Das Zimmer ist etwas klein.", "La habitación es un poco chica."),
]

# ---------------------------------------------------------------------------
ciudad = cat("ciudad y transporte")
ciudad += [
    ("die Stadt", "la ciudad", "the city", "die", "Berlin ist eine große Stadt.", "Berlín es una ciudad grande."),
    ("die Straße", "la calle", "the street", "die", "Ich wohne in dieser Straße.", "Vivo en esta calle."),
    ("der Bahnhof", "la estación de tren", "the train station", "der", "Der Bahnhof ist fünf Minuten von hier.", "La estación queda a cinco minutos de acá."),
    ("der Flughafen", "el aeropuerto", "the airport", "der", "Wir fahren zum Flughafen.", "Vamos hacia el aeropuerto."),
    ("der Bus", "el colectivo / autobús", "the bus", "der", "Der Bus kommt in zehn Minuten.", "El colectivo llega en diez minutos."),
    ("die U-Bahn", "el metro", "the subway", "die", "Ich fahre mit der U-Bahn zur Arbeit.", "Voy al trabajo en metro."),
    ("die S-Bahn", "el tren urbano", "the commuter train", "die", "Die S-Bahn hält an jeder Station.", "El tren urbano para en cada estación."),
    ("das Auto", "el auto", "the car", "das", "Wir fahren mit dem Auto in den Urlaub.", "Vamos de vacaciones en auto."),
    ("das Fahrrad", "la bicicleta", "the bicycle", "das", "In Deutschland fahren viele Leute Fahrrad.", "En Alemania mucha gente anda en bicicleta."),
    ("das Taxi", "el taxi", "the taxi", "das", "Wir nehmen ein Taxi zum Hotel.", "Tomamos un taxi al hotel."),
    ("die Fahrkarte", "el boleto / pasaje", "the ticket", "die", "Ich brauche eine Fahrkarte für den Zug.", "Necesito un pasaje para el tren."),
    ("die Haltestelle", "la parada", "the stop", "die", "Die nächste Haltestelle ist meine.", "La próxima parada es la mía."),
    ("links", "izquierda", "left", "adverbio", "Gehen Sie hier links.", "Vaya para la izquierda acá."),
    ("rechts", "derecha", "right", "adverbio", "Das Geschäft ist rechts.", "El negocio está a la derecha."),
    ("geradeaus", "derecho / recto", "straight ahead", "adverbio", "Gehen Sie einfach geradeaus.", "Siga derecho nomás."),
    ("hier", "aquí / acá", "here", "adverbio", "Ich warte hier auf dich.", "Te espero acá."),
    ("dort", "allí / allá", "there", "adverbio", "Der Supermarkt ist dort.", "El supermercado está allá."),
    ("die Ampel", "el semáforo", "the traffic light", "die", "Warte, bis die Ampel grün ist.", "Esperá a que el semáforo esté verde."),
    ("die Brücke", "el puente", "the bridge", "die", "Wir gehen über die Brücke.", "Cruzamos el puente."),
    ("der Park", "el parque", "the park", "der", "Am Wochenende gehen wir in den Park.", "El fin de semana vamos al parque."),
    ("das Geschäft", "la tienda / negocio", "the shop", "das", "Das Geschäft schließt um acht.", "El negocio cierra a las ocho."),
    ("die Apotheke", "la farmacia", "the pharmacy", "die", "Die Apotheke ist gleich um die Ecke.", "La farmacia está a la vuelta."),
    ("die Bank", "el banco", "the bank", "die", "Ich muss zur Bank gehen.", "Tengo que ir al banco."),
    ("das Krankenhaus", "el hospital", "the hospital", "das", "Das Krankenhaus ist nicht weit.", "El hospital no queda lejos."),
    ("die Post", "el correo", "the post office", "die", "Ich schicke das Paket von der Post.", "Mando el paquete desde el correo."),
    ("die Kirche", "la iglesia", "the church", "die", "Die Kirche ist sehr alt.", "La iglesia es muy antigua."),
    ("die Schule", "la escuela", "the school", "die", "Die Kinder gehen zu Fuß zur Schule.", "Los chicos van caminando a la escuela."),
    ("fahren", "ir (en vehículo) / conducir", "to drive / to go (by vehicle)", "verbo", "Wir fahren morgen nach Köln.", "Mañana vamos a Colonia."),
    ("gehen", "ir / caminar", "to go / to walk", "verbo", "Ich gehe zu Fuß zur Arbeit.", "Voy caminando al trabajo."),
    ("Wo ist...?", "¿dónde está...?", "where is...?", "frase", "Entschuldigung, wo ist der Bahnhof?", "Disculpe, ¿dónde está la estación?"),
    ("Wie komme ich zu...?", "¿cómo llego a...?", "how do I get to...?", "frase", "Wie komme ich zum Hauptbahnhof?", "¿Cómo llego a la estación central?"),
]

# ---------------------------------------------------------------------------
compras = cat("compras")
compras += [
    ("der Supermarkt", "el supermercado", "the supermarket", "der", "Ich kaufe im Supermarkt ein.", "Compro en el supermercado."),
    ("das Geld", "el dinero", "the money", "das", "Ich habe nicht genug Geld dabei.", "No tengo suficiente plata encima."),
    ("der Preis", "el precio", "the price", "der", "Der Preis ist sehr hoch.", "El precio es muy alto."),
    ("billig", "barato", "cheap", "adjetivo", "Dieses Geschäft ist sehr billig.", "Este negocio es muy barato."),
    ("teuer", "caro", "expensive", "adjetivo", "Das ist mir zu teuer.", "Eso me resulta muy caro."),
    ("kaufen", "comprar", "to buy", "verbo", "Ich möchte ein Geschenk kaufen.", "Quiero comprar un regalo."),
    ("verkaufen", "vender", "to sell", "verbo", "Sie verkaufen frisches Obst.", "Venden fruta fresca."),
    ("die Kasse", "la caja (de pago)", "the checkout / cashier", "die", "Die Schlange an der Kasse ist lang.", "La fila en la caja es larga."),
    ("die Quittung", "el recibo / ticket", "the receipt", "die", "Kann ich bitte eine Quittung haben?", "¿Me puede dar un recibo, por favor?"),
    ("die Größe", "el talle", "the size", "die", "Welche Größe brauchen Sie?", "¿Qué talle necesita?"),
    ("die Farbe", "el color", "the color", "die", "Welche Farbe gefällt dir?", "¿Qué color te gusta?"),
    ("die Kleidung", "la ropa", "the clothing", "die", "Ich brauche neue Kleidung für den Winter.", "Necesito ropa nueva para el invierno."),
    ("das Hemd", "la camisa", "the shirt", "das", "Das Hemd passt dir gut.", "La camisa te queda bien."),
    ("die Hose", "el pantalón", "the pants", "die", "Diese Hose ist zu groß.", "Este pantalón me queda grande."),
    ("das Kleid", "el vestido", "the dress", "das", "Sie trägt ein blaues Kleid.", "Ella lleva puesto un vestido azul."),
    ("die Schuhe", "los zapatos", "the shoes", "die", "Meine Schuhe sind kaputt.", "Mis zapatos están rotos."),
    ("die Jacke", "la campera", "the jacket", "die", "Zieh deine Jacke an, es ist kalt.", "Ponete la campera, hace frío."),
    ("Was kostet das?", "¿cuánto cuesta esto?", "how much does this cost?", "frase", "Entschuldigung, was kostet das?", "Disculpe, ¿cuánto cuesta esto?"),
    ("Das ist zu teuer", "eso es muy caro", "that's too expensive", "frase", "Danke, aber das ist mir zu teuer.", "Gracias, pero eso me resulta muy caro."),
    ("in bar", "en efectivo", "in cash", "frase", "Ich bezahle in bar.", "Pago en efectivo."),
    ("mit Karte", "con tarjeta", "with card", "frase", "Kann ich mit Karte bezahlen?", "¿Puedo pagar con tarjeta?"),
    ("der Rabatt", "el descuento", "the discount", "der", "Es gibt zehn Prozent Rabatt.", "Hay un diez por ciento de descuento."),
    ("die Öffnungszeiten", "el horario de atención", "the opening hours", "die", "Wie sind die Öffnungszeiten?", "¿Cuál es el horario de atención?"),
    ("geschlossen", "cerrado", "closed", "adjetivo", "Der Laden ist heute geschlossen.", "El local está cerrado hoy."),
    ("offen", "abierto", "open", "adjetivo", "Ist die Apotheke noch offen?", "¿La farmacia sigue abierta?"),
    ("groß", "grande (talle)", "large (size)", "adjetivo", "Haben Sie das in Größe groß?", "¿Lo tiene en talle grande?"),
]

# ---------------------------------------------------------------------------
cuerpo = cat("cuerpo y salud")
cuerpo += [
    ("der Kopf", "la cabeza", "the head", "der", "Mir tut der Kopf weh.", "Me duele la cabeza."),
    ("das Auge", "el ojo", "the eye", "das", "Sie hat grüne Augen.", "Ella tiene ojos verdes."),
    ("die Nase", "la nariz", "the nose", "die", "Meine Nase ist verstopft.", "Tengo la nariz tapada."),
    ("der Mund", "la boca", "the mouth", "der", "Öffnen Sie bitte den Mund.", "Abra la boca, por favor."),
    ("das Ohr", "la oreja / oído", "the ear", "das", "Ich habe Schmerzen im Ohr.", "Tengo dolor de oído."),
    ("der Arm", "el brazo", "the arm", "der", "Er hat sich den Arm gebrochen.", "Se rompió el brazo."),
    ("die Hand", "la mano", "the hand", "die", "Gib mir bitte deine Hand.", "Dame la mano, por favor."),
    ("das Bein", "la pierna", "the leg", "das", "Mein Bein tut weh.", "Me duele la pierna."),
    ("der Fuß", "el pie", "the foot", "der", "Ich habe kalte Füße.", "Tengo los pies fríos."),
    ("der Bauch", "la panza", "the belly / stomach", "der", "Mir tut der Bauch weh.", "Me duele la panza."),
    ("der Rücken", "la espalda", "the back", "der", "Mein Rücken tut weh vom Sitzen.", "Me duele la espalda de estar sentado."),
    ("krank", "enfermo", "sick", "adjetivo", "Ich bin heute krank.", "Hoy estoy enfermo."),
    ("gesund", "sano / saludable", "healthy", "adjetivo", "Gemüse ist sehr gesund.", "Las verduras son muy saludables."),
    ("der Arzt", "el médico", "the doctor (m.)", "der", "Ich habe einen Termin beim Arzt.", "Tengo turno con el médico."),
    ("die Ärztin", "la médica", "the doctor (f.)", "die", "Die Ärztin untersucht mich.", "La médica me examina."),
    ("das Krankenhaus", "el hospital", "the hospital", "das", "Sie arbeitet im Krankenhaus.", "Ella trabaja en el hospital."),
    ("die Tablette", "la pastilla", "the pill", "die", "Nimm diese Tablette gegen die Schmerzen.", "Tomá esta pastilla para el dolor."),
    ("die Schmerzen", "los dolores", "the pain", "die", "Ich habe starke Schmerzen.", "Tengo dolores fuertes."),
    ("die Kopfschmerzen", "el dolor de cabeza", "headache", "die", "Ich habe Kopfschmerzen seit heute Morgen.", "Tengo dolor de cabeza desde esta mañana."),
    ("Mir geht es nicht gut", "no me siento bien", "I don't feel well", "frase", "Entschuldigung, mir geht es nicht gut.", "Disculpa, no me siento bien."),
    ("Ich bin krank", "estoy enfermo", "I am sick", "frase", "Ich kann heute nicht kommen, ich bin krank.", "Hoy no puedo ir, estoy enfermo."),
    ("der Termin", "el turno / la cita", "the appointment", "der", "Ich habe morgen einen Termin.", "Mañana tengo un turno."),
    ("sich fühlen", "sentirse", "to feel", "verbo", "Wie fühlst du dich heute?", "¿Cómo te sentís hoy?"),
    ("die Erkältung", "el resfrío", "the cold (illness)", "die", "Ich habe eine Erkältung.", "Tengo un resfrío."),
    ("das Fieber", "la fiebre", "the fever", "das", "Er hat hohes Fieber.", "Él tiene mucha fiebre."),
    ("der Notfall", "la emergencia", "the emergency", "der", "Das ist ein Notfall!", "¡Esto es una emergencia!"),
    ("die Versicherung", "el seguro", "the insurance", "die", "Ich brauche eine Krankenversicherung.", "Necesito un seguro médico."),
    ("weh tun", "doler", "to hurt", "verbo", "Mein Hals tut weh.", "Me duele la garganta."),
]

# ---------------------------------------------------------------------------
trabajo = cat("trabajo y profesiones")
trabajo += [
    ("die Arbeit", "el trabajo", "the work / job", "die", "Meine Arbeit macht mir Spaß.", "Mi trabajo me gusta."),
    ("der Beruf", "la profesión", "the profession", "der", "Was ist dein Beruf?", "¿Cuál es tu profesión?"),
    ("arbeiten", "trabajar", "to work", "verbo", "Ich arbeite von Montag bis Freitag.", "Trabajo de lunes a viernes."),
    ("der Chef", "el jefe", "the boss (m.)", "der", "Mein Chef ist sehr nett.", "Mi jefe es muy amable."),
    ("die Chefin", "la jefa", "the boss (f.)", "die", "Die Chefin ist heute nicht im Büro.", "La jefa no está hoy en la oficina."),
    ("das Büro", "la oficina", "the office", "das", "Ich arbeite im Büro.", "Trabajo en la oficina."),
    ("der Kollege", "el colega (varón)", "the colleague (m.)", "der", "Mein Kollege hilft mir gern.", "A mi colega le gusta ayudarme."),
    ("die Kollegin", "la colega", "the colleague (f.)", "die", "Meine Kollegin ist aus Polen.", "Mi colega es de Polonia."),
    ("der Lehrer", "el profesor", "the teacher (m.)", "der", "Der Lehrer erklärt die Grammatik.", "El profesor explica la gramática."),
    ("die Lehrerin", "la profesora", "the teacher (f.)", "die", "Die Lehrerin ist sehr geduldig.", "La profesora es muy paciente."),
    ("der Verkäufer", "el vendedor", "the salesman", "der", "Der Verkäufer hilft mir bei der Wahl.", "El vendedor me ayuda a elegir."),
    ("die Verkäuferin", "la vendedora", "the saleswoman", "die", "Die Verkäuferin ist sehr freundlich.", "La vendedora es muy amable."),
    ("der Kellner", "el mozo", "the waiter", "der", "Der Kellner bringt die Speisekarte.", "El mozo trae el menú."),
    ("die Kellnerin", "la moza", "the waitress", "die", "Die Kellnerin ist sehr schnell.", "La moza es muy rápida."),
    ("der Student", "el estudiante", "the student (m.)", "der", "Er ist Student an der Universität.", "Él es estudiante universitario."),
    ("die Studentin", "la estudiante", "the student (f.)", "die", "Sie ist Studentin im ersten Jahr.", "Ella es estudiante de primer año."),
    ("das Gehalt", "el sueldo", "the salary", "das", "Das Gehalt wird am Monatsende bezahlt.", "El sueldo se paga a fin de mes."),
    ("die Firma", "la empresa", "the company", "die", "Ich arbeite für eine große Firma.", "Trabajo para una empresa grande."),
    ("die Erfahrung", "la experiencia", "the experience", "die", "Ich habe wenig Erfahrung in diesem Beruf.", "Tengo poca experiencia en esta profesión."),
    ("der Lebenslauf", "el currículum", "the resume / CV", "der", "Schick mir bitte deinen Lebenslauf.", "Mandame tu currículum, por favor."),
    ("das Vorstellungsgespräch", "la entrevista de trabajo", "the job interview", "das", "Morgen habe ich ein Vorstellungsgespräch.", "Mañana tengo una entrevista de trabajo."),
    ("die Pause", "el descanso / pausa", "the break", "die", "Wir machen jetzt eine Pause.", "Ahora hacemos una pausa."),
    ("der Feierabend", "el fin de la jornada laboral", "end of the workday", "der", "Endlich Feierabend!", "¡Por fin terminó el trabajo!"),
    ("arbeitslos", "desempleado", "unemployed", "adjetivo", "Er ist seit zwei Monaten arbeitslos.", "Él está desempleado desde hace dos meses."),
    ("verdienen", "ganar (dinero)", "to earn", "verbo", "Sie verdient gut in ihrem Job.", "Ella gana bien en su trabajo."),
    ("die Karriere", "la carrera (profesional)", "the career", "die", "Er macht schnell Karriere.", "Él está progresando rápido en su carrera."),
]

# ---------------------------------------------------------------------------
clima = cat("clima")
clima += [
    ("das Wetter", "el clima / tiempo", "the weather", "das", "Wie ist das Wetter heute?", "¿Cómo está el clima hoy?"),
    ("die Sonne", "el sol", "the sun", "die", "Die Sonne scheint heute.", "Hoy brilla el sol."),
    ("der Regen", "la lluvia", "the rain", "der", "Der Regen hört bald auf.", "La lluvia va a parar pronto."),
    ("der Schnee", "la nieve", "the snow", "der", "Der Schnee ist sehr schön.", "La nieve es muy linda."),
    ("der Wind", "el viento", "the wind", "der", "Heute weht ein starker Wind.", "Hoy sopla un viento fuerte."),
    ("die Wolke", "la nube", "the cloud", "die", "Es gibt viele Wolken am Himmel.", "Hay muchas nubes en el cielo."),
    ("warm", "cálido / templado", "warm", "adjetivo", "Heute ist es angenehm warm.", "Hoy hace un calor agradable."),
    ("kalt", "frío", "cold", "adjetivo", "Zieh dich warm an, es ist kalt.", "Abrigate, hace frío."),
    ("heiß", "caluroso", "hot", "adjetivo", "Im Sommer ist es hier sehr heiß.", "En verano acá hace mucho calor."),
    ("kühl", "fresco", "cool", "adjetivo", "Am Abend wird es kühl.", "A la noche refresca."),
    ("Es regnet", "está lloviendo", "it's raining", "frase", "Nimm einen Schirm mit, es regnet.", "Llevate un paraguas, está lloviendo."),
    ("Es schneit", "está nevando", "it's snowing", "frase", "Schau mal, es schneit!", "¡Mirá, está nevando!"),
    ("sonnig", "soleado", "sunny", "adjetivo", "Morgen wird es sonnig.", "Mañana va a estar soleado."),
    ("bewölkt", "nublado", "cloudy", "adjetivo", "Heute ist es bewölkt.", "Hoy está nublado."),
    ("der Himmel", "el cielo", "the sky", "der", "Der Himmel ist heute sehr blau.", "El cielo está muy azul hoy."),
    ("das Gewitter", "la tormenta", "the thunderstorm", "das", "Heute Nacht kommt ein Gewitter.", "Esta noche va a haber una tormenta."),
    ("der Frühling", "la primavera", "spring", "der", "Im Frühling werden die Tage länger.", "En primavera los días se hacen más largos."),
    ("der Sommer", "el verano", "summer", "der", "Der Sommer ist meine Lieblingsjahreszeit.", "El verano es mi estación favorita."),
    ("der Herbst", "el otoño", "autumn / fall", "der", "Im Herbst fallen die Blätter.", "En otoño caen las hojas."),
    ("der Winter", "el invierno", "winter", "der", "Der Winter in Deutschland ist lang.", "El invierno en Alemania es largo."),
]

# ---------------------------------------------------------------------------
verbos = cat("verbos básicos de alta frecuencia")
verbos += [
    ("sein", "ser / estar", "to be", "verbo", "Ich bin müde.", "Estoy cansado."),
    ("haben", "tener", "to have", "verbo", "Ich habe eine Frage.", "Tengo una pregunta."),
    ("machen", "hacer", "to do / to make", "verbo", "Was machst du gerade?", "¿Qué estás haciendo?"),
    ("gehen", "ir", "to go", "verbo", "Wir gehen jetzt nach Hause.", "Ahora nos vamos a casa."),
    ("kommen", "venir", "to come", "verbo", "Kommst du mit?", "¿Venís con nosotros?"),
    ("sagen", "decir", "to say", "verbo", "Was hast du gesagt?", "¿Qué dijiste?"),
    ("sehen", "ver", "to see", "verbo", "Ich sehe dich morgen.", "Te veo mañana."),
    ("wissen", "saber", "to know (a fact)", "verbo", "Ich weiß es nicht.", "No lo sé."),
    ("geben", "dar", "to give", "verbo", "Kannst du mir das geben?", "¿Me podés dar eso?"),
    ("nehmen", "tomar / agarrar", "to take", "verbo", "Ich nehme den Bus.", "Tomo el colectivo."),
    ("finden", "encontrar", "to find", "verbo", "Ich finde meinen Schlüssel nicht.", "No encuentro mi llave."),
    ("denken", "pensar", "to think", "verbo", "Was denkst du darüber?", "¿Qué pensás sobre eso?"),
    ("brauchen", "necesitar", "to need", "verbo", "Ich brauche mehr Zeit.", "Necesito más tiempo."),
    ("wollen", "querer", "to want", "verbo", "Ich will Deutsch lernen.", "Quiero aprender alemán."),
    ("können", "poder / saber (hacer algo)", "to be able to / can", "verbo", "Kannst du mir helfen?", "¿Podés ayudarme?"),
    ("müssen", "tener que / deber", "to have to / must", "verbo", "Ich muss jetzt gehen.", "Tengo que irme ahora."),
    ("dürfen", "tener permiso / poder", "to be allowed to", "verbo", "Darf ich hier rauchen?", "¿Puedo fumar acá?"),
    ("mögen", "gustar / querer (a alguien)", "to like", "verbo", "Ich mag dieses Lied.", "Me gusta esta canción."),
    ("sollen", "deber (obligación externa)", "should / to be supposed to", "verbo", "Ich soll früh aufstehen.", "Se supone que debo levantarme temprano."),
    ("lernen", "aprender / estudiar", "to learn", "verbo", "Ich lerne jeden Tag Deutsch.", "Estudio alemán todos los días."),
    ("spielen", "jugar", "to play", "verbo", "Die Kinder spielen im Garten.", "Los chicos juegan en el jardín."),
    ("helfen", "ayudar", "to help", "verbo", "Kannst du mir bitte helfen?", "¿Me podés ayudar, por favor?"),
    ("warten", "esperar", "to wait", "verbo", "Ich warte auf den Bus.", "Estoy esperando el colectivo."),
    ("lesen", "leer", "to read", "verbo", "Ich lese gern Bücher.", "Me gusta leer libros."),
    ("schreiben", "escribir", "to write", "verbo", "Kannst du mir eine Nachricht schreiben?", "¿Me podés escribir un mensaje?"),
    ("hören", "escuchar / oír", "to hear / to listen", "verbo", "Ich höre gern Musik.", "Me gusta escuchar música."),
    ("schlafen", "dormir", "to sleep", "verbo", "Ich schlafe früh ein.", "Me duermo temprano."),
    ("anfangen", "empezar", "to start", "verbo", "Wann fängt der Film an?", "¿Cuándo empieza la película?"),
    ("aufhören", "terminar / dejar de", "to stop", "verbo", "Hör bitte auf zu reden.", "Dejá de hablar, por favor."),
    ("lieben", "amar", "to love", "verbo", "Ich liebe meine Familie.", "Amo a mi familia."),
    ("leben", "vivir (existir)", "to live (exist)", "verbo", "Ich lebe gern in Deutschland.", "Me gusta vivir en Alemania."),
    ("bringen", "traer / llevar", "to bring", "verbo", "Kannst du mir Wasser bringen?", "¿Me podés traer agua?"),
]

# ---------------------------------------------------------------------------
frases = cat("frases útiles del día a día")
frases += [
    ("Wie viel kostet das?", "¿cuánto cuesta esto?", "how much is this?", "frase", "Wie viel kostet das T-Shirt?", "¿Cuánto cuesta esta remera?"),
    ("Wo ist die Toilette?", "¿dónde está el baño?", "where is the bathroom?", "frase", "Entschuldigung, wo ist die Toilette?", "Disculpe, ¿dónde está el baño?"),
    ("Ich habe eine Frage", "tengo una pregunta", "I have a question", "frase", "Entschuldigung, ich habe eine Frage.", "Disculpe, tengo una pregunta."),
    ("Können Sie mir helfen?", "¿puede ayudarme?", "can you help me?", "frase", "Entschuldigung, können Sie mir helfen?", "Disculpe, ¿puede ayudarme?"),
    ("Ich brauche Hilfe", "necesito ayuda", "I need help", "frase", "Ich brauche Hilfe, bitte.", "Necesito ayuda, por favor."),
    ("Sprechen Sie Englisch?", "¿habla inglés?", "do you speak English?", "frase", "Entschuldigung, sprechen Sie Englisch?", "Disculpe, ¿habla inglés?"),
    ("Ich spreche kein Deutsch", "no hablo alemán", "I don't speak German", "frase", "Tut mir leid, ich spreche kein Deutsch.", "Lo siento, no hablo alemán."),
    ("Langsamer, bitte", "más despacio, por favor", "slower, please", "frase", "Können Sie langsamer sprechen, bitte?", "¿Puede hablar más despacio, por favor?"),
    ("Wie bitte?", "¿cómo dice? / ¿perdón?", "excuse me? / pardon?", "frase", "Wie bitte? Ich habe das nicht verstanden.", "¿Cómo dice? No entendí eso."),
    ("Kein Problem", "no hay problema", "no problem", "frase", "Kein Problem, das mache ich gern.", "No hay problema, lo hago con gusto."),
    ("Es tut mir leid", "lo siento", "I'm sorry", "frase", "Es tut mir leid, ich bin spät dran.", "Lo siento, estoy llegando tarde."),
    ("Alles klar", "todo bien / entendido", "all clear / got it", "frase", "Alles klar, bis morgen!", "Entendido, ¡hasta mañana!"),
    ("Genau", "exacto", "exactly", "frase", "Genau, das habe ich auch gedacht.", "Exacto, eso mismo pensé yo."),
    ("Natürlich", "por supuesto", "of course", "frase", "Natürlich kann ich dir helfen.", "Por supuesto que te puedo ayudar."),
    ("Ich weiß nicht", "no sé", "I don't know", "frase", "Ich weiß nicht, wo mein Schlüssel ist.", "No sé dónde está mi llave."),
    ("Ich bin fertig", "ya terminé / estoy listo", "I'm done / I'm ready", "frase", "Ich bin fertig, wir können gehen.", "Ya terminé, podemos irnos."),
    ("Einen Moment, bitte", "un momento, por favor", "one moment, please", "frase", "Einen Moment, bitte, ich komme gleich.", "Un momento, por favor, ya vengo."),
    ("Herzlichen Glückwunsch", "felicitaciones", "congratulations", "frase", "Herzlichen Glückwunsch zum Geburtstag!", "¡Felicitaciones por tu cumpleaños!"),
    ("Viel Glück", "buena suerte", "good luck", "frase", "Viel Glück bei deinem Termin!", "¡Buena suerte con tu turno!"),
    ("Gute Reise", "buen viaje", "have a good trip", "frase", "Gute Reise und pass auf dich auf!", "¡Buen viaje y cuidate!"),
    ("Willkommen", "bienvenido", "welcome", "frase", "Willkommen in Deutschland!", "¡Bienvenido a Alemania!"),
    ("Prost!", "¡salud!", "cheers!", "frase", "Prost! Auf die Freundschaft.", "¡Salud! Por la amistad."),
    ("Schade", "qué lástima", "what a shame", "frase", "Schade, dass du nicht kommen kannst.", "Qué lástima que no puedas venir."),
    ("Alles Gute", "que te vaya bien / todo lo mejor", "all the best", "frase", "Alles Gute für die Zukunft!", "¡Todo lo mejor para el futuro!"),
    ("Bis dann", "hasta entonces / nos vemos", "see you then", "frase", "Bis dann, wir sehen uns am Montag.", "Nos vemos, hasta el lunes."),
    ("Mach's gut", "cuidate / que te vaya bien", "take care", "frase", "Mach's gut und bis bald!", "¡Cuidate y hasta pronto!"),
    ("Pass auf!", "¡ten cuidado!", "watch out!", "frase", "Pass auf, das Auto kommt!", "¡Cuidado, viene el auto!"),
    ("Vorsicht!", "¡cuidado!", "caution!", "frase", "Vorsicht, die Straße ist rutschig!", "¡Cuidado, la calle está resbaladiza!"),
    ("Ruf mich an", "llamame", "call me", "frase", "Ruf mich an, wenn du ankommst.", "Llamame cuando llegues."),
    ("Schreib mir", "escribime", "text me / write to me", "frase", "Schreib mir, wenn du Zeit hast.", "Escribime cuando tengas tiempo."),
]

# ---------------------------------------------------------------------------

KIND_TO_TIPO_ARTICULO = {
    "der": ("sustantivo", "der"),
    "die": ("sustantivo", "die"),
    "das": ("sustantivo", "das"),
    "verbo": ("verbo", ""),
    "frase": ("frase", ""),
    "adjetivo": ("adjetivo", ""),
    "adverbio": ("adverbio", ""),
    "partícula": ("partícula", ""),
    "número": ("número", ""),
}

def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "entry"

def build_vocab(categories, nivel="A1", id_prefix=""):
    """Convierte un dict {categoria: [tuplas]} al formato interno de la app.
    id_prefix evita colisiones de id entre niveles distintos (ej. "a2-")
    aunque coincida la misma palabra alemana en dos niveles."""
    entries = []
    seen_ids = {}
    for categoria, rows in categories.items():
        for row in rows:
            de, es, en, kind, ejemplo_de, ejemplo_es = row
            tipo, articulo = KIND_TO_TIPO_ARTICULO[kind]
            base_id = id_prefix + slugify(de)
            seen_ids[base_id] = seen_ids.get(base_id, 0) + 1
            entry_id = base_id if seen_ids[base_id] == 1 else f"{base_id}-{seen_ids[base_id]}"
            entries.append({
                "id": entry_id,
                "de": de,
                "es": es,
                "en": en,
                "categoria": categoria,
                "nivel": nivel,
                "ejemplo_de": ejemplo_de,
                "ejemplo_es": ejemplo_es,
                "tipo": tipo,
                "articulo": articulo,
            })
    return entries

if __name__ == "__main__":
    vocab = build_vocab(CATEGORIES, nivel="A1")
    out_path = "/root/german-app/data/vocab-a1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Generadas {len(vocab)} entradas en {out_path}")
    by_cat = {}
    for e in vocab:
        by_cat[e["categoria"]] = by_cat.get(e["categoria"], 0) + 1
    for c, n in by_cat.items():
        print(f"  - {c}: {n}")
