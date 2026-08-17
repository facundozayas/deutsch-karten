#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera data/vocab-a2.json — vocabulario A2 del Goethe-Zertifikat A2,
con foco extra en trámites/vida cotidiana en Alemania (muy relevante
para alguien que ya vive ahí). Reutiliza los helpers de gen_vocab.py.

Formato de cada tupla: igual que en gen_vocab.py (de, es, en, kind, ejemplo_de, ejemplo_es)
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from gen_vocab import KIND_TO_TIPO_ARTICULO, slugify, build_vocab  # noqa: E402

CATEGORIES_A2 = {}

def cat(name):
    CATEGORIES_A2[name] = []
    return CATEGORIES_A2[name]

# ---------------------------------------------------------------------------
rutinas = cat("rutinas y actividades diarias")
rutinas += [
    ("aufstehen", "levantarse", "to get up", "verbo", "Ich stehe jeden Tag um sieben Uhr auf.", "Me levanto todos los días a las siete."),
    ("sich duschen", "ducharse", "to shower", "verbo", "Ich dusche mich jeden Morgen.", "Me ducho todas las mañanas."),
    ("sich anziehen", "vestirse", "to get dressed", "verbo", "Zieh dich schnell an, wir sind spät dran.", "Vestite rápido, estamos llegando tarde."),
    ("sich waschen", "lavarse", "to wash (oneself)", "verbo", "Wasch dir die Hände vor dem Essen.", "Lavate las manos antes de comer."),
    ("frühstücken", "desayunar", "to have breakfast", "verbo", "Wir frühstücken zusammen um acht.", "Desayunamos juntos a las ocho."),
    ("einkaufen", "hacer las compras", "to go shopping", "verbo", "Ich muss noch einkaufen gehen.", "Todavía tengo que ir a hacer las compras."),
    ("aufräumen", "ordenar", "to tidy up", "verbo", "Am Wochenende räume ich die Wohnung auf.", "El fin de semana ordeno el departamento."),
    ("fernsehen", "mirar televisión", "to watch TV", "verbo", "Abends sehe ich gern fern.", "A la noche me gusta mirar tele."),
    ("anrufen", "llamar (por teléfono)", "to call", "verbo", "Ruf mich später an, bitte.", "Llamame más tarde, por favor."),
    ("abholen", "ir a buscar / recoger", "to pick up", "verbo", "Kannst du mich vom Bahnhof abholen?", "¿Me podés ir a buscar a la estación?"),
    ("mitkommen", "acompañar / venir con", "to come along", "verbo", "Kommst du heute Abend mit?", "¿Venís esta noche con nosotros?"),
    ("ausgehen", "salir (de noche/social)", "to go out", "verbo", "Wir gehen am Freitag aus.", "El viernes salimos."),
    ("sich ausruhen", "descansar", "to rest", "verbo", "Ich muss mich ein bisschen ausruhen.", "Tengo que descansar un poco."),
    ("sich beeilen", "apurarse", "to hurry", "verbo", "Beeil dich, wir kommen zu spät!", "¡Apurate, vamos a llegar tarde!"),
    ("die Gewohnheit", "la costumbre / hábito", "the habit", "die", "Frühes Aufstehen ist eine gute Gewohnheit.", "Levantarse temprano es una buena costumbre."),
    ("der Alltag", "la vida cotidiana", "everyday life", "der", "Mein Alltag ist ziemlich stressig.", "Mi día a día es bastante estresante."),
    ("normalerweise", "normalmente", "normally", "adverbio", "Normalerweise arbeite ich bis fünf Uhr.", "Normalmente trabajo hasta las cinco."),
    ("selten", "rara vez", "rarely", "adverbio", "Ich koche selten am Wochenende.", "Cocino rara vez el fin de semana."),
    ("manchmal", "a veces", "sometimes", "adverbio", "Manchmal gehe ich zu Fuß zur Arbeit.", "A veces voy caminando al trabajo."),
    ("meistens", "la mayoría de las veces", "mostly", "adverbio", "Meistens esse ich zu Hause.", "La mayoría de las veces como en casa."),
    ("gewöhnlich", "habitualmente", "usually", "adverbio", "Gewöhnlich stehe ich früh auf.", "Habitualmente me levanto temprano."),
]

# ---------------------------------------------------------------------------
planes = cat("planes y futuro")
planes += [
    ("vorhaben", "tener planeado", "to plan / intend", "verbo", "Was hast du dieses Wochenende vor?", "¿Qué tenés planeado para este fin de semana?"),
    ("planen", "planear", "to plan", "verbo", "Wir planen eine Reise nach Italien.", "Estamos planeando un viaje a Italia."),
    ("vorschlagen", "proponer", "to suggest", "verbo", "Ich schlage vor, dass wir früher losgehen.", "Propongo que salgamos más temprano."),
    ("die Absicht", "la intención", "the intention", "die", "Ich habe nicht die Absicht, umzuziehen.", "No tengo la intención de mudarme."),
    ("das Ziel", "el objetivo / meta", "the goal", "das", "Mein Ziel ist es, fließend Deutsch zu sprechen.", "Mi objetivo es hablar alemán con fluidez."),
    ("die Zukunft", "el futuro", "the future", "die", "Wie siehst du deine Zukunft?", "¿Cómo ves tu futuro?"),
    ("demnächst", "próximamente", "soon / shortly", "adverbio", "Wir ziehen demnächst um.", "Próximamente nos mudamos."),
    ("bald", "pronto", "soon", "adverbio", "Ich fahre bald in den Urlaub.", "Pronto me voy de vacaciones."),
    ("vielleicht werde ich...", "tal vez voy a...", "maybe I will...", "frase", "Vielleicht werde ich nächstes Jahr umziehen.", "Tal vez el año que viene me mude."),
    ("Ich habe vor, zu...", "tengo pensado...", "I'm planning to...", "frase", "Ich habe vor, einen Deutschkurs zu machen.", "Tengo pensado hacer un curso de alemán."),
    ("sich entscheiden", "decidirse", "to decide", "verbo", "Ich muss mich noch entscheiden.", "Todavía tengo que decidirme."),
    ("überlegen", "pensar / considerar", "to consider", "verbo", "Ich überlege, ob ich das mache.", "Estoy pensando si hago eso."),
]

# ---------------------------------------------------------------------------
pasado = cat("experiencias pasadas")
pasado += [
    ("gewesen", "sido / estado (Partizip de sein)", "been", "frase", "Ich bin noch nie in Berlin gewesen.", "Nunca estuve en Berlín."),
    ("gemacht", "hecho (Partizip de machen)", "done/made", "frase", "Was hast du gestern gemacht?", "¿Qué hiciste ayer?"),
    ("gegangen", "ido (Partizip de gehen)", "gone", "frase", "Wir sind früh ins Bett gegangen.", "Nos fuimos temprano a la cama."),
    ("gesehen", "visto (Partizip de sehen)", "seen", "frase", "Hast du diesen Film schon gesehen?", "¿Ya viste esta película?"),
    ("früher", "antes / en el pasado", "before / in the past", "adverbio", "Früher habe ich in Spanien gelebt.", "Antes vivía en España."),
    ("letztes Jahr", "el año pasado", "last year", "frase", "Letztes Jahr bin ich nach Deutschland gezogen.", "El año pasado me mudé a Alemania."),
    ("letzte Woche", "la semana pasada", "last week", "frase", "Letzte Woche hatte ich viel zu tun.", "La semana pasada tuve mucho para hacer."),
    ("schon einmal", "alguna vez / ya una vez", "already once / ever", "frase", "Warst du schon einmal in München?", "¿Estuviste alguna vez en Múnich?"),
    ("noch nie", "nunca (todavía)", "never (yet)", "frase", "Ich war noch nie so glücklich.", "Nunca estuve tan feliz."),
    ("die Erinnerung", "el recuerdo", "the memory", "die", "Das ist eine schöne Erinnerung.", "Ese es un lindo recuerdo."),
    ("sich erinnern", "acordarse", "to remember", "verbo", "Ich erinnere mich nicht an seinen Namen.", "No me acuerdo de su nombre."),
    ("passieren", "pasar / suceder", "to happen", "verbo", "Was ist passiert?", "¿Qué pasó?"),
    ("erleben", "vivir / experimentar (una experiencia)", "to experience", "verbo", "Ich habe viel Neues erlebt.", "Viví muchas cosas nuevas."),
    ("die Erfahrung machen", "tener una experiencia", "to have an experience", "frase", "Ich habe gute Erfahrungen gemacht.", "Tuve buenas experiencias."),
]

# ---------------------------------------------------------------------------
opiniones = cat("opiniones y comparaciones")
opiniones += [
    ("meiner Meinung nach", "en mi opinión", "in my opinion", "frase", "Meiner Meinung nach ist Deutsch nicht so schwer.", "En mi opinión, el alemán no es tan difícil."),
    ("ich finde, dass...", "me parece que...", "I think that...", "frase", "Ich finde, dass das eine gute Idee ist.", "Me parece que es una buena idea."),
    ("ich denke, dass...", "pienso que...", "I think that...", "frase", "Ich denke, dass wir früh losgehen sollten.", "Pienso que deberíamos salir temprano."),
    ("Ich bin der Meinung, dass...", "soy de la opinión de que...", "I am of the opinion that...", "frase", "Ich bin der Meinung, dass wir mehr üben sollten.", "Soy de la opinión de que deberíamos practicar más."),
    ("einverstanden sein", "estar de acuerdo", "to agree", "verbo", "Ich bin damit einverstanden.", "Estoy de acuerdo con eso."),
    ("zustimmen", "coincidir / dar la razón", "to agree with", "verbo", "Ich stimme dir zu.", "Coincido con vos."),
    ("besser als", "mejor que", "better than", "frase", "Das ist besser als nichts.", "Eso es mejor que nada."),
    ("schlechter als", "peor que", "worse than", "frase", "Die Situation ist schlechter als letztes Jahr.", "La situación está peor que el año pasado."),
    ("genauso wie", "igual que / tal como", "just like", "frase", "Sie spricht genauso wie ihre Mutter.", "Ella habla igual que su madre."),
    ("lieber", "preferir / preferentemente", "rather / prefer", "adverbio", "Ich trinke lieber Tee als Kaffee.", "Prefiero tomar té antes que café."),
    ("am liebsten", "lo que más me gusta", "most preferred / favorite", "frase", "Am liebsten esse ich italienisch.", "Lo que más me gusta comer es comida italiana."),
    ("bevorzugen", "preferir (formal)", "to prefer", "verbo", "Ich bevorzuge ruhige Restaurants.", "Prefiero los restaurantes tranquilos."),
    ("wichtig", "importante", "important", "adjetivo", "Das ist mir sehr wichtig.", "Eso es muy importante para mí."),
    ("unwichtig", "poco importante", "unimportant", "adjetivo", "Das Detail ist unwichtig.", "Ese detalle es poco importante."),
]

# ---------------------------------------------------------------------------
vivienda = cat("vivienda y trámites")
vivienda += [
    ("die Anmeldung", "el empadronamiento (registro de domicilio)", "residence registration", "die", "Die Anmeldung muss ich innerhalb von zwei Wochen machen.", "El empadronamiento lo tengo que hacer dentro de dos semanas."),
    ("das Bürgeramt", "la oficina de atención ciudadana", "citizens' registration office", "das", "Ich habe einen Termin beim Bürgeramt.", "Tengo un turno en la oficina de atención ciudadana."),
    ("der Aufenthaltstitel", "el permiso de residencia", "residence permit", "der", "Mein Aufenthaltstitel läuft nächstes Jahr ab.", "Mi permiso de residencia vence el año que viene."),
    ("das Finanzamt", "la oficina de impuestos", "the tax office", "das", "Das Finanzamt hat mir einen Brief geschickt.", "La oficina de impuestos me mandó una carta."),
    ("die Steuer", "el impuesto", "the tax", "die", "Ich muss meine Steuererklärung machen.", "Tengo que hacer mi declaración de impuestos."),
    ("der Mietvertrag", "el contrato de alquiler", "the rental contract", "der", "Ich habe den Mietvertrag unterschrieben.", "Firmé el contrato de alquiler."),
    ("kündigen", "rescindir / dar de baja", "to cancel / terminate", "verbo", "Ich möchte meinen Vertrag kündigen.", "Quiero rescindir mi contrato."),
    ("die Kündigung", "la rescisión / baja", "the cancellation", "die", "Die Kündigung muss schriftlich sein.", "La rescisión tiene que ser por escrito."),
    ("die Kaution", "el depósito (de garantía)", "the deposit", "die", "Die Kaution sind zwei Monatsmieten.", "El depósito son dos meses de alquiler."),
    ("die Nebenkosten", "los gastos adicionales (expensas)", "additional costs", "die", "Die Nebenkosten sind separat.", "Los gastos adicionales van aparte."),
    ("der Vermieter", "el propietario / locador", "the landlord", "der", "Der Vermieter wohnt im selben Haus.", "El propietario vive en el mismo edificio."),
    ("die Versicherung", "el seguro", "the insurance", "die", "Ich brauche eine Haftpflichtversicherung.", "Necesito un seguro de responsabilidad civil."),
    ("das Konto", "la cuenta (bancaria)", "the bank account", "das", "Ich habe ein Konto bei der Sparkasse eröffnet.", "Abrí una cuenta en la Sparkasse."),
    ("die Überweisung", "la transferencia (bancaria)", "the bank transfer", "die", "Ich mache eine Überweisung an dich.", "Te hago una transferencia."),
    ("die Unterschrift", "la firma", "the signature", "die", "Ich brauche noch Ihre Unterschrift.", "Todavía necesito su firma."),
    ("das Dokument", "el documento", "the document", "das", "Bringen Sie bitte alle Dokumente mit.", "Traiga todos los documentos, por favor."),
    ("der Ausweis", "el documento de identidad", "the ID card", "der", "Ich habe meinen Ausweis vergessen.", "Me olvidé mi documento."),
    ("der Termin vereinbaren", "sacar / concertar un turno", "to make an appointment", "frase", "Ich möchte einen Termin vereinbaren.", "Quisiera concertar un turno."),
    ("das Formular", "el formulario", "the form", "das", "Füllen Sie bitte dieses Formular aus.", "Complete este formulario, por favor."),
    ("ausfüllen", "completar (un formulario)", "to fill out", "verbo", "Können Sie mir helfen, das Formular auszufüllen?", "¿Me puede ayudar a completar el formulario?"),
]

# ---------------------------------------------------------------------------
salud2 = cat("salud (nivel A2)")
salud2 += [
    ("die Sprechstunde", "el horario de consulta", "office hours (doctor)", "die", "Die Sprechstunde ist von neun bis zwölf.", "El horario de consulta es de nueve a doce."),
    ("die Überweisung (medizinisch)", "la derivación médica", "the referral", "die", "Ich brauche eine Überweisung zum Facharzt.", "Necesito una derivación a un especialista."),
    ("der Facharzt", "el médico especialista", "the specialist doctor", "der", "Der Facharzt hat mich gründlich untersucht.", "El especialista me examinó a fondo."),
    ("die Impfung", "la vacuna", "the vaccination", "die", "Ich brauche noch eine Impfung.", "Todavía necesito una vacuna."),
    ("das Rezept", "la receta médica", "the prescription", "das", "Der Arzt hat mir ein Rezept gegeben.", "El médico me dio una receta."),
    ("die Nebenwirkung", "el efecto secundario", "the side effect", "die", "Diese Tablette hat keine Nebenwirkungen.", "Esta pastilla no tiene efectos secundarios."),
    ("sich erkälten", "resfriarse", "to catch a cold", "verbo", "Ich habe mich erkältet.", "Me resfrié."),
    ("die Behandlung", "el tratamiento", "the treatment", "die", "Die Behandlung dauert zwei Wochen.", "El tratamiento dura dos semanas."),
    ("sich verletzen", "lastimarse", "to injure oneself", "verbo", "Ich habe mich beim Sport verletzt.", "Me lastimé haciendo deporte."),
    ("die Gesundheit", "la salud", "health", "die", "Gesundheit geht vor.", "La salud es lo primero."),
    ("gesund werden", "sanarse / mejorarse", "to get better", "frase", "Gute Besserung, ich hoffe, du wirst schnell gesund.", "Que te mejores, espero que sanes rápido."),
    ("die Apotheke Notdienst", "la farmacia de guardia", "the emergency pharmacy", "frase", "Welche Apotheke hat heute Notdienst?", "¿Qué farmacia está de guardia hoy?"),
]

# ---------------------------------------------------------------------------
medios = cat("medios y comunicación")
medios += [
    ("das Handy", "el celular", "the mobile phone", "das", "Mein Handy-Akku ist leer.", "Se me descargó la batería del celular."),
    ("der Anruf", "la llamada", "the phone call", "der", "Ich habe einen Anruf verpasst.", "Me perdí una llamada."),
    ("die Nachricht", "el mensaje", "the message", "die", "Ich schicke dir eine Nachricht.", "Te mando un mensaje."),
    ("die E-Mail", "el correo electrónico", "the email", "die", "Ich schreibe dir eine E-Mail.", "Te escribo un correo."),
    ("das Internet", "internet", "the internet", "das", "Das Internet funktioniert nicht.", "No funciona internet."),
    ("das WLAN", "el wifi", "the wifi", "das", "Wie ist das WLAN-Passwort?", "¿Cuál es la contraseña del wifi?"),
    ("die Webseite", "el sitio web", "the website", "die", "Schau auf der Webseite nach.", "Fijate en el sitio web."),
    ("die Zeitung", "el diario / periódico", "the newspaper", "die", "Ich lese jeden Tag die Zeitung.", "Leo el diario todos los días."),
    ("die Nachrichten", "las noticias", "the news", "die", "Hast du die Nachrichten gesehen?", "¿Viste las noticias?"),
    ("anrufen", "llamar por teléfono", "to call", "verbo", "Ich rufe dich später an.", "Te llamo más tarde."),
    ("herunterladen", "descargar", "to download", "verbo", "Ich lade die App herunter.", "Estoy descargando la aplicación."),
    ("die App", "la aplicación", "the app", "die", "Diese App ist sehr nützlich.", "Esta aplicación es muy útil."),
    ("das Passwort", "la contraseña", "the password", "das", "Ich habe mein Passwort vergessen.", "Me olvidé mi contraseña."),
    ("aufladen", "cargar (batería/saldo)", "to charge / top up", "verbo", "Ich muss mein Handy aufladen.", "Tengo que cargar mi celular."),
]

# ---------------------------------------------------------------------------
viajes = cat("viajes")
viajes += [
    ("die Reise", "el viaje", "the trip", "die", "Die Reise nach Berlin war toll.", "El viaje a Berlín estuvo genial."),
    ("der Urlaub", "las vacaciones", "the vacation", "der", "Wir fahren im Sommer in den Urlaub.", "En verano nos vamos de vacaciones."),
    ("das Gepäck", "el equipaje", "the luggage", "das", "Mein Gepäck ist noch nicht angekommen.", "Mi equipaje todavía no llegó."),
    ("der Koffer", "la valija", "the suitcase", "der", "Ich packe meinen Koffer.", "Estoy armando mi valija."),
    ("der Flug", "el vuelo", "the flight", "der", "Unser Flug hat Verspätung.", "Nuestro vuelo está demorado."),
    ("die Buchung", "la reserva", "the booking", "die", "Ich habe die Buchung bestätigt.", "Confirmé la reserva."),
    ("buchen", "reservar", "to book", "verbo", "Ich möchte ein Hotel buchen.", "Quiero reservar un hotel."),
    ("die Unterkunft", "el alojamiento", "the accommodation", "die", "Wir suchen noch eine Unterkunft.", "Todavía estamos buscando alojamiento."),
    ("die Sehenswürdigkeit", "el lugar turístico / atracción", "the sight / landmark", "die", "Welche Sehenswürdigkeiten gibt es hier?", "¿Qué lugares turísticos hay acá?"),
    ("die Grenze", "la frontera", "the border", "die", "Wir haben die Grenze überquert.", "Cruzamos la frontera."),
    ("der Reisepass", "el pasaporte", "the passport", "der", "Vergiss deinen Reisepass nicht.", "No te olvides tu pasaporte."),
    ("die Verspätung", "la demora / atraso", "the delay", "die", "Der Zug hat zwanzig Minuten Verspätung.", "El tren tiene veinte minutos de demora."),
    ("umsteigen", "hacer trasbordo / trasbordar", "to change (trains/buses)", "verbo", "Du musst in Frankfurt umsteigen.", "Tenés que hacer trasbordo en Fráncfort."),
    ("die Ankunft", "la llegada", "the arrival", "die", "Die Ankunft ist um zehn Uhr.", "La llegada es a las diez."),
    ("die Abfahrt", "la salida (de un transporte)", "the departure", "die", "Die Abfahrt verspätet sich.", "La salida se está demorando."),
]

# ---------------------------------------------------------------------------
social = cat("vida social")
social += [
    ("einladen", "invitar", "to invite", "verbo", "Ich lade dich zu meiner Party ein.", "Te invito a mi fiesta."),
    ("die Einladung", "la invitación", "the invitation", "die", "Danke für die Einladung!", "¡Gracias por la invitación!"),
    ("die Verabredung", "la cita / quedada", "the date / meetup", "die", "Ich habe heute eine Verabredung.", "Hoy tengo una cita."),
    ("sich treffen", "encontrarse (con alguien)", "to meet up", "verbo", "Wir treffen uns um sieben.", "Nos encontramos a las siete."),
    ("die Feier", "la celebración / fiesta", "the celebration", "die", "Die Feier war sehr schön.", "La celebración estuvo muy linda."),
    ("feiern", "festejar", "to celebrate", "verbo", "Wir feiern seinen Geburtstag.", "Festejamos su cumpleaños."),
    ("das Fest", "la fiesta / festividad", "the festival / party", "das", "Das Fest findet im Park statt.", "La fiesta es en el parque."),
    ("der Gast", "el invitado", "the guest", "der", "Wir haben heute Abend Gäste.", "Esta noche tenemos invitados."),
    ("kennenlernen", "conocer (a alguien por primera vez)", "to get to know / meet", "verbo", "Ich möchte dich gern kennenlernen.", "Me gustaría conocerte."),
    ("die Verabredung absagen", "cancelar una cita", "to cancel a plan", "frase", "Ich muss unsere Verabredung leider absagen.", "Lamentablemente tengo que cancelar nuestra cita."),
    ("Lust haben", "tener ganas", "to feel like (doing something)", "frase", "Hast du Lust, ins Kino zu gehen?", "¿Tenés ganas de ir al cine?"),
    ("sich verabschieden", "despedirse", "to say goodbye", "verbo", "Wir haben uns am Bahnhof verabschiedet.", "Nos despedimos en la estación."),
]

# ---------------------------------------------------------------------------
conectores = cat("conectores y conjunciones")
conectores += [
    ("weil", "porque", "because", "partícula", "Ich lerne Deutsch, weil ich hier lebe.", "Aprendo alemán porque vivo acá."),
    ("deshalb", "por eso", "that's why", "partícula", "Es regnet, deshalb bleibe ich zu Hause.", "Está lloviendo, por eso me quedo en casa."),
    ("deswegen", "por esa razón", "for that reason", "partícula", "Ich war krank, deswegen konnte ich nicht kommen.", "Estuve enfermo, por esa razón no pude ir."),
    ("obwohl", "aunque", "although", "partícula", "Ich gehe arbeiten, obwohl ich müde bin.", "Voy a trabajar aunque esté cansado."),
    ("trotzdem", "sin embargo / a pesar de eso", "nevertheless", "partícula", "Es war schwer, trotzdem habe ich es geschafft.", "Fue difícil, sin embargo lo logré."),
    ("außerdem", "además", "besides / moreover", "partícula", "Das Zimmer ist groß, außerdem ist es hell.", "La habitación es grande, además es luminosa."),
    ("während", "mientras", "while", "partícula", "Ich höre Musik, während ich koche.", "Escucho música mientras cocino."),
    ("bevor", "antes de que", "before", "partícula", "Ruf mich an, bevor du kommst.", "Llamame antes de venir."),
    ("nachdem", "después de que", "after", "partícula", "Nachdem ich gegessen habe, gehe ich spazieren.", "Después de comer, salgo a caminar."),
    ("wenn", "cuando / si", "when / if", "partícula", "Wenn ich Zeit habe, rufe ich dich an.", "Cuando tenga tiempo, te llamo."),
    ("sodass", "de modo que", "so that", "partícula", "Er sprach laut, sodass alle ihn hörten.", "Habló fuerte, de modo que todos lo escucharon."),
    ("außer", "excepto / salvo", "except", "partícula", "Alle waren da, außer meine Schwester.", "Todos estaban, excepto mi hermana."),
]

# ---------------------------------------------------------------------------
descripciones = cat("descripciones de personas")
descripciones += [
    ("freundlich", "amable", "friendly", "adjetivo", "Die Nachbarn sind sehr freundlich.", "Los vecinos son muy amables."),
    ("unfreundlich", "poco amable", "unfriendly", "adjetivo", "Der Verkäufer war unfreundlich.", "El vendedor fue poco amable."),
    ("geduldig", "paciente", "patient", "adjetivo", "Meine Lehrerin ist sehr geduldig.", "Mi profesora es muy paciente."),
    ("ungeduldig", "impaciente", "impatient", "adjetivo", "Er wird schnell ungeduldig.", "Él se pone impaciente rápido."),
    ("fleißig", "trabajador / aplicado", "hardworking", "adjetivo", "Sie ist eine fleißige Studentin.", "Ella es una estudiante aplicada."),
    ("faul", "haragán / vago", "lazy", "adjetivo", "Sei nicht so faul!", "¡No seas tan vago!"),
    ("ehrlich", "honesto", "honest", "adjetivo", "Er ist immer ehrlich zu mir.", "Él siempre es honesto conmigo."),
    ("lustig", "gracioso / divertido", "funny", "adjetivo", "Mein Bruder ist sehr lustig.", "Mi hermano es muy gracioso."),
    ("schüchtern", "tímido", "shy", "adjetivo", "Als Kind war ich sehr schüchtern.", "De chico era muy tímido."),
    ("selbstbewusst", "seguro de sí mismo", "self-confident", "adjetivo", "Sie wirkt sehr selbstbewusst.", "Ella parece muy segura de sí misma."),
    ("nett", "simpático / amable", "nice", "adjetivo", "Deine Kollegen sind sehr nett.", "Tus colegas son muy simpáticos."),
    ("höflich", "cortés / educado", "polite", "adjetivo", "Sei höflich zu den Kunden.", "Sé cortés con los clientes."),
    ("neugierig", "curioso", "curious", "adjetivo", "Kinder sind oft sehr neugierig.", "Los chicos suelen ser muy curiosos."),
    ("zuverlässig", "confiable", "reliable", "adjetivo", "Er ist ein zuverlässiger Kollege.", "Es un colega confiable."),
]

# ---------------------------------------------------------------------------
comparaciones = cat("comparativos y superlativos")
comparaciones += [
    ("größer", "más grande", "bigger", "adjetivo", "Meine neue Wohnung ist größer.", "Mi departamento nuevo es más grande."),
    ("kleiner", "más chico", "smaller", "adjetivo", "Dieses Zimmer ist kleiner als das andere.", "Este cuarto es más chico que el otro."),
    ("am größten", "el/la más grande", "the biggest", "adjetivo", "Das ist der größte Park der Stadt.", "Ese es el parque más grande de la ciudad."),
    ("besser", "mejor", "better", "adjetivo", "Diese Lösung ist besser.", "Esta solución es mejor."),
    ("am besten", "lo mejor / el mejor", "the best", "adjetivo", "Das ist am besten für uns.", "Eso es lo mejor para nosotros."),
    ("schlechter", "peor", "worse", "adjetivo", "Das Wetter wird schlechter.", "El clima está empeorando."),
    ("mehr", "más (cantidad)", "more", "adverbio", "Ich brauche mehr Zeit.", "Necesito más tiempo."),
    ("weniger", "menos", "less", "adverbio", "Ich esse jetzt weniger Fleisch.", "Ahora como menos carne."),
    ("so...wie", "tan...como", "as...as", "frase", "Er ist so groß wie sein Vater.", "Él es tan alto como su padre."),
    ("nicht so...wie", "no tan...como", "not as...as", "frase", "Das ist nicht so schwer wie ich dachte.", "No es tan difícil como pensaba."),
    ("je mehr, desto besser", "cuanto más, mejor", "the more, the better", "frase", "Je mehr du übst, desto besser wirst du.", "Cuanto más practiques, mejor te vas a poner."),
    ("gleich", "igual", "the same / equal", "adjetivo", "Beide Wohnungen sind gleich groß.", "Los dos departamentos son igual de grandes."),
    ("ähnlich", "parecido / similar", "similar", "adjetivo", "Die Häuser sehen alle ähnlich aus.", "Las casas se ven todas parecidas."),
    ("unterschiedlich", "diferente / distinto", "different", "adjetivo", "Wir haben unterschiedliche Meinungen.", "Tenemos opiniones distintas."),
    ("der Unterschied", "la diferencia", "the difference", "der", "Was ist der Unterschied zwischen den beiden?", "¿Cuál es la diferencia entre los dos?"),
    ("vergleichen", "comparar", "to compare", "verbo", "Man kann die zwei Städte nicht vergleichen.", "No se pueden comparar las dos ciudades."),
    ("am meisten", "lo que más", "the most", "frase", "Das mag ich am meisten.", "Eso es lo que más me gusta."),
    ("am wenigsten", "lo que menos", "the least", "frase", "Das interessiert mich am wenigsten.", "Eso es lo que menos me interesa."),
]

# ---------------------------------------------------------------------------
trabajo2 = cat("trabajo y oficina (A2)")
trabajo2 += [
    ("die Besprechung", "la reunión", "the meeting", "die", "Wir haben um zehn eine Besprechung.", "Tenemos una reunión a las diez."),
    ("das Projekt", "el proyecto", "the project", "das", "Das Projekt muss bis Freitag fertig sein.", "El proyecto tiene que estar listo para el viernes."),
    ("die Frist", "el plazo", "the deadline", "die", "Die Frist ist morgen.", "El plazo vence mañana."),
    ("der Vertrag", "el contrato", "the contract", "der", "Ich habe den Vertrag unterschrieben.", "Firmé el contrato."),
    ("befördern", "ascender (en el trabajo)", "to promote", "verbo", "Sie wurde letzten Monat befördert.", "A ella la ascendieron el mes pasado."),
    ("das Team", "el equipo (de trabajo)", "the team", "das", "Ich arbeite in einem netten Team.", "Trabajo en un equipo agradable."),
    ("die Verantwortung", "la responsabilidad", "the responsibility", "die", "Er trägt viel Verantwortung.", "Él tiene mucha responsabilidad."),
    ("der Auftrag", "el encargo / pedido (de trabajo)", "the assignment / order", "der", "Wir haben einen neuen Auftrag bekommen.", "Recibimos un encargo nuevo."),
    ("die Abteilung", "el departamento (de una empresa)", "the department", "die", "Sie arbeitet in der IT-Abteilung.", "Ella trabaja en el departamento de IT."),
    ("die Präsentation", "la presentación", "the presentation", "die", "Ich muss eine Präsentation vorbereiten.", "Tengo que preparar una presentación."),
    ("die Aufgabe", "la tarea", "the task", "die", "Diese Aufgabe ist ziemlich schwierig.", "Esta tarea es bastante difícil."),
    ("erledigen", "realizar / resolver (una tarea)", "to take care of / handle", "verbo", "Ich muss noch ein paar Dinge erledigen.", "Todavía tengo que resolver un par de cosas."),
    ("die Überstunden", "las horas extra", "overtime", "die", "Ich mache diese Woche viele Überstunden.", "Esta semana hago muchas horas extra."),
    ("der Urlaubsantrag", "la solicitud de vacaciones", "the vacation request", "der", "Ich habe meinen Urlaubsantrag geschickt.", "Mandé mi solicitud de vacaciones."),
    ("die Gehaltserhöhung", "el aumento de sueldo", "the raise", "die", "Ich bitte um eine Gehaltserhöhung.", "Voy a pedir un aumento de sueldo."),
    ("kündigen (Job)", "renunciar (al trabajo)", "to quit (a job)", "verbo", "Er hat letzten Monat gekündigt.", "Él renunció el mes pasado."),
    ("die Probezeit", "el período de prueba", "the probation period", "die", "Meine Probezeit dauert sechs Monate.", "Mi período de prueba dura seis meses."),
]

# ---------------------------------------------------------------------------
educacion = cat("educación y aprendizaje")
educacion += [
    ("die Prüfung", "el examen", "the exam", "die", "Ich habe nächste Woche eine Prüfung.", "La semana que viene tengo un examen."),
    ("die Note", "la calificación / nota", "the grade", "die", "Ich habe eine gute Note bekommen.", "Saqué una buena nota."),
    ("bestehen", "aprobar (un examen)", "to pass (an exam)", "verbo", "Ich habe die Prüfung bestanden!", "¡Aprobé el examen!"),
    ("durchfallen", "reprobar / desaprobar", "to fail (an exam)", "verbo", "Zum Glück bin ich nicht durchgefallen.", "Por suerte no reprobé."),
    ("der Kurs", "el curso", "the course", "der", "Ich mache einen Deutschkurs.", "Estoy haciendo un curso de alemán."),
    ("der Unterricht", "la clase / enseñanza", "the lesson / class", "der", "Der Unterricht beginnt um neun.", "La clase empieza a las nueve."),
    ("üben", "practicar", "to practice", "verbo", "Ich übe jeden Tag ein bisschen.", "Practico un poco todos los días."),
    ("wiederholen", "repasar / repetir", "to review / repeat", "verbo", "Wir sollten das Kapitel wiederholen.", "Deberíamos repasar el capítulo."),
    ("das Zeugnis", "el certificado / boletín", "the certificate / report card", "das", "Ich habe mein Zeugnis bekommen.", "Recibí mi certificado."),
    ("die Hausaufgabe", "la tarea (escolar)", "the homework", "die", "Hast du deine Hausaufgaben gemacht?", "¿Hiciste tus tareas?"),
    ("der Fortschritt", "el progreso / avance", "the progress", "der", "Du machst gute Fortschritte.", "Estás haciendo buenos progresos."),
    ("sich verbessern", "mejorar (uno mismo)", "to improve", "verbo", "Mein Deutsch verbessert sich langsam.", "Mi alemán está mejorando de a poco."),
    ("das Ziel erreichen", "alcanzar un objetivo", "to reach a goal", "frase", "Ich will mein Ziel erreichen.", "Quiero alcanzar mi objetivo."),
    ("die Fähigkeit", "la habilidad / capacidad", "the ability", "die", "Er hat gute sprachliche Fähigkeiten.", "Él tiene buenas habilidades lingüísticas."),
    ("die Erklärung", "la explicación", "the explanation", "die", "Danke für die Erklärung.", "Gracias por la explicación."),
    ("erklären", "explicar", "to explain", "verbo", "Kannst du mir das noch einmal erklären?", "¿Me lo podés explicar de nuevo?"),
]

# ---------------------------------------------------------------------------
emociones = cat("estado de ánimo y emociones")
emociones += [
    ("glücklich", "feliz", "happy", "adjetivo", "Ich bin heute sehr glücklich.", "Hoy estoy muy feliz."),
    ("traurig", "triste", "sad", "adjetivo", "Warum bist du so traurig?", "¿Por qué estás tan triste?"),
    ("wütend", "enojado / furioso", "angry", "adjetivo", "Er war sehr wütend auf mich.", "Él estaba muy enojado conmigo."),
    ("nervös", "nervioso", "nervous", "adjetivo", "Ich bin nervös vor der Prüfung.", "Estoy nervioso antes del examen."),
    ("gestresst", "estresado", "stressed", "adjetivo", "Ich fühle mich gestresst.", "Me siento estresado."),
    ("entspannt", "relajado", "relaxed", "adjetivo", "Nach dem Urlaub bin ich entspannt.", "Después de las vacaciones estoy relajado."),
    ("überrascht", "sorprendido", "surprised", "adjetivo", "Ich war total überrascht.", "Quedé totalmente sorprendido."),
    ("enttäuscht", "decepcionado", "disappointed", "adjetivo", "Ich bin von ihm enttäuscht.", "Estoy decepcionado de él."),
    ("stolz", "orgulloso", "proud", "adjetivo", "Ich bin stolz auf dich.", "Estoy orgulloso de vos."),
    ("verliebt", "enamorado", "in love", "adjetivo", "Sie ist total verliebt.", "Ella está totalmente enamorada."),
    ("eifersüchtig", "celoso", "jealous", "adjetivo", "Sei nicht eifersüchtig.", "No seas celoso."),
    ("gelangweilt", "aburrido", "bored", "adjetivo", "Die Kinder sind gelangweilt.", "Los chicos están aburridos."),
    ("aufgeregt", "emocionado / excitado", "excited", "adjetivo", "Ich bin aufgeregt wegen der Reise.", "Estoy emocionado por el viaje."),
    ("zufrieden", "conforme / satisfecho", "satisfied", "adjetivo", "Ich bin mit meiner Arbeit zufrieden.", "Estoy conforme con mi trabajo."),
    ("sich freuen", "alegrarse", "to be happy / look forward to", "verbo", "Ich freue mich auf das Wochenende.", "Estoy contento por el fin de semana que se viene."),
    ("sich ärgern", "enojarse / molestarse", "to get annoyed", "verbo", "Ärgere dich nicht darüber.", "No te molestes por eso."),
    ("sich Sorgen machen", "preocuparse", "to worry", "frase", "Mach dir keine Sorgen.", "No te preocupes."),
]

# ---------------------------------------------------------------------------
ambiente = cat("naturaleza y medio ambiente")
ambiente += [
    ("die Umwelt", "el medio ambiente", "the environment", "die", "Wir müssen die Umwelt schützen.", "Tenemos que proteger el medio ambiente."),
    ("der Müll", "la basura", "the trash", "der", "Der Müll wird dienstags abgeholt.", "La basura se recoge los martes."),
    ("recyceln", "reciclar", "to recycle", "verbo", "In Deutschland recycelt man viel.", "En Alemania se recicla mucho."),
    ("die Natur", "la naturaleza", "nature", "die", "Ich verbringe gern Zeit in der Natur.", "Me gusta pasar tiempo en la naturaleza."),
    ("der Wald", "el bosque", "the forest", "der", "Wir machen einen Spaziergang im Wald.", "Damos un paseo por el bosque."),
    ("das Tier", "el animal", "the animal", "das", "Ich mag Tiere sehr.", "Me gustan mucho los animales."),
    ("umweltfreundlich", "ecológico / amigable con el ambiente", "eco-friendly", "adjetivo", "Dieses Produkt ist umweltfreundlich.", "Este producto es ecológico."),
    ("die Energie", "la energía", "the energy", "die", "Wir sparen Energie zu Hause.", "Ahorramos energía en casa."),
    ("sparen", "ahorrar", "to save", "verbo", "Ich spare Wasser und Strom.", "Ahorro agua y electricidad."),
    ("der Klimawandel", "el cambio climático", "climate change", "der", "Der Klimawandel betrifft uns alle.", "El cambio climático nos afecta a todos."),
    ("die Pflanze", "la planta", "the plant", "die", "Ich gieße meine Pflanzen jeden Tag.", "Riego mis plantas todos los días."),
    ("die Mülltrennung", "la separación de residuos", "waste separation", "die", "Die Mülltrennung ist in Deutschland Pflicht.", "La separación de residuos es obligatoria en Alemania."),
    ("der Gelbe Sack", "la bolsa amarilla (envases reciclables)", "the yellow recycling bag", "der", "Plastik kommt in den Gelben Sack.", "El plástico va en la bolsa amarilla."),
]

# ---------------------------------------------------------------------------
tecnologia = cat("tecnología y dispositivos")
tecnologia += [
    ("der Computer", "la computadora", "the computer", "der", "Mein Computer ist sehr langsam.", "Mi computadora anda muy lenta."),
    ("der Laptop", "la notebook", "the laptop", "der", "Ich arbeite mit meinem Laptop.", "Trabajo con mi notebook."),
    ("drucken", "imprimir", "to print", "verbo", "Kannst du das für mich drucken?", "¿Me lo podés imprimir?"),
    ("speichern", "guardar (un archivo)", "to save (a file)", "verbo", "Vergiss nicht zu speichern!", "¡No te olvides de guardar!"),
    ("installieren", "instalar", "to install", "verbo", "Ich installiere gerade ein Programm.", "Estoy instalando un programa."),
    ("das Programm", "el programa", "the program", "das", "Dieses Programm ist kostenlos.", "Este programa es gratis."),
    ("die Datei", "el archivo", "the file", "die", "Ich kann die Datei nicht öffnen.", "No puedo abrir el archivo."),
    ("der Bildschirm", "la pantalla", "the screen", "der", "Der Bildschirm ist kaputt.", "La pantalla está rota."),
    ("klicken", "cliquear", "to click", "verbo", "Klicken Sie hier, um fortzufahren.", "Hagan clic acá para continuar."),
    ("hochladen", "subir (un archivo)", "to upload", "verbo", "Ich lade die Fotos hoch.", "Estoy subiendo las fotos."),
    ("das Update", "la actualización", "the update", "das", "Es gibt ein neues Update.", "Hay una actualización nueva."),
    ("funktionieren", "funcionar", "to work / function", "verbo", "Die App funktioniert nicht richtig.", "La aplicación no funciona bien."),
]

# ---------------------------------------------------------------------------
cocina2 = cat("comida y cocina (A2)")
cocina2 += [
    ("schneiden", "cortar", "to cut", "verbo", "Schneide die Zwiebel klein.", "Cortá la cebolla chiquita."),
    ("braten", "freír / asar", "to fry / roast", "verbo", "Ich brate das Fleisch in der Pfanne.", "Frío la carne en la sartén."),
    ("backen", "hornear", "to bake", "verbo", "Wir backen heute einen Kuchen.", "Hoy horneamos una torta."),
    ("die Zutat", "el ingrediente", "the ingredient", "die", "Welche Zutaten brauchen wir?", "¿Qué ingredientes necesitamos?"),
    ("das Rezept (Kochen)", "la receta (de cocina)", "the recipe", "das", "Hast du ein gutes Rezept für Nudeln?", "¿Tenés una buena receta de fideos?"),
    ("würzen", "condimentar", "to season", "verbo", "Ich würze die Suppe mit Salz und Pfeffer.", "Condimento la sopa con sal y pimienta."),
    ("probieren", "probar (comida)", "to try / taste", "verbo", "Probier mal, das ist sehr lecker!", "¡Probá, está muy rico!"),
    ("servieren", "servir", "to serve", "verbo", "Wir servieren das Essen um acht.", "Servimos la comida a las ocho."),
    ("die Portion", "la porción", "the portion", "die", "Das ist eine große Portion.", "Es una porción grande."),
    ("vegetarisch", "vegetariano", "vegetarian", "adjetivo", "Ich esse vegetarisch.", "Como vegetariano."),
    ("die Allergie", "la alergia", "the allergy", "die", "Ich habe eine Allergie gegen Nüsse.", "Tengo alergia a los frutos secos."),
    ("scharf", "picante", "spicy", "adjetivo", "Das Essen ist mir zu scharf.", "La comida me resulta muy picante."),
]

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    vocab = build_vocab(CATEGORIES_A2, nivel="A2", id_prefix="a2-")
    out_path = "/root/german-app/data/vocab-a2.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Generadas {len(vocab)} entradas en {out_path}")
    by_cat = {}
    for e in vocab:
        by_cat[e["categoria"]] = by_cat.get(e["categoria"], 0) + 1
    for c, n in by_cat.items():
        print(f"  - {c}: {n}")
